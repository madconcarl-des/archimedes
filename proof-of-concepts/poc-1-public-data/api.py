"""
Archimedes POC1: FastAPI REST API Service

Provides REST API endpoints for querying economic data
Enhanced with GLM-4.6 natural language query capabilities
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
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

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://archimedes:password@localhost:5432/archimedes_poc1")

# Create FastAPI app
app = FastAPI(
    title="Archimedes POC1 API",
    description="Public economic data aggregation platform with GLM-4.6 AI capabilities",
    version="0.2.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
engine = create_engine(DATABASE_URL)

# Initialize GLM-4.6 integration
glm_integration = None
if GLM_ENABLED:
    try:
        glm_integration = ArchimedesGLMIntegration()
        print("GLM-4.6 integration enabled")
    except Exception as e:
        print(f"GLM-4.6 initialization failed: {e}")


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


class Observation(BaseModel):
    country_code: str
    indicator_code: str
    date: datetime
    value: float
    source: str


class TimeSeriesData(BaseModel):
    country_code: str
    country_name: str
    indicator_code: str
    indicator_name: str
    data: List[dict]  # [{"date": "2020-01-01", "value": 2.5}, ...]


class NaturalLanguageQuery(BaseModel):
    query: str
    explain: Optional[bool] = False


class QueryResponse(BaseModel):
    query: str
    parsed_params: Dict
    data: Optional[Any] = None
    explanation: Optional[str] = None


# API Endpoints

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "Archimedes POC1 API",
        "version": "0.2.0",
        "description": "Public economic data aggregation platform with GLM-4.6 AI",
        "glm_enabled": GLM_ENABLED and glm_integration is not None,
        "endpoints": {
            "countries": "/countries",
            "indicators": "/indicators",
            "data": "/data",
            "timeseries": "/timeseries",
            "nlp_query": "/nlp/query (POST)",
            "explain": "/nlp/explain (POST)"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/countries", response_model=List[Country])
def get_countries():
    """Get list of all countries"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT country_code, country_name, region, income_level
                FROM countries
                ORDER BY country_name
            """))
            countries = [
                Country(
                    country_code=row[0],
                    country_name=row[1],
                    region=row[2],
                    income_level=row[3]
                )
                for row in result
            ]
            return countries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/indicators", response_model=List[Indicator])
def get_indicators(category: Optional[str] = None):
    """Get list of all indicators, optionally filtered by category"""
    try:
        query = """
            SELECT indicator_id, indicator_code, indicator_name,
                   description, unit, category
            FROM indicators
        """
        params = {}

        if category:
            query += " WHERE category = :category"
            params["category"] = category

        query += " ORDER BY indicator_name"

        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            indicators = [
                Indicator(
                    indicator_id=row[0],
                    indicator_code=row[1],
                    indicator_name=row[2],
                    description=row[3],
                    unit=row[4],
                    category=row[5]
                )
                for row in result
            ]
            return indicators
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data", response_model=List[Observation])
def get_data(
    country_code: Optional[str] = None,
    indicator_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(1000, le=10000)
):
    """
    Get observations with optional filters

    Args:
        country_code: Filter by country (ISO 3-letter code)
        indicator_code: Filter by indicator
        start_date: Filter by start date (YYYY-MM-DD)
        end_date: Filter by end date (YYYY-MM-DD)
        limit: Maximum number of results (max 10000)
    """
    try:
        query = """
            SELECT o.country_code, i.indicator_code, o.time_period, o.value, s.source_name
            FROM observations o
            JOIN indicators i ON o.indicator_id = i.indicator_id
            JOIN sources s ON o.source_id = s.source_id
            WHERE 1=1
        """
        params = {}

        if country_code:
            query += " AND o.country_code = :country_code"
            params["country_code"] = country_code

        if indicator_code:
            query += " AND i.indicator_code = :indicator_code"
            params["indicator_code"] = indicator_code

        if start_date:
            query += " AND o.time_period >= :start_date"
            params["start_date"] = start_date

        if end_date:
            query += " AND o.time_period <= :end_date"
            params["end_date"] = end_date

        query += " ORDER BY o.time_period DESC LIMIT :limit"
        params["limit"] = limit

        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            observations = [
                Observation(
                    country_code=row[0],
                    indicator_code=row[1],
                    date=row[2],
                    value=float(row[3]),
                    source=row[4]
                )
                for row in result
            ]
            return observations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/timeseries/{country_code}/{indicator_code}", response_model=TimeSeriesData)
def get_timeseries(
    country_code: str,
    indicator_code: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None
):
    """
    Get time series data for a specific country and indicator

    Args:
        country_code: ISO 3-letter country code
        indicator_code: Indicator code
        start_year: Optional start year filter
        end_year: Optional end year filter
    """
    try:
        query = """
            SELECT c.country_name, i.indicator_name, o.time_period, o.value
            FROM observations o
            JOIN countries c ON o.country_code = c.country_code
            JOIN indicators i ON o.indicator_id = i.indicator_id
            WHERE o.country_code = :country_code
              AND i.indicator_code = :indicator_code
        """
        params = {
            "country_code": country_code,
            "indicator_code": indicator_code
        }

        if start_year:
            query += " AND EXTRACT(YEAR FROM o.time_period) >= :start_year"
            params["start_year"] = start_year

        if end_year:
            query += " AND EXTRACT(YEAR FROM o.time_period) <= :end_year"
            params["end_year"] = end_year

        query += " ORDER BY o.time_period"

        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            rows = list(result)

            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for {country_code} - {indicator_code}"
                )

            country_name = rows[0][0]
            indicator_name = rows[0][1]

            data = [
                {"date": row[2].isoformat(), "value": float(row[3])}
                for row in rows
            ]

            return TimeSeriesData(
                country_code=country_code,
                country_name=country_name,
                indicator_code=indicator_code,
                indicator_name=indicator_name,
                data=data
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/compare")
def compare_countries(
    indicator_code: str,
    country_codes: str = Query(..., description="Comma-separated country codes"),
    year: Optional[int] = None
):
    """
    Compare an indicator across multiple countries

    Args:
        indicator_code: Indicator to compare
        country_codes: Comma-separated list of country codes (e.g., "USA,CHN,JPN")
        year: Optional year to compare (defaults to most recent)
    """
    try:
        codes = [c.strip() for c in country_codes.split(",")]

        query = """
            WITH ranked_data AS (
                SELECT
                    c.country_code,
                    c.country_name,
                    o.time_period,
                    o.value,
                    ROW_NUMBER() OVER (
                        PARTITION BY c.country_code
                        ORDER BY o.time_period DESC
                    ) as rn
                FROM observations o
                JOIN countries c ON o.country_code = c.country_code
                JOIN indicators i ON o.indicator_id = i.indicator_id
                WHERE i.indicator_code = :indicator_code
                  AND c.country_code IN :country_codes
        """
        params = {
            "indicator_code": indicator_code,
            "country_codes": tuple(codes)
        }

        if year:
            query += " AND EXTRACT(YEAR FROM o.time_period) = :year"
            params["year"] = year

        query += """
            )
            SELECT country_code, country_name, time_period, value
            FROM ranked_data
            WHERE rn = 1
            ORDER BY value DESC
        """

        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            comparison = [
                {
                    "country_code": row[0],
                    "country_name": row[1],
                    "date": row[2].isoformat(),
                    "value": float(row[3])
                }
                for row in result
            ]
            return {
                "indicator_code": indicator_code,
                "comparison": comparison
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/nlp/query")
def natural_language_query(request: NaturalLanguageQuery):
    """
    Process natural language query using GLM-4.6

    Args:
        request: Natural language query and options

    Returns:
        Parsed parameters, data, and optional explanation
    """
    if not GLM_ENABLED or glm_integration is None:
        raise HTTPException(
            status_code=503,
            detail="GLM-4.6 integration not available. Set GLM_API_KEY environment variable."
        )

    try:
        # Get available indicators
        with engine.connect() as conn:
            result = conn.execute(text("SELECT indicator_code FROM indicators"))
            available_indicators = [row[0] for row in result]

        # Parse query using GLM-4.6
        parsed_params = glm_integration.process_natural_language_query(
            request.query,
            available_indicators
        )

        # Execute query based on parsed params
        data = None
        endpoint = parsed_params.get('endpoint')

        if endpoint == 'timeseries':
            country_code = parsed_params.get('country_code')
            indicator_code = parsed_params.get('indicator_code')
            if country_code and indicator_code:
                data = get_timeseries(
                    country_code,
                    indicator_code,
                    parsed_params.get('start_year'),
                    parsed_params.get('end_year')
                )

        elif endpoint == 'compare':
            indicator_code = parsed_params.get('indicator_code')
            country_codes = parsed_params.get('country_codes', [])
            if indicator_code and country_codes:
                data = compare_countries(
                    indicator_code,
                    ','.join(country_codes),
                    parsed_params.get('year')
                )

        # Generate explanation if requested
        explanation = None
        if request.explain and data:
            explanation = glm_integration.explain_data(
                data.dict() if hasattr(data, 'dict') else data,
                context=request.query
            )

        return {
            "query": request.query,
            "parsed_params": parsed_params,
            "data": data,
            "explanation": explanation
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/nlp/explain")
def explain_data_endpoint(data: Dict, context: str = ""):
    """
    Generate natural language explanation of economic data using GLM-4.6

    Args:
        data: Economic data to explain
        context: Optional context about the data

    Returns:
        Natural language explanation
    """
    if not GLM_ENABLED or glm_integration is None:
        raise HTTPException(
            status_code=503,
            detail="GLM-4.6 integration not available"
        )

    try:
        explanation = glm_integration.explain_data(data, context)
        return {
            "explanation": explanation,
            "model": "glm-4.6",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn api:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
