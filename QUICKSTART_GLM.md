# GLM-4.6 Integration - Quick Reference

## Installation (30 seconds)

```bash
pip install -r integrations/requirements.txt
export GLM_API_KEY='your-api-key-here'
python proof-of-concepts/poc-3-glm-integration/demo.py
```

## Usage Examples

### Python - Natural Language Query
```python
from integrations.glm46_integration import ArchimedesGLMIntegration

glm = ArchimedesGLMIntegration()
params = glm.process_natural_language_query(
    "Compare GDP between USA and China in 2023",
    ["GDP_GROWTH", "INFLATION"]
)
```

### Python - Explain Economic Data
```python
explanation = glm.explain_data(
    {"indicator": "GDP", "values": [2.1, 2.5, 2.8]},
    context="GDP growth trends"
)
```

### Python - Analyze Suspicious Transaction
```python
analysis = glm.analyze_suspicious_transaction(
    transaction={"amount": 9850, "to_country": "PA"},
    risk_scores={"ensemble_score": 87.3}
)
```

### REST API - Natural Language Query
```bash
curl -X POST "http://localhost:8000/nlp/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show inflation in USA from 2020-2023", "explain": true}'
```

### REST API - Explain Data
```bash
curl -X POST "http://localhost:8000/nlp/explain" \
  -H "Content-Type: application/json" \
  -d '{"data": {...}, "context": "GDP analysis"}'
```

## File Locations

| File | Purpose |
|------|---------|
| `integrations/glm46_integration.py` | Core module |
| `integrations/README.md` | Integration docs |
| `proof-of-concepts/poc-3-glm-integration/demo.py` | Full demo |
| `proof-of-concepts/poc-2-aml-detection/aml_detection_glm.py` | Enhanced AML |
| `docs/GLM_INTEGRATION.md` | Complete guide |
| `docs/GLM_SUMMARY.md` | Implementation summary |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/nlp/query` | POST | Natural language queries |
| `/nlp/explain` | POST | Economic data explanation |

## Environment Variables

```bash
export GLM_API_KEY='your-api-key'        # Required
export GLM_BASE_URL='https://api.z.ai/v1'  # Optional
```

## Quick Commands

```bash
# Run demo
python proof-of-concepts/poc-3-glm-integration/demo.py

# Run enhanced AML demo
python proof-of-concepts/poc-2-aml-detection/aml_detection_glm.py

# Start API server
cd proof-of-concepts/poc-1-public-data
uvicorn api:app --reload --port 8000

# View API docs
http://localhost:8000/docs
```

## Features Summary

1. **Natural Language Queries** - Ask questions in English
2. **Economic Analysis** - AI-generated insights
3. **Enhanced AML** - Detailed transaction analysis
4. **SAR Generation** - Automated compliance reports
5. **Forecast Explanation** - Plain language predictions

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "GLM_API_KEY not set" | `export GLM_API_KEY='your-key'` |
| Import errors | `pip install -r integrations/requirements.txt` |
| API timeout | Increase timeout in code |
| Rate limit | Implement caching or upgrade tier |

## Resources

- **GLM-4.6 Docs**: https://docs.z.ai
- **Get API Key**: https://docs.z.ai (sign up)
- **Model Info**: https://huggingface.co/zai-org/GLM-4.6
- **Pricing**: https://z.ai/pricing

## Support

- GLM-4.6: Z.ai support
- Archimedes: Project issue tracker
- Docs: `docs/GLM_INTEGRATION.md`

---

**Version**: 1.0 | **Date**: 2025-10-19 | **Status**: Production-Ready
