# Archimedes GLM-4.6 Integration

This directory contains the integration module for GLM-4.6 (Zhipu AI's 355B parameter language model) into the Archimedes Project.

## Overview

GLM-4.6 enhances the Archimedes platform with:
- Natural language querying of economic data
- AI-powered analysis and explanation
- Enhanced AML transaction narrative generation
- Economic forecast interpretation

## Quick Start

### 1. Get API Access

Sign up for GLM-4.6 API access:
- Visit: https://docs.z.ai
- Create account and get API key

### 2. Set Environment Variable

**Linux/Mac:**
```bash
export GLM_API_KEY='your-api-key-here'
```

**Windows:**
```cmd
set GLM_API_KEY=your-api-key-here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test Integration

```python
from integrations.glm46_integration import ArchimedesGLMIntegration

# Initialize
glm = ArchimedesGLMIntegration()

# Test natural language query
indicators = ["GDP_GROWTH", "INFLATION", "UNEMPLOYMENT"]
params = glm.process_natural_language_query(
    "What was China's GDP growth in 2023?",
    indicators
)
print(params)
```

## Features

### Natural Language Query Translation

Convert questions into structured API calls:

```python
query = "Compare inflation between USA and China from 2020 to 2023"
params = glm.process_natural_language_query(query, available_indicators)
# Returns: {"endpoint": "compare", "indicator_code": "INFLATION", ...}
```

### Economic Data Explanation

Get expert analysis of data:

```python
data = {"indicator": "GDP", "values": [2.1, 2.3, 2.5]}
explanation = glm.explain_data(data, "GDP growth trends")
# Returns natural language analysis
```

### Enhanced AML Analysis

Detailed transaction analysis:

```python
transaction = {
    "transaction_id": "TX123",
    "amount": 9950,
    "from_country": "US",
    "to_country": "PA"
}

risk_scores = {"ensemble_score": 85.3}
analysis = glm.analyze_suspicious_transaction(transaction, risk_scores)
# Returns red flags, assessment, and recommendations
```

### SAR Generation

Automated Suspicious Activity Reports:

```python
transactions = [...]  # List of suspicious transactions
sar_narrative = glm.generate_sar(transactions)
# Returns professional SAR text
```

## API Integration

The GLM-4.6 module integrates with the Archimedes API:

### New Endpoints

**POST /nlp/query**
```json
{
  "query": "Show me GDP growth in China from 2020-2023",
  "explain": true
}
```

**POST /nlp/explain**
```json
{
  "data": {...},
  "context": "GDP analysis"
}
```

## Architecture

```
integrations/
├── glm46_integration.py      # Main integration module
├── requirements.txt           # Python dependencies
└── README.md                  # This file

Classes:
- GLM46Client: Low-level API client
- EconomicDataQueryAgent: NLP query translation
- AMLAnalysisAgent: Transaction analysis
- EconomicForecastExplainer: Forecast interpretation
- ArchimedesGLMIntegration: Main interface
```

## Configuration

### Environment Variables

- `GLM_API_KEY`: Your GLM-4.6 API key (required)
- `GLM_BASE_URL`: API endpoint (default: https://api.z.ai/v1)

### Model Parameters

```python
client = GLM46Client()
client.temperature = 0.7  # Creativity (0-1)
client.max_tokens = 4000  # Response length
```

## Examples

See demonstration files:
- `proof-of-concepts/poc-3-glm-integration/demo.py` - Full feature demo
- `proof-of-concepts/poc-2-aml-detection/aml_detection_glm.py` - Enhanced AML

## Technical Specifications

- **Model**: GLM-4.6
- **Parameters**: 355B (Mixture of Experts)
- **Context Window**: 200,000 tokens
- **Provider**: Z.ai (Zhipu AI)
- **API**: REST with JSON
- **Authentication**: Bearer token

## Performance

- Typical latency: 2-5 seconds
- Throughput: Depends on API tier
- Cost: See Z.ai pricing (https://z.ai/pricing)

## Limitations

- Requires internet connection
- API key needed for production use
- Subject to Z.ai rate limits and pricing
- English language optimized (multi-language support varies)

## Troubleshooting

**"GLM_API_KEY not set" error:**
- Set environment variable with your API key

**Import errors:**
- Install requirements: `pip install -r requirements.txt`

**API timeout:**
- Check internet connection
- Verify API key is valid
- Try increasing timeout in code

**Rate limit errors:**
- Reduce request frequency
- Upgrade API tier

## Support

- GLM-4.6 Documentation: https://docs.z.ai
- Archimedes Project: See main README.md
- Issues: Report in project issue tracker

## License

Same as main Archimedes Project.

---

**Last Updated**: 2025-10-19
**Integration Version**: 1.0
**GLM-4.6 Version**: 4.6 (Latest)
