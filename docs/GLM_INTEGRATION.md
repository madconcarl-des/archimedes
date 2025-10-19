# Archimedes Project - GLM-4.6 Integration Guide

## Overview

The Archimedes Project now includes integration with **GLM-4.6**, Zhipu AI's state-of-the-art 355 billion parameter Mixture of Experts (MoE) language model, adding powerful natural language processing capabilities to the economic intelligence platform.

## What's New

### GLM-4.6 Capabilities Added

1. **Natural Language Querying**
   - Ask questions in plain English
   - Automatic translation to API calls
   - Example: "What was China's GDP growth from 2020 to 2023?" → Structured query

2. **AI-Powered Economic Analysis**
   - Expert-level data interpretation
   - Trend identification and context
   - Policy implications
   - Stakeholder-friendly explanations

3. **Enhanced AML Detection**
   - Detailed transaction narratives
   - Red flag identification (FATF guidelines)
   - Investigative recommendations
   - Automated SAR generation

4. **Forecast Explanation**
   - Plain language interpretation of ML predictions
   - Assumptions and limitations
   - Confidence levels and scenarios

## Architecture

```
archimedes-project/
├── integrations/
│   ├── glm46_integration.py       # Core GLM-4.6 module
│   ├── requirements.txt           # Dependencies
│   └── README.md                  # Integration docs
│
├── proof-of-concepts/
│   ├── poc-1-public-data/
│   │   └── api.py                 # Enhanced with /nlp endpoints
│   ├── poc-2-aml-detection/
│   │   └── aml_detection_glm.py   # AI-enhanced AML
│   └── poc-3-glm-integration/
│       └── demo.py                # Full feature demo
```

## Quick Start

### 1. Installation

```bash
# Install GLM-4.6 integration dependencies
cd integrations
pip install -r requirements.txt
```

### 2. Get API Key

1. Visit https://docs.z.ai
2. Sign up for GLM-4.6 API access
3. Obtain your API key

### 3. Configure Environment

**Linux/Mac:**
```bash
export GLM_API_KEY='your-api-key-here'
```

**Windows CMD:**
```cmd
set GLM_API_KEY=your-api-key-here
```

**Windows PowerShell:**
```powershell
$env:GLM_API_KEY='your-api-key-here'
```

### 4. Run Demo

```bash
# Full GLM-4.6 feature demo
python proof-of-concepts/poc-3-glm-integration/demo.py

# Enhanced AML detection demo
python proof-of-concepts/poc-2-aml-detection/aml_detection_glm.py
```

### 5. Start API Server

```bash
cd proof-of-concepts/poc-1-public-data
uvicorn api:app --reload --port 8000
```

Access API docs: http://localhost:8000/docs

## Usage Examples

### Natural Language Query (Python)

```python
from integrations.glm46_integration import ArchimedesGLMIntegration

# Initialize
glm = ArchimedesGLMIntegration()

# Natural language query
query = "Compare GDP growth between USA, China, and Germany in 2023"
indicators = ["GDP_GROWTH", "INFLATION", "UNEMPLOYMENT"]

params = glm.process_natural_language_query(query, indicators)
print(params)
# Output: {
#   "endpoint": "compare",
#   "indicator_code": "GDP_GROWTH",
#   "country_codes": ["USA", "CHN", "DEU"],
#   "year": 2023
# }
```

### Economic Data Explanation

```python
# Sample economic data
data = {
    "indicator": "Inflation Rate",
    "country": "United States",
    "values": [1.2, 4.7, 8.0, 4.1, 3.4],
    "years": [2019, 2020, 2021, 2022, 2023]
}

# Get AI explanation
explanation = glm.explain_data(data, "Post-COVID inflation trends")
print(explanation)
```

### Enhanced AML Analysis

```python
# Suspicious transaction
transaction = {
    "transaction_id": "TX123456",
    "amount": 9850,
    "from_country": "US",
    "to_country": "PA",  # Panama
    "timestamp": "2025-10-19T02:30:00Z"
}

# ML risk scores
scores = {
    "ensemble_score": 85.3,
    "random_forest_score": 82.1,
    "xgboost_score": 88.5
}

# Get AI analysis
analysis = glm.analyze_suspicious_transaction(transaction, scores)
print(analysis['analysis'])
# Returns detailed red flags, assessment, and recommendations
```

### API Endpoints (REST)

**POST /nlp/query** - Natural language query
```bash
curl -X POST "http://localhost:8000/nlp/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me inflation in Japan from 2020 to 2023", "explain": true}'
```

**POST /nlp/explain** - Explain economic data
```bash
curl -X POST "http://localhost:8000/nlp/explain" \
  -H "Content-Type: application/json" \
  -d '{"data": {...}, "context": "GDP analysis"}'
```

## Features in Detail

### 1. Natural Language Query Translation

**Problem Solved**: Non-technical users struggle with API endpoints and parameters

**Solution**: Ask questions naturally, GLM-4.6 translates to API calls

**Examples**:
- "What was inflation in the US last year?" → `/timeseries/USA/INFLATION?year=2024`
- "Compare GDP between G7 countries" → `/compare?indicator=GDP&countries=USA,CAN,GBR,...`

### 2. Economic Analysis & Insights

**Problem Solved**: Raw data lacks context and interpretation

**Solution**: AI-generated analysis with trends, implications, and insights

**Output Quality**:
- Professional economist-level analysis
- Accessible to non-experts
- Identifies patterns and anomalies
- Provides actionable insights

### 3. Enhanced AML Detection

**Problem Solved**: ML models flag transactions but don't explain why

**Solution**: Detailed narratives following FATF AML guidelines

**Features**:
- Specific red flag identification
- Pattern analysis (structuring, layering, etc.)
- Compliance-ready language
- Investigative recommendations

### 4. Automated SAR Generation

**Problem Solved**: Writing Suspicious Activity Reports is time-consuming

**Solution**: GLM-4.6 generates professional SAR narratives

**Benefits**:
- Saves compliance team hours
- Consistent quality and format
- FinCEN guideline compliance
- Faster regulatory reporting

## Technical Specifications

### GLM-4.6 Model

- **Parameters**: 355 billion (Mixture of Experts)
- **Context Window**: 200,000 tokens
- **Architecture**: MoE (Mixture of Experts)
- **Provider**: Z.ai (Zhipu AI)
- **Released**: September 2025
- **Strengths**: Coding, reasoning, long-context understanding

### API Integration

- **Protocol**: REST API (HTTPS)
- **Authentication**: Bearer token (API key)
- **Format**: JSON request/response
- **Typical Latency**: 2-5 seconds
- **Rate Limits**: Depends on subscription tier

### Module Structure

**Main Classes**:

1. `GLM46Client` - Low-level API client
2. `EconomicDataQueryAgent` - NLP query parsing
3. `AMLAnalysisAgent` - Transaction analysis
4. `EconomicForecastExplainer` - Forecast interpretation
5. `ArchimedesGLMIntegration` - Unified interface

## Performance & Costs

### Latency

- Simple queries: 2-3 seconds
- Complex analysis: 3-5 seconds
- Long documents: 5-10 seconds

### API Costs

Visit https://z.ai/pricing for current pricing.

Typical usage:
- Query translation: ~500 tokens
- Data explanation: ~1,500 tokens
- AML analysis: ~2,000 tokens
- SAR generation: ~3,000 tokens

## Deployment

### Development

```bash
# Set API key
export GLM_API_KEY='dev-key'

# Run with auto-reload
uvicorn api:app --reload --port 8000
```

### Production

```bash
# Use production API key
export GLM_API_KEY='prod-key'

# Run with workers
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY integrations/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV GLM_API_KEY=${GLM_API_KEY}
CMD ["uvicorn", "api:app", "--host", "0.0.0.0"]
```

## Limitations & Considerations

### API Dependency

- Requires internet connection
- Subject to Z.ai API availability
- Costs scale with usage

### Accuracy

- AI-generated content should be reviewed
- Not a replacement for human experts
- May occasionally produce incorrect analysis

### Rate Limits

- Subject to API tier rate limits
- Implement caching for repeated queries
- Consider batch processing for high volume

### Privacy

- Do not send PII in API requests
- Sanitize data before submission
- Review Z.ai privacy policy

## Troubleshooting

### Common Issues

**"GLM_API_KEY not set" error**
```bash
# Solution: Set environment variable
export GLM_API_KEY='your-key'
```

**Import errors**
```bash
# Solution: Install dependencies
pip install -r integrations/requirements.txt
```

**API timeout**
```python
# Solution: Increase timeout
client = GLM46Client()
# Modify timeout in requests.post(..., timeout=120)
```

**Rate limit exceeded**
```
# Solution: Implement exponential backoff
# Or upgrade API tier
```

## Best Practices

### 1. Cache Results

```python
import functools

@functools.lru_cache(maxsize=100)
def cached_query(query_text):
    return glm.process_natural_language_query(query_text, indicators)
```

### 2. Error Handling

```python
try:
    analysis = glm.explain_data(data)
except Exception as e:
    logger.error(f"GLM analysis failed: {e}")
    analysis = "Analysis unavailable"
```

### 3. Sanitize Inputs

```python
def sanitize_transaction(tx):
    # Remove PII before sending to API
    return {k: v for k, v in tx.items() if k not in ['ssn', 'account_holder']}
```

### 4. Monitor Costs

```python
# Log API usage
logger.info(f"GLM API call: {endpoint}, tokens: ~{estimated_tokens}")
```

## Roadmap

### Upcoming Features

- [ ] Batch query processing
- [ ] Streaming responses for long analysis
- [ ] Fine-tuned models for economic domain
- [ ] Multi-language support
- [ ] Voice interface integration

### Future Integrations

- GPT-4 fallback option
- Claude integration for comparison
- Local LLM option (Llama 3, etc.)

## Resources

### Documentation

- **GLM-4.6 Official Docs**: https://docs.z.ai
- **API Reference**: https://docs.z.ai/api-references/text-models-llm/zhipu/glm-4.6
- **Model Card**: https://huggingface.co/zai-org/GLM-4.6
- **Archimedes Integration**: `/integrations/README.md`

### Support

- GLM-4.6 Issues: Z.ai support
- Archimedes Issues: Project issue tracker
- Community: Project discussions

## License

GLM-4.6 integration follows the main Archimedes Project license.
GLM-4.6 API usage subject to Z.ai terms of service.

---

**Integration Version**: 1.0
**Last Updated**: 2025-10-19
**Compatible with**: Archimedes Project v0.2.0+
**GLM-4.6 Version**: 4.6 (Latest)
