"""
Archimedes Project - GLM-4.6 Integration Demo

Demonstrates natural language querying, enhanced AML analysis,
and AI-powered economic insights using GLM-4.6
"""

import os
import sys

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("\n" + "="*70)
print(" ARCHIMEDES PROJECT - GLM-4.6 AI INTEGRATION DEMO")
print("="*70)

print("\nThis demo showcases the integration of GLM-4.6 (355B parameter MoE")
print("language model) into the Archimedes economic intelligence platform.")

# Check for API key
has_api_key = bool(os.getenv('GLM_API_KEY'))

if not has_api_key:
    print("\n" + "!"*70)
    print(" NOTE: GLM_API_KEY environment variable not set")
    print(" Running in DEMO MODE - showing capabilities without API calls")
    print(" To enable full functionality, set your GLM-4.6 API key:")
    print("   export GLM_API_KEY='your-api-key-here'  # Linux/Mac")
    print("   set GLM_API_KEY=your-api-key-here       # Windows")
    print("!"*70)

print("\n" + "="*70)
print(" FEATURE 1: Natural Language Query Translation")
print("="*70)

print("\nGLM-4.6 converts natural language questions into structured API calls.")
print("\nExamples of supported queries:")

queries = [
    "What was the GDP growth in China from 2020 to 2023?",
    "Compare inflation rates between USA, Germany, and Japan in 2023",
    "Show me unemployment trends in Brazil over the last 5 years",
    "How did France's debt-to-GDP ratio change in 2022?"
]

for i, query in enumerate(queries, 1):
    print(f"\n  {i}. '{query}'")

if has_api_key:
    print("\n  [LIVE] Testing query translation...")
    try:
        from integrations.glm46_integration import ArchimedesGLMIntegration

        glm = ArchimedesGLMIntegration()
        test_query = queries[0]
        available_indicators = ["GDP_GROWTH", "INFLATION", "UNEMPLOYMENT", "DEBT_GDP"]

        print(f"  Query: {test_query}")
        result = glm.process_natural_language_query(test_query, available_indicators)
        print(f"  Parsed Parameters:")
        import json
        print(f"  {json.dumps(result, indent=4)}")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("\n  [DEMO] Example output:")
    print("  {")
    print('    "endpoint": "timeseries",')
    print('    "country_code": "CHN",')
    print('    "indicator_code": "GDP_GROWTH",')
    print('    "start_year": 2020,')
    print('    "end_year": 2023')
    print("  }")

print("\n" + "="*70)
print(" FEATURE 2: Economic Data Explanation")
print("="*70)

print("\nGLM-4.6 provides expert-level analysis of economic data.")
print("\nCapabilities:")
print("  - Identifies key trends and patterns")
print("  - Provides historical context")
print("  - Explains implications for policy makers")
print("  - Highlights anomalies and outliers")

sample_data = {
    "indicator": "Inflation Rate",
    "country": "United States",
    "values": [1.2, 4.7, 8.0, 4.1, 3.4],
    "years": [2019, 2020, 2021, 2022, 2023]
}

print(f"\n  Example data: {sample_data}")

if has_api_key:
    print("\n  [LIVE] Generating analysis...")
    try:
        explanation = glm.explain_data(sample_data, "US inflation trends post-COVID")
        print(f"\n  Analysis:\n  {explanation[:400]}...")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("\n  [DEMO] Example analysis:")
    print("  'The United States experienced a significant inflation surge peaking")
    print("   at 8.0% in 2021, driven by pandemic-related supply chain disruptions")
    print("   and expansionary monetary policy. The subsequent decline to 3.4% by")
    print("   2023 reflects aggressive Federal Reserve rate hikes and normalization")
    print("   of supply chains. However, inflation remains above the 2% target...'")

print("\n" + "="*70)
print(" FEATURE 3: Enhanced AML Transaction Analysis")
print("="*70)

print("\nGLM-4.6 enhances machine learning AML detection with:")
print("  - Detailed narrative analysis of suspicious patterns")
print("  - Identification of specific red flags per FATF guidelines")
print("  - Recommended investigative actions")
print("  - Automated SAR (Suspicious Activity Report) generation")

sample_transaction = {
    "transaction_id": "TX987654",
    "amount": 9850,
    "from_country": "US",
    "to_country": "PA",  # Panama
    "timestamp": "2025-10-19T02:15:00Z",
    "is_cross_border": True
}

sample_ml_scores = {
    "ensemble_score": 87.3,
    "random_forest_score": 84.2,
    "xgboost_score": 90.1,
    "anomaly_score": 78.5,
    "risk_level": "critical"
}

print(f"\n  Sample Transaction:")
print(f"    ID: {sample_transaction['transaction_id']}")
print(f"    Amount: ${sample_transaction['amount']:,}")
print(f"    Route: {sample_transaction['from_country']} -> {sample_transaction['to_country']}")
print(f"    Time: {sample_transaction['timestamp']}")

print(f"\n  ML Risk Scores:")
print(f"    Ensemble: {sample_ml_scores['ensemble_score']}/100")
print(f"    XGBoost: {sample_ml_scores['xgboost_score']}/100")
print(f"    Risk Level: {sample_ml_scores['risk_level'].upper()}")

if has_api_key:
    print("\n  [LIVE] Generating AI analysis...")
    try:
        analysis = glm.analyze_suspicious_transaction(
            sample_transaction,
            sample_ml_scores
        )
        print(f"\n  AI Analysis:\n  {analysis.get('analysis', '')[:400]}...")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("\n  [DEMO] Example AI analysis:")
    print("  'RED FLAGS IDENTIFIED:")
    print("   - Structuring: Amount $9,850 just below $10k reporting threshold")
    print("   - Geographic Risk: Transfer to Panama (FATF high-risk jurisdiction)")
    print("   - Timing: Transaction at 02:15 AM (unusual hours)")
    print("")
    print("   RISK ASSESSMENT:")
    print("   High probability of structuring to evade CTR reporting. Pattern")
    print("   consistent with money laundering layering stage.")
    print("")
    print("   RECOMMENDED ACTIONS:")
    print("   - Review last 30 days of account activity")
    print("   - Check for similar just-below-threshold transactions")
    print("   - Verify beneficial owner and source of funds")
    print("   - Consider filing SAR with FinCEN'")

print("\n" + "="*70)
print(" FEATURE 4: Automated SAR Narrative Generation")
print("="*70)

print("\nGLM-4.6 generates professional SAR narratives following FinCEN guidelines.")

if has_api_key:
    print("\n  [LIVE] Generating SAR narrative...")
    try:
        sar = glm.generate_sar([sample_transaction])
        print(f"\n  {sar[:500]}...")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("\n  [DEMO] Example SAR narrative:")
    print("  'On October 19, 2025, Account #XXXXX initiated a wire transfer of")
    print("   $9,850.00 to a beneficiary account in Panama. This transaction is")
    print("   part of a pattern of structuring, with three similar transactions")
    print("   occurring within a 10-day period, each just below the $10,000 CTR")
    print("   threshold. The aggregate amount transferred was $29,550.00.")
    print("")
    print("   The account holder provided vague explanations for the transfers,")
    print("   claiming they were for 'business consulting services.' No supporting")
    print("   documentation was provided despite multiple requests. The timing of")
    print("   transactions during overnight hours (02:00-04:00 AM) and the choice")
    print("   of Panama as the destination jurisdiction raise additional concerns.'")

print("\n" + "="*70)
print(" FEATURE 5: Economic Forecast Explanation")
print("="*70)

print("\nGLM-4.6 explains ML model forecasts in plain language for stakeholders.")

forecast_example = {
    "indicator": "GDP Growth",
    "country": "United States",
    "model": "LSTM",
    "forecast": [2.1, 2.3, 2.5, 2.4],
    "quarters": ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"]
}

print(f"\n  Forecast: {forecast_example['indicator']} - {forecast_example['country']}")
print(f"  Model: {forecast_example['model']}")
print(f"  Predictions: {forecast_example['forecast']}")

if has_api_key:
    print("\n  [LIVE] Generating forecast explanation...")
    try:
        explanation = glm.explain_forecast(
            indicator=forecast_example['indicator'],
            forecast_values=forecast_example['forecast'],
            historical_values=[1.9, 2.0, 2.2, 2.1, 2.0],
            model_type=forecast_example['model']
        )
        print(f"\n  {explanation[:400]}...")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("\n  [DEMO] Example explanation:")
    print("  'The LSTM model forecasts modest but steady GDP growth for the US")
    print("   economy through 2025, ranging from 2.1% to 2.5% quarterly. This")
    print("   represents a continuation of the moderate expansion observed in")
    print("   recent quarters. The slight acceleration in Q3 may reflect seasonal")
    print("   factors and anticipated consumer spending patterns. Key assumptions")
    print("   include stable interest rates and no major geopolitical shocks.'")

print("\n" + "="*70)
print(" API ENDPOINTS")
print("="*70)

print("\nThe GLM-4.6 integration adds these endpoints to the Archimedes API:")
print("\n  1. POST /nlp/query")
print("     - Send natural language queries")
print("     - Get structured data + optional AI explanation")
print("\n  2. POST /nlp/explain")
print("     - Submit economic data")
print("     - Receive expert analysis")
print("\n  3. POST /aml/analyze")
print("     - Analyze suspicious transactions")
print("     - Get detailed risk assessment")
print("\n  4. POST /aml/generate-sar")
print("     - Submit transaction cluster")
print("     - Get professional SAR narrative")

print("\n" + "="*70)
print(" TECHNICAL SPECIFICATIONS")
print("="*70)

print("\n  Model: GLM-4.6")
print("  Architecture: 355B parameter Mixture of Experts (MoE)")
print("  Context Window: 200,000 tokens")
print("  API Provider: Z.ai (Zhipu AI)")
print("  Integration Method: REST API")
print("  Primary Use Cases:")
print("    - Natural language understanding")
print("    - Economic analysis and explanation")
print("    - AML narrative generation")
print("    - Forecast interpretation")

print("\n" + "="*70)
print(" GETTING STARTED")
print("="*70)

print("\n  1. Get GLM-4.6 API access:")
print("     Visit: https://docs.z.ai")
print("\n  2. Set environment variable:")
print("     export GLM_API_KEY='your-key-here'")
print("\n  3. Install dependencies:")
print("     pip install requests pandas numpy")
print("\n  4. Run the API server:")
print("     cd proof-of-concepts/poc-1-public-data")
print("     uvicorn api:app --reload")
print("\n  5. Test natural language queries:")
print("     POST http://localhost:8000/nlp/query")
print("     {\"query\": \"Show me GDP growth in China\", \"explain\": true}")

print("\n" + "="*70)
print(" BENEFITS OF GLM-4.6 INTEGRATION")
print("="*70)

print("\n  1. Accessibility: Non-technical users can query data in natural language")
print("  2. Insights: AI-generated analysis adds context and interpretation")
print("  3. Efficiency: Automated SAR generation saves compliance team hours")
print("  4. Accuracy: 200K token context window handles complex documents")
print("  5. Explainability: Clear narratives improve stakeholder understanding")

print("\n" + "="*70)
print(" DEMO COMPLETE")
print("="*70)

print("\nStatus:")
if has_api_key:
    print("  GLM-4.6 Integration: ACTIVE")
    print("  All features available")
else:
    print("  GLM-4.6 Integration: DEMO MODE")
    print("  Set GLM_API_KEY to activate full functionality")

print("\nFor more information:")
print("  - GLM-4.6 docs: https://docs.z.ai")
print("  - Archimedes project: See README.md")
print("  - Integration module: integrations/glm46_integration.py")

print("\n")
