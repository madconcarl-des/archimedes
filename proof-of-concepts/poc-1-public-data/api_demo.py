"""
Archimedes POC1: FastAPI Demo Server (No Database Required)

Simplified version for demonstration without database setup
Enhanced with GLM-4.6 natural language query capabilities
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import os
import sys

# Add integrations path for GLM-4.6 module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from integrations.glm46_integration import ArchimedesGLMIntegration
    GLM_ENABLED = True
except ImportError:
    GLM_ENABLED = False
    print("GLM-4.6 integration not available. Install dependencies or check path.")

# Create FastAPI app
app = FastAPI(
    title="Archimedes POC1 API (Demo)",
    description="Public economic data aggregation platform with GLM-4.6 AI capabilities - Demo Mode",
    version="0.2.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GLM-4.6 integration
glm_integration = None
if GLM_ENABLED:
    try:
        glm_integration = ArchimedesGLMIntegration()
        print("GLM-4.6 integration enabled")
    except Exception as e:
        print(f"GLM-4.6 initialization failed: {e}")

# Sample data for demo
SAMPLE_COUNTRIES = [
    {"country_code": "USA", "country_name": "United States", "region": "North America", "income_level": "High"},
    {"country_code": "CHN", "country_name": "China", "region": "East Asia", "income_level": "Upper Middle"},
    {"country_code": "DEU", "country_name": "Germany", "region": "Europe", "income_level": "High"},
    {"country_code": "JPN", "country_name": "Japan", "region": "East Asia", "income_level": "High"},
]

SAMPLE_INDICATORS = [
    {"indicator_id": 1, "indicator_code": "GDP_GROWTH", "indicator_name": "GDP Growth", "unit": "%", "category": "Growth"},
    {"indicator_id": 2, "indicator_code": "INFLATION", "indicator_name": "Inflation Rate", "unit": "%", "category": "Prices"},
    {"indicator_id": 3, "indicator_code": "UNEMPLOYMENT", "indicator_name": "Unemployment Rate", "unit": "%", "category": "Labor"},
]

# Pydantic models
class Country(BaseModel):
    country_code: str
    country_name: str
    region: Optional[str] = None
    income_level: Optional[str] = None

class Indicator(BaseModel):
    indicator_id: int
    indicator_code: str
    indicator_name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None

class NaturalLanguageQuery(BaseModel):
    query: str
    explain: Optional[bool] = False

# API Endpoints

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "Archimedes POC1 API (Demo Mode)",
        "version": "0.2.0",
        "description": "Public economic data aggregation platform with GLM-4.6 AI",
        "mode": "DEMO - No database required",
        "glm_enabled": GLM_ENABLED and glm_integration is not None,
        "endpoints": {
            "health": "/health",
            "countries": "/countries",
            "indicators": "/indicators",
            "nlp_query": "/nlp/query (POST)",
            "explain": "/nlp/explain (POST)",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "note": "This is a demo server. For full functionality with database, use docker-compose or manual setup."
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": "demo",
        "database": "not required",
        "glm_integration": GLM_ENABLED and glm_integration is not None
    }

@app.get("/countries", response_model=List[Country])
def get_countries():
    """Get list of all countries (demo data)"""
    return [Country(**c) for c in SAMPLE_COUNTRIES]

@app.get("/indicators", response_model=List[Indicator])
def get_indicators(category: Optional[str] = None):
    """Get list of all indicators (demo data)"""
    indicators = SAMPLE_INDICATORS
    if category:
        indicators = [i for i in indicators if i.get("category") == category]
    return [Indicator(**i) for i in indicators]

@app.post("/nlp/query")
def natural_language_query(request: NaturalLanguageQuery):
    """
    Process natural language query using GLM-4.6

    Example:
    {
        "query": "What was China's GDP growth from 2020 to 2023?",
        "explain": true
    }
    """
    if not GLM_ENABLED or glm_integration is None:
        return {
            "status": "demo_mode",
            "query": request.query,
            "message": "GLM-4.6 integration not active. Set GLM_API_KEY to enable.",
            "demo_response": {
                "endpoint": "timeseries",
                "country_code": "CHN",
                "indicator_code": "GDP_GROWTH",
                "start_year": 2020,
                "end_year": 2023
            }
        }

    try:
        available_indicators = [i["indicator_code"] for i in SAMPLE_INDICATORS]

        parsed_params = glm_integration.process_natural_language_query(
            request.query,
            available_indicators
        )

        response = {
            "query": request.query,
            "parsed_params": parsed_params,
            "status": "success"
        }

        if request.explain:
            sample_data = {
                "query": request.query,
                "parsed_to": parsed_params
            }
            explanation = glm_integration.explain_data(sample_data, request.query)
            response["explanation"] = explanation

        return response

    except Exception as e:
        return {
            "status": "error",
            "query": request.query,
            "error": str(e),
            "message": "GLM-4.6 API error. Check API key and rate limits."
        }

@app.post("/nlp/explain")
def explain_data_endpoint(data: Dict, context: str = ""):
    """
    Generate natural language explanation of economic data using GLM-4.6

    Example:
    {
        "data": {"indicator": "GDP", "values": [2.1, 2.5, 2.8]},
        "context": "GDP growth trends"
    }
    """
    if not GLM_ENABLED or glm_integration is None:
        return {
            "status": "demo_mode",
            "message": "GLM-4.6 not active. Set GLM_API_KEY to enable.",
            "demo_explanation": "This is a demo explanation. With GLM-4.6 active, you would receive AI-generated expert analysis of the provided economic data."
        }

    try:
        explanation = glm_integration.explain_data(data, context)
        return {
            "explanation": explanation,
            "model": "glm-4.6",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "GLM-4.6 API error. Check API key and rate limits."
        }

@app.get("/demo/info")
def demo_info():
    """Information about demo mode"""
    return {
        "mode": "DEMO",
        "description": "This is a simplified demo server that works without database setup.",
        "features": {
            "basic_endpoints": True,
            "sample_data": True,
            "glm_integration": GLM_ENABLED and glm_integration is not None,
            "database": False
        },
        "glm_status": {
            "enabled": GLM_ENABLED,
            "initialized": glm_integration is not None,
            "api_key_set": bool(os.getenv('GLM_API_KEY')),
            "note": "Set GLM_API_KEY environment variable to enable AI features"
        },
        "full_version": {
            "description": "For full functionality with database and all features:",
            "options": [
                "Use Docker: cd proof-of-concepts/poc-1-public-data && docker-compose up",
                "Manual setup: See README-NO-DOCKER.md",
                "Or run the full demo.py: python demo.py"
            ]
        }
    }

# Run with: uvicorn api_demo:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("  ARCHIMEDES POC1 API - DEMO MODE")
    print("="*70)
    print("\n  Starting server at: http://localhost:8000")
    print("  API Documentation: http://localhost:8000/docs")
    print("  Alternative Docs: http://localhost:8000/redoc")
    print("\n  Mode: DEMO (No database required)")
    print(f"  GLM-4.6: {'ENABLED' if GLM_ENABLED and glm_integration else 'DISABLED'}")
    print("\n" + "="*70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
