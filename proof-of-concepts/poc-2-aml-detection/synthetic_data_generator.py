"""
Synthetic Data Generator for AML POC

Generates realistic financial transaction data with
known suspicious patterns for model training and testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)


def generate_synthetic_data(n_accounts=10000, n_transactions=100000, suspicious_ratio=0.05):
    """
    Generate synthetic financial data with realistic patterns

    Args:
        n_accounts: Number of accounts to generate
        n_transactions: Number of transactions
        suspicious_ratio: Proportion of suspicious transactions (0-1)

    Returns:
        Tuple of (accounts_df, transactions_df, labels)
    """
    print(f"Generating {n_accounts} accounts and {n_transactions} transactions...")

    # Generate accounts
    accounts_df = generate_accounts(n_accounts)

    # Calculate number of suspicious transactions
    n_suspicious = int(n_transactions * suspicious_ratio)
    n_legitimate = n_transactions - n_suspicious

    # Generate legitimate transactions
    legitimate_txs = generate_legitimate_transactions(accounts_df, n_legitimate)
    legitimate_labels = pd.Series([0] * n_legitimate)

    # Generate suspicious transactions with various patterns
    suspicious_txs, suspicious_labels = generate_suspicious_transactions(accounts_df, n_suspicious)

    # Combine and shuffle
    all_transactions = pd.concat([legitimate_txs, suspicious_txs], ignore_index=True)
    all_labels = pd.concat([legitimate_labels, suspicious_labels], ignore_index=True)

    # Shuffle
    shuffle_idx = np.random.permutation(len(all_transactions))
    all_transactions = all_transactions.iloc[shuffle_idx].reset_index(drop=True)
    all_labels = all_labels.iloc[shuffle_idx].reset_index(drop=True)

    print(f"Generated {len(all_transactions)} transactions:")
    print(f"  - Legitimate: {(all_labels == 0).sum()}")
    print(f"  - Suspicious: {(all_labels == 1).sum()}")

    return accounts_df, all_transactions, all_labels


def generate_accounts(n_accounts):
    """Generate realistic account data"""

    COUNTRIES = ['USA', 'GBR', 'DEU', 'FRA', 'CHN', 'JPN', 'IND', 'BRA', 'CAN', 'AUS',
                 'ITA', 'ESP', 'KOR', 'MEX', 'RUS', 'TUR', 'SAU', 'ZAF', 'ARG', 'IDN']

    accounts = []
    for i in range(n_accounts):
        # Higher chance of high-risk countries for some accounts
        if np.random.random() < 0.05:
            country = np.random.choice(['AF', 'KP', 'SY', 'IR', 'PK'])
            risk_rating = np.random.choice(['medium', 'high', 'severe'], p=[0.3, 0.5, 0.2])
        else:
            country = np.random.choice(COUNTRIES)
            risk_rating = np.random.choice(['low', 'medium', 'high'], p=[0.7, 0.25, 0.05])

        account = {
            'account_id': f'ACC{i:08d}',
            'customer_name': fake.name(),
            'account_type': np.random.choice(['personal', 'business'], p=[0.8, 0.2]),
            'country': country,
            'risk_rating': risk_rating,
            'is_pep': np.random.random() < 0.02,  # 2% PEPs
            'kyc_status': np.random.choice(['verified', 'pending', 'incomplete'], p=[0.85, 0.10, 0.05]),
            'opening_date': fake.date_between(start_date='-5y', end_date='-30d')
        }
        accounts.append(account)

    return pd.DataFrame(accounts)


def generate_legitimate_transactions(accounts_df, n_transactions):
    """Generate legitimate transaction patterns"""

    transactions = []
    account_ids = accounts_df['account_id'].tolist()
    countries = accounts_df.set_index('account_id')['country'].to_dict()

    for i in range(n_transactions):
        from_account = np.random.choice(account_ids)
        to_account = np.random.choice(account_ids)

        # Legitimate transactions have realistic amounts
        # Log-normal distribution (most transactions are small, few are large)
        amount = np.random.lognormal(mean=7.0, sigma=1.5)  # Mean ~$1100
        amount = round(amount, 2)

        # Legitimate transactions mostly during business hours
        hour_weights = [1 if 9 <= h <= 17 else 0.3 for h in range(24)]
        hour = np.random.choice(range(24), p=np.array(hour_weights) / sum(hour_weights))

        timestamp = datetime.now() - timedelta(
            days=np.random.randint(0, 365),
            hours=hour,
            minutes=np.random.randint(0, 60)
        )

        from_country = countries.get(from_account, 'USA')
        to_country = countries.get(to_account, 'USA')

        transaction = {
            'transaction_id': f'TX{i:010d}',
            'from_account_id': from_account,
            'to_account_id': to_account,
            'amount': amount,
            'currency': 'USD',
            'transaction_type': np.random.choice(['wire', 'ach', 'check', 'card'], p=[0.3, 0.4, 0.2, 0.1]),
            'timestamp': timestamp,
            'from_country': from_country,
            'to_country': to_country,
            'is_cross_border': from_country != to_country,
            'narrative': fake.sentence()
        }
        transactions.append(transaction)

    return pd.DataFrame(transactions)


def generate_suspicious_transactions(accounts_df, n_transactions):
    """Generate suspicious transaction patterns"""

    # Different suspicious patterns
    patterns = {
        'smurfing': 0.30,           # Multiple transactions just below threshold
        'rapid_movement': 0.20,     # Quick in-and-out
        'layering': 0.15,           # Complex chains
        'round_amounts': 0.15,      # Suspiciously round numbers
        'high_risk_geo': 0.10,      # High-risk jurisdictions
        'unusual_timing': 0.10      # Odd hours, weekends
    }

    transactions = []
    labels = []

    account_ids = accounts_df['account_id'].tolist()
    high_risk_accounts = accounts_df[accounts_df['risk_rating'].isin(['high', 'severe'])]['account_id'].tolist()

    pattern_names = list(patterns.keys())
    pattern_probs = list(patterns.values())

    for i in range(n_transactions):
        pattern = np.random.choice(pattern_names, p=pattern_probs)

        if pattern == 'smurfing':
            txs = generate_smurfing_pattern(i, account_ids)
        elif pattern == 'rapid_movement':
            txs = generate_rapid_movement_pattern(i, account_ids)
        elif pattern == 'layering':
            txs = generate_layering_pattern(i, account_ids)
        elif pattern == 'round_amounts':
            txs = generate_round_amount_pattern(i, account_ids)
        elif pattern == 'high_risk_geo':
            txs = generate_high_risk_geo_pattern(i, high_risk_accounts if high_risk_accounts else account_ids)
        else:  # unusual_timing
            txs = generate_unusual_timing_pattern(i, account_ids)

        transactions.extend(txs)
        labels.extend([1] * len(txs))  # All suspicious

    return pd.DataFrame(transactions), pd.Series(labels)


def generate_smurfing_pattern(base_id, account_ids):
    """Generate structuring/smurfing pattern"""
    # Multiple transactions just below $10k threshold
    n_txs = np.random.randint(3, 8)
    txs = []

    from_account = np.random.choice(account_ids)
    to_account = np.random.choice(account_ids)
    base_time = datetime.now() - timedelta(days=np.random.randint(0, 30))

    for j in range(n_txs):
        amount = np.random.uniform(9700, 9950)  # Just below $10k
        timestamp = base_time + timedelta(hours=j * 2)

        tx = {
            'transaction_id': f'SUSP{base_id:08d}_{j}',
            'from_account_id': from_account,
            'to_account_id': to_account,
            'amount': round(amount, 2),
            'currency': 'USD',
            'transaction_type': 'wire',
            'timestamp': timestamp,
            'from_country': 'USA',
            'to_country': 'USA',
            'is_cross_border': False,
            'narrative': fake.sentence()
        }
        txs.append(tx)

    return txs


def generate_rapid_movement_pattern(base_id, account_ids):
    """Generate rapid movement pattern (funds in and quickly out)"""
    from_account = np.random.choice(account_ids)
    intermediate_account = np.random.choice(account_ids)
    to_account = np.random.choice(account_ids)

    amount = np.random.uniform(50000, 500000)
    base_time = datetime.now() - timedelta(days=np.random.randint(0, 30))

    txs = [
        {
            'transaction_id': f'SUSP{base_id:08d}_in',
            'from_account_id': from_account,
            'to_account_id': intermediate_account,
            'amount': round(amount, 2),
            'currency': 'USD',
            'transaction_type': 'wire',
            'timestamp': base_time,
            'from_country': 'USA',
            'to_country': 'USA',
            'is_cross_border': False,
            'narrative': 'Investment proceeds'
        },
        {
            'transaction_id': f'SUSP{base_id:08d}_out',
            'from_account_id': intermediate_account,
            'to_account_id': to_account,
            'amount': round(amount * 0.98, 2),  # Slightly less (fees)
            'currency': 'USD',
            'transaction_type': 'wire',
            'timestamp': base_time + timedelta(hours=1),  # Very quick
            'from_country': 'USA',
            'to_country': 'USA',
            'is_cross_border': False,
            'narrative': 'Business expense'
        }
    ]

    return txs


def generate_layering_pattern(base_id, account_ids):
    """Generate layering pattern (complex transaction chains)"""
    # 4-6 transactions in a chain
    n_txs = np.random.randint(4, 7)
    accounts = np.random.choice(account_ids, size=n_txs+1, replace=False)

    amount = np.random.uniform(100000, 1000000)
    base_time = datetime.now() - timedelta(days=np.random.randint(0, 30))

    txs = []
    for j in range(n_txs):
        tx = {
            'transaction_id': f'SUSP{base_id:08d}_{j}',
            'from_account_id': accounts[j],
            'to_account_id': accounts[j+1],
            'amount': round(amount * (0.95 ** j), 2),  # Amount decreases (fees)
            'currency': 'USD',
            'transaction_type': 'wire',
            'timestamp': base_time + timedelta(hours=j*6),
            'from_country': np.random.choice(['USA', 'GBR', 'CHE']),
            'to_country': np.random.choice(['USA', 'GBR', 'CHE']),
            'is_cross_border': np.random.random() > 0.5,
            'narrative': fake.sentence()
        }
        txs.append(tx)

    return txs


def generate_round_amount_pattern(base_id, account_ids):
    """Generate suspiciously round amount pattern"""
    from_account = np.random.choice(account_ids)
    to_account = np.random.choice(account_ids)

    # Very round numbers
    amount = np.random.choice([50000, 100000, 250000, 500000, 1000000])
    timestamp = datetime.now() - timedelta(days=np.random.randint(0, 30))

    tx = {
        'transaction_id': f'SUSP{base_id:08d}',
        'from_account_id': from_account,
        'to_account_id': to_account,
        'amount': float(amount),
        'currency': 'USD',
        'transaction_type': 'wire',
        'timestamp': timestamp,
        'from_country': 'USA',
        'to_country': 'USA',
        'is_cross_border': False,
        'narrative': 'Payment'
    }

    return [tx]


def generate_high_risk_geo_pattern(base_id, account_ids):
    """Generate high-risk geography pattern"""
    from_account = np.random.choice(account_ids)
    to_account = np.random.choice(account_ids)

    HIGH_RISK = ['AF', 'KP', 'SY', 'IR', 'PK', 'SD']

    amount = np.random.uniform(10000, 200000)
    timestamp = datetime.now() - timedelta(days=np.random.randint(0, 30))

    tx = {
        'transaction_id': f'SUSP{base_id:08d}',
        'from_account_id': from_account,
        'to_account_id': to_account,
        'amount': round(amount, 2),
        'currency': 'USD',
        'transaction_type': 'wire',
        'timestamp': timestamp,
        'from_country': np.random.choice(HIGH_RISK),
        'to_country': np.random.choice(['USA', 'GBR', 'CHE']),
        'is_cross_border': True,
        'narrative': fake.sentence()
    }

    return [tx]


def generate_unusual_timing_pattern(base_id, account_ids):
    """Generate unusual timing pattern (late night, weekends)"""
    from_account = np.random.choice(account_ids)
    to_account = np.random.choice(account_ids)

    amount = np.random.uniform(20000, 500000)

    # Late night (2-5 AM) on weekend
    timestamp = datetime.now() - timedelta(days=np.random.randint(0, 30))
    # Make it a weekend
    while timestamp.weekday() < 5:  # 0-4 = Mon-Fri
        timestamp += timedelta(days=1)
    # Set to late night
    timestamp = timestamp.replace(hour=np.random.randint(2, 5), minute=np.random.randint(0, 60))

    tx = {
        'transaction_id': f'SUSP{base_id:08d}',
        'from_account_id': from_account,
        'to_account_id': to_account,
        'amount': round(amount, 2),
        'currency': 'USD',
        'transaction_type': 'wire',
        'timestamp': timestamp,
        'from_country': 'USA',
        'to_country': 'USA',
        'is_cross_border': False,
        'narrative': fake.sentence()
    }

    return [tx]


if __name__ == "__main__":
    # Test data generation
    accounts_df, transactions_df, labels = generate_synthetic_data(
        n_accounts=1000,
        n_transactions=10000,
        suspicious_ratio=0.05
    )

    print("\nAccount Sample:")
    print(accounts_df.head())

    print("\nTransaction Sample:")
    print(transactions_df.head())

    print("\nLabel Distribution:")
    print(labels.value_counts())

    print("\nSuspicious Transaction Sample:")
    suspicious_txs = transactions_df[labels == 1].head()
    print(suspicious_txs[['transaction_id', 'amount', 'timestamp', 'from_country', 'to_country']])
