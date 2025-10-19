"""
Archimedes POC2: AML Transaction Monitoring with ML

This module implements machine learning models for detecting
suspicious financial transactions and money laundering patterns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from imblearn.over_sampling import SMOTE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering for AML detection"""

    def __init__(self, lookback_window_days=30):
        self.lookback_window = lookback_window_days
        self.scaler = StandardScaler()

    def create_features(self, transaction_df: pd.DataFrame, account_df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features for ML models

        Args:
            transaction_df: Transaction data
            account_df: Account metadata

        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering features...")

        features = pd.DataFrame(index=transaction_df.index)

        # Basic transaction features
        features['amount'] = transaction_df['amount']
        features['log_amount'] = np.log1p(transaction_df['amount'])
        features['is_cross_border'] = transaction_df['is_cross_border'].astype(int)

        # Amount pattern features
        features['is_round_amount'] = (transaction_df['amount'] % 1000 == 0).astype(int)
        features['is_just_below_10k'] = (
            (transaction_df['amount'] >= 9800) &
            (transaction_df['amount'] < 10000)
        ).astype(int)
        features['is_just_below_5k'] = (
            (transaction_df['amount'] >= 4900) &
            (transaction_df['amount'] < 5000)
        ).astype(int)

        # Temporal features
        transaction_df['timestamp'] = pd.to_datetime(transaction_df['timestamp'])
        features['hour'] = transaction_df['timestamp'].dt.hour
        features['day_of_week'] = transaction_df['timestamp'].dt.dayofweek
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        features['is_night'] = ((features['hour'] < 6) | (features['hour'] > 22)).astype(int)

        # Velocity features (requires sorting by timestamp)
        features = self._add_velocity_features(features, transaction_df)

        # Account features
        features = self._add_account_features(features, transaction_df, account_df)

        # Geographic risk features
        features = self._add_geographic_risk(features, transaction_df)

        # Statistical features
        features = self._add_statistical_features(features, transaction_df)

        logger.info(f"Created {len(features.columns)} features")
        return features

    def _add_velocity_features(self, features: pd.DataFrame, transaction_df: pd.DataFrame) -> pd.DataFrame:
        """Add transaction velocity features"""

        # Sort by account and timestamp
        df_sorted = transaction_df.sort_values(['from_account_id', 'timestamp'])

        # Count transactions in various windows
        features['tx_count_1h'] = self._count_recent(df_sorted, 'from_account_id', hours=1)
        features['tx_count_24h'] = self._count_recent(df_sorted, 'from_account_id', hours=24)
        features['tx_count_7d'] = self._count_recent(df_sorted, 'from_account_id', days=7)
        features['tx_count_30d'] = self._count_recent(df_sorted, 'from_account_id', days=30)

        # Amount velocity
        features['amount_sum_24h'] = self._sum_recent(df_sorted, 'from_account_id', 'amount', hours=24)
        features['amount_sum_7d'] = self._sum_recent(df_sorted, 'from_account_id', 'amount', days=7)

        return features

    def _count_recent(self, df: pd.DataFrame, group_col: str, hours=None, days=None) -> pd.Series:
        """Count recent transactions within window"""
        if hours:
            window = timedelta(hours=hours)
        elif days:
            window = timedelta(days=days)
        else:
            raise ValueError("Must specify hours or days")

        # Simplified implementation - in production use rolling window
        return df.groupby(group_col).cumcount() + 1

    def _sum_recent(self, df: pd.DataFrame, group_col: str, value_col: str, hours=None, days=None) -> pd.Series:
        """Sum values in recent window"""
        if hours:
            window = timedelta(hours=hours)
        elif days:
            window = timedelta(days=days)

        # Simplified - in production use proper rolling sum
        return df.groupby(group_col)[value_col].cumsum()

    def _add_account_features(self, features: pd.DataFrame, transaction_df: pd.DataFrame,
                              account_df: pd.DataFrame) -> pd.DataFrame:
        """Add account-level features"""

        # Merge account data
        account_features = transaction_df['from_account_id'].map(
            account_df.set_index('account_id')['risk_rating']
        )

        # Encode risk rating
        risk_encoding = {'low': 0, 'medium': 1, 'high': 2, 'severe': 3}
        features['account_risk'] = account_features.map(risk_encoding).fillna(1)

        # PEP flag
        features['is_pep'] = transaction_df['from_account_id'].map(
            account_df.set_index('account_id')['is_pep']
        ).fillna(False).astype(int)

        # Account age
        account_opening = transaction_df['from_account_id'].map(
            account_df.set_index('account_id')['opening_date']
        )
        features['account_age_days'] = (
            transaction_df['timestamp'] - pd.to_datetime(account_opening)
        ).dt.days.fillna(0)

        return features

    def _add_geographic_risk(self, features: pd.DataFrame, transaction_df: pd.DataFrame) -> pd.DataFrame:
        """Add geographic risk features"""

        # FATF high-risk jurisdictions (simplified list)
        HIGH_RISK_COUNTRIES = [
            'AF', 'BY', 'BI', 'KH', 'CF', 'CD', 'CU', 'ER', 'GN', 'GW',
            'HT', 'IR', 'IQ', 'LB', 'LY', 'ML', 'MM', 'NI', 'KP', 'PK',
            'PA', 'PH', 'RU', 'SO', 'SS', 'SD', 'SY', 'TZ', 'UG', 'VU', 'YE', 'ZW'
        ]

        features['from_high_risk'] = transaction_df['from_country'].isin(HIGH_RISK_COUNTRIES).astype(int)
        features['to_high_risk'] = transaction_df['to_country'].isin(HIGH_RISK_COUNTRIES).astype(int)

        # Tax havens (simplified list)
        TAX_HAVENS = ['BM', 'KY', 'VG', 'LI', 'MC', 'PA', 'CH', 'LU']
        features['to_tax_haven'] = transaction_df['to_country'].isin(TAX_HAVENS).astype(int)

        return features

    def _add_statistical_features(self, features: pd.DataFrame, transaction_df: pd.DataFrame) -> pd.DataFrame:
        """Add statistical features based on account history"""

        # Amount deviation from account average (simplified)
        account_avg = transaction_df.groupby('from_account_id')['amount'].transform('mean')
        account_std = transaction_df.groupby('from_account_id')['amount'].transform('std')

        features['amount_z_score'] = (transaction_df['amount'] - account_avg) / (account_std + 1)
        features['amount_deviation_pct'] = ((transaction_df['amount'] - account_avg) / account_avg * 100).fillna(0)

        return features


class AMLModelEnsemble:
    """Ensemble of ML models for AML detection"""

    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.isolation_forest = None
        self.feature_engineer = FeatureEngineer()
        self.scaler = StandardScaler()

    def train(self, transaction_df: pd.DataFrame, account_df: pd.DataFrame, labels: pd.Series):
        """
        Train all models in the ensemble

        Args:
            transaction_df: Transaction data
            account_df: Account metadata
            labels: Binary labels (0=legitimate, 1=suspicious)
        """
        logger.info("Training AML model ensemble...")

        # Engineer features
        X = self.feature_engineer.create_features(transaction_df, account_df)

        # Handle missing values
        X = X.fillna(0)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42, stratify=labels
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train Random Forest
        logger.info("Training Random Forest...")
        self.rf_model = self._train_random_forest(X_train, y_train, X_test, y_test)

        # Train XGBoost
        logger.info("Training XGBoost...")
        self.xgb_model = self._train_xgboost(X_train, y_train, X_test, y_test)

        # Train Isolation Forest (unsupervised)
        logger.info("Training Isolation Forest...")
        self.isolation_forest = self._train_isolation_forest(X_train_scaled)

        logger.info("Ensemble training complete!")

    def _train_random_forest(self, X_train, y_train, X_test, y_test) -> RandomForestClassifier:
        """Train Random Forest classifier"""

        # Handle class imbalance with SMOTE
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

        # Train model
        rf = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )

        rf.fit(X_train_balanced, y_train_balanced)

        # Evaluate
        y_pred = rf.predict(X_test)
        y_proba = rf.predict_proba(X_test)[:, 1]

        logger.info("Random Forest Results:")
        logger.info(f"\n{classification_report(y_test, y_pred)}")
        logger.info(f"AUC-ROC: {roc_auc_score(y_test, y_proba):.4f}")

        return rf

    def _train_xgboost(self, X_train, y_train, X_test, y_test) -> xgb.XGBClassifier:
        """Train XGBoost classifier"""

        # Calculate scale_pos_weight for imbalanced data
        scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

        model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=10,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            eval_metric='aucpr',
            use_label_encoder=False
        )

        # Train
        eval_set = [(X_train, y_train), (X_test, y_test)]
        model.fit(
            X_train, y_train,
            eval_set=eval_set,
            verbose=False
        )

        # Evaluate
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        logger.info("XGBoost Results:")
        logger.info(f"\n{classification_report(y_test, y_pred)}")
        logger.info(f"AUC-ROC: {roc_auc_score(y_test, y_proba):.4f}")

        return model

    def _train_isolation_forest(self, X_train_scaled) -> IsolationForest:
        """Train Isolation Forest for anomaly detection"""

        iso_forest = IsolationForest(
            n_estimators=200,
            contamination=0.05,  # Assume 5% anomalies
            random_state=42,
            n_jobs=-1
        )

        iso_forest.fit(X_train_scaled)

        logger.info("Isolation Forest trained (unsupervised)")

        return iso_forest

    def predict(self, transaction_df: pd.DataFrame, account_df: pd.DataFrame) -> Dict:
        """
        Predict risk score for transactions

        Args:
            transaction_df: Transaction data
            account_df: Account metadata

        Returns:
            Dictionary with predictions from all models and ensemble score
        """
        # Engineer features
        X = self.feature_engineer.create_features(transaction_df, account_df)
        X = X.fillna(0)
        X_scaled = self.scaler.transform(X)

        # Get predictions from all models
        rf_proba = self.rf_model.predict_proba(X)[:, 1]
        xgb_proba = self.xgb_model.predict_proba(X)[:, 1]

        # Isolation Forest returns anomaly scores (-1 to 1, lower is more anomalous)
        iso_scores = self.isolation_forest.score_samples(X_scaled)
        # Normalize to 0-1 (higher = more anomalous)
        iso_proba = 1 - (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min() + 1e-10)

        # Ensemble: weighted average
        ensemble_score = (
            0.35 * rf_proba +
            0.45 * xgb_proba +
            0.20 * iso_proba
        ) * 100  # Scale to 0-100

        return {
            'ensemble_score': ensemble_score,
            'random_forest_score': rf_proba * 100,
            'xgboost_score': xgb_proba * 100,
            'anomaly_score': iso_proba * 100,
            'risk_level': self._classify_risk(ensemble_score)
        }

    def _classify_risk(self, scores: np.ndarray) -> List[str]:
        """Classify risk level based on score"""
        return ['critical' if s >= 80 else 'high' if s >= 60 else 'medium' if s >= 40 else 'low' for s in scores]

    def get_feature_importance(self, top_n=20) -> pd.DataFrame:
        """Get feature importance from Random Forest"""
        if self.rf_model is None:
            raise ValueError("Model not trained yet")

        feature_names = self.feature_engineer.create_features(
            pd.DataFrame(), pd.DataFrame()
        ).columns

        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': self.rf_model.feature_importances_
        }).sort_values('importance', ascending=False).head(top_n)

        return importance_df


# Example usage
if __name__ == "__main__":
    from synthetic_data_generator import generate_synthetic_data

    # Generate synthetic data
    logger.info("Generating synthetic data...")
    accounts_df, transactions_df, labels = generate_synthetic_data(
        n_accounts=10000,
        n_transactions=100000
    )

    # Train models
    logger.info("Training models...")
    ensemble = AMLModelEnsemble()
    ensemble.train(transactions_df, accounts_df, labels)

    # Get feature importance
    importance = ensemble.get_feature_importance(top_n=15)
    logger.info("Top 15 Most Important Features:")
    logger.info(f"\n{importance}")

    # Make predictions on new data
    logger.info("Making predictions...")
    predictions = ensemble.predict(transactions_df.head(100), accounts_df)

    logger.info(f"Predicted {len(predictions['risk_level'])} transactions")
    logger.info(f"Risk distribution:")
    logger.info(pd.Series(predictions['risk_level']).value_counts())

    print("\nAML Detection POC2 Complete!")
