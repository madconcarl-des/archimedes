"""
Test GLM-4.6 integration with live API key
"""
import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Set API key
os.environ['GLM_API_KEY'] = 'ce45838fe39d44b48bfd040c22118080.0VZD0hr09tcLQacP'

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from integrations.glm46_integration import ArchimedesGLMIntegration

print("="*70)
print(" GLM-4.6 LIVE API TEST")
print("="*70)

# Test 1: Initialize
print("\n[Test 1] Initializing GLM-4.6 client...")
try:
    glm = ArchimedesGLMIntegration()
    print("  [OK] Client initialized successfully")
    print(f"  API Key: {os.getenv('GLM_API_KEY')[:20]}...")
except Exception as e:
    print(f"  [FAIL] Initialization failed: {e}")
    sys.exit(1)

# Test 2: Natural Language Query Translation
print("\n[Test 2] Natural Language Query Translation...")
query = "What was China's GDP growth from 2020 to 2023?"
indicators = ["GDP_GROWTH", "INFLATION", "UNEMPLOYMENT", "DEBT_GDP"]

try:
    print(f"  Query: '{query}'")
    result = glm.process_natural_language_query(query, indicators)
    print(f"  [OK] Query parsed successfully!")
    print(f"  Parsed Parameters:")
    import json
    print(json.dumps(result, indent=4))
except Exception as e:
    print(f"  [FAIL] Query parsing failed: {e}")
    print(f"  Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

# Test 3: Economic Data Explanation
print("\n[Test 3] Economic Data Explanation...")
sample_data = {
    "indicator": "Inflation Rate",
    "country": "United States",
    "values": [1.2, 4.7, 8.0, 4.1, 3.4],
    "years": [2019, 2020, 2021, 2022, 2023]
}

try:
    print(f"  Data: US Inflation 2019-2023")
    explanation = glm.explain_data(sample_data, "Post-COVID inflation trends")
    print(f"  [OK] Explanation generated!")
    print(f"\n  Analysis:")
    print(f"  {explanation[:300]}...")
except Exception as e:
    print(f"  [FAIL] Explanation failed: {e}")
    print(f"  Error type: {type(e).__name__}")

# Test 4: AML Transaction Analysis
print("\n[Test 4] AML Transaction Analysis...")
transaction = {
    "transaction_id": "TX123456",
    "amount": 9850,
    "from_country": "US",
    "to_country": "PA",
    "timestamp": "2025-10-19T02:30:00Z"
}

risk_scores = {
    "ensemble_score": 85.3,
    "random_forest_score": 82.1,
    "xgboost_score": 88.5,
    "anomaly_score": 76.2
}

try:
    print(f"  Transaction: ${transaction['amount']:,} {transaction['from_country']} → {transaction['to_country']}")
    print(f"  Risk Score: {risk_scores['ensemble_score']}/100")

    analysis = glm.analyze_suspicious_transaction(transaction, risk_scores)
    print(f"  [OK] Analysis complete!")
    print(f"\n  AI Analysis:")
    print(f"  {analysis.get('analysis', '')[:300]}...")
except Exception as e:
    print(f"  [FAIL] AML analysis failed: {e}")
    print(f"  Error type: {type(e).__name__}")

# Test 5: SAR Generation
print("\n[Test 5] SAR Narrative Generation...")
transactions_cluster = [
    {"transaction_id": "TX001", "amount": 9850, "timestamp": "2025-10-01"},
    {"transaction_id": "TX002", "amount": 9900, "timestamp": "2025-10-05"},
    {"transaction_id": "TX003", "amount": 9800, "timestamp": "2025-10-10"}
]

try:
    print(f"  Cluster: {len(transactions_cluster)} suspicious transactions")
    sar = glm.generate_sar(transactions_cluster)
    print(f"  [OK] SAR generated!")
    print(f"\n  SAR Narrative:")
    print(f"  {sar[:300]}...")
except Exception as e:
    print(f"  [FAIL] SAR generation failed: {e}")
    print(f"  Error type: {type(e).__name__}")

print("\n" + "="*70)
print(" TEST SUMMARY")
print("="*70)
print("\nAll tests completed. Check results above.")
print("\nAPI Endpoint: https://api.z.ai/v1")
print(f"API Key: {os.getenv('GLM_API_KEY')[:20]}...")
print("\n")
