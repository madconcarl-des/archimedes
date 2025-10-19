# Proof of Concept 1: Public Data Aggregation Platform

## Overview

This POC demonstrates the core capability of the Archimedes Platform: automated ingestion, standardization, and visualization of economic data from major international organizations.

## Objectives

1. **Validate Data Access:** Confirm we can programmatically access IMF, World Bank, and OECD data
2. **Demonstrate ETL:** Show data extraction, transformation, and loading into a unified schema
3. **Prove Visualization:** Create interactive dashboards for economic indicators
4. **Test Performance:** Measure data freshness and query responsiveness

## Scope

**Data Sources:**
- IMF (World Economic Outlook, International Financial Statistics)
- World Bank (World Development Indicators)
- OECD (Economic Outlook)
- Federal Reserve (FRED)

**Countries:** G20 (20 countries)

**Indicators:**
- GDP Growth Rate
- Inflation (CPI)
- Unemployment Rate
- Current Account Balance
- Government Debt to GDP

**Time Period:** 2000-2024 (24 years)

**Estimated Data Volume:**
- 5 sources × 20 countries × 5 indicators × 24 years = 12,000 data points
- With quarterly data: ~50,000 data points

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Data Sources (Public APIs)                  │
│  ┌──────────┬──────────────┬─────────────┬──────────────────┐  │
│  │ IMF API  │ World Bank   │  OECD API   │  FRED API        │  │
│  │ (SDMX)   │  API (REST)  │  (SDMX)     │  (REST)          │  │
│  └──────────┴──────────────┴─────────────┴──────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Ingestion Service                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Python Script (airflow DAG)                             │  │
│  │  - Fetch data from each API                              │  │
│  │  - Parse responses (JSON, XML, SDMX)                     │  │
│  │  - Validate data quality                                 │  │
│  │  - Transform to common schema                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Storage                              │
│  ┌────────────────────┬────────────────────────────────────┐   │
│  │ PostgreSQL         │  Unified Schema:                   │   │
│  │ (Relational)       │  - countries                       │   │
│  │                    │  - indicators                      │   │
│  │                    │  - observations (time series)      │   │
│  │                    │  - sources                         │   │
│  └────────────────────┴────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Service                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI (Python)                                        │  │
│  │  - GET /indicators                                       │  │
│  │  - GET /countries                                        │  │
│  │  - GET /data?country=USA&indicator=GDP&year=2020        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Visualization Dashboard                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React Web App                                           │  │
│  │  - Line charts for time series                           │  │
│  │  - World map for geographic visualization                │  │
│  │  - Comparison tools                                       │  │
│  │  - Export to CSV/Excel                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Language:** Python 3.11+
- **API Framework:** FastAPI
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy
- **Data Processing:** Pandas, NumPy
- **API Clients:** requests, pandas-datareader
- **Scheduler:** Apache Airflow (or simple cron)

### Frontend
- **Framework:** React 18 with TypeScript
- **Charting:** Recharts / Chart.js
- **Maps:** Leaflet / Mapbox
- **State Management:** React Query
- **Styling:** Tailwind CSS

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Docker Compose (POC) → Kubernetes (production)
- **Cloud:** Local development, deploy to AWS/Azure

## Database Schema

```sql
-- Countries dimension
CREATE TABLE countries (
    country_code VARCHAR(3) PRIMARY KEY,  -- ISO 3166-1 alpha-3
    country_name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    income_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indicators dimension
CREATE TABLE indicators (
    indicator_id SERIAL PRIMARY KEY,
    indicator_code VARCHAR(50) UNIQUE NOT NULL,
    indicator_name VARCHAR(200) NOT NULL,
    description TEXT,
    unit VARCHAR(50),  -- %, USD, Index, etc.
    category VARCHAR(50),  -- macroeconomic, financial, social, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data sources dimension
CREATE TABLE sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) UNIQUE NOT NULL,
    source_url VARCHAR(500),
    api_endpoint VARCHAR(500),
    update_frequency VARCHAR(50),  -- daily, monthly, quarterly, annual
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Observations fact table (time series data)
CREATE TABLE observations (
    observation_id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(3) REFERENCES countries(country_code),
    indicator_id INTEGER REFERENCES indicators(indicator_id),
    source_id INTEGER REFERENCES sources(source_id),
    time_period DATE NOT NULL,  -- Date of observation
    value NUMERIC(20, 4),  -- The actual value
    frequency VARCHAR(10),  -- A (annual), Q (quarterly), M (monthly)
    status VARCHAR(20),  -- preliminary, final, revised
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (country_code, indicator_id, source_id, time_period)
);

-- Indexes for query performance
CREATE INDEX idx_observations_country ON observations(country_code);
CREATE INDEX idx_observations_indicator ON observations(indicator_id);
CREATE INDEX idx_observations_time ON observations(time_period);
CREATE INDEX idx_observations_composite ON observations(country_code, indicator_id, time_period);

-- Metadata table for tracking data freshness
CREATE TABLE data_freshness (
    source_id INTEGER REFERENCES sources(source_id),
    indicator_id INTEGER REFERENCES indicators(indicator_id),
    last_update TIMESTAMP NOT NULL,
    next_update TIMESTAMP,
    record_count INTEGER,
    PRIMARY KEY (source_id, indicator_id)
);
```

## API Endpoints

### Data Source APIs

#### 1. IMF Data API
```python
# World Economic Outlook (WEO)
BASE_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc/"
ENDPOINT = f"{BASE_URL}CompactData/IFS/Q.US.NGDP_R_K_SA_XDC"
# Frequency: Q (quarterly), Country: US, Indicator: Real GDP

# Parameters:
# - Database: IFS (International Financial Statistics)
# - Frequency: A (annual), Q (quarterly), M (monthly)
# - Country: ISO 2-letter code
# - Indicator: NGDP_R_K_SA_XDC (Real GDP), PCPI_IX (CPI), etc.
```

#### 2. World Bank API
```python
BASE_URL = "https://api.worldbank.org/v2/"
ENDPOINT = f"{BASE_URL}country/USA/indicator/NY.GDP.MKTP.KD.ZG?format=json"
# Country: USA, Indicator: GDP growth (annual %), Format: JSON

# Key Indicators:
# - NY.GDP.MKTP.KD.ZG: GDP growth (annual %)
# - FP.CPI.TOTL.ZG: Inflation, consumer prices (annual %)
# - SL.UEM.TOTL.ZS: Unemployment, total (% of total labor force)
```

#### 3. OECD API
```python
BASE_URL = "https://stats.oecd.org/SDMX-JSON/data/"
DATASET = "QNA"  # Quarterly National Accounts
ENDPOINT = f"{BASE_URL}{DATASET}/USA.B1_GE.CUR+VOBARSA.Q"
# Country: USA, Measure: GDP, Transformation: Current prices + Volume

# Key Datasets:
# - QNA: Quarterly National Accounts
# - MEI: Main Economic Indicators
# - EO: Economic Outlook
```

#### 4. FRED API (Federal Reserve)
```python
BASE_URL = "https://api.stlouisfed.org/fred/"
ENDPOINT = f"{BASE_URL}series/observations?series_id=GDP&api_key=YOUR_KEY&file_type=json"
# Series: GDP (Gross Domestic Product)

# Key Series:
# - GDP: Gross Domestic Product
# - CPIAUCSL: Consumer Price Index for All Urban Consumers
# - UNRATE: Unemployment Rate
```

## Implementation

### Step 1: Environment Setup

```bash
# Create project directory
mkdir -p poc-1-public-data
cd poc-1-public-data

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary pandas requests python-dotenv
```

### Step 2: Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/archimedes"

    # API Keys
    IMF_API_KEY: str = ""  # IMF doesn't require API key
    WORLDBANK_API_KEY: str = ""  # World Bank doesn't require API key
    OECD_API_KEY: str = ""  # OECD doesn't require API key
    FRED_API_KEY: str = ""  # Get from https://fred.stlouisfed.org/docs/api/api_key.html

    # App Config
    APP_NAME: str = "Archimedes POC1"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
```

### Step 3: Data Ingestion

See `poc-1-public-data/ingestion.py` for full implementation

### Step 4: API Service

See `poc-1-public-data/api.py` for full implementation

### Step 5: Frontend Dashboard

See `poc-1-public-data/frontend/` for full implementation

## Success Metrics

### Data Coverage
- ✅ **Target:** 5 data sources integrated
- ✅ **Target:** 20 countries (G20)
- ✅ **Target:** 5 key indicators
- ✅ **Target:** 24 years of historical data (2000-2024)

### Data Quality
- ✅ **Target:** <5% missing data points
- ✅ **Target:** <1% data validation errors
- ✅ **Target:** Data freshness <24 hours from source publication

### Performance
- ✅ **Target:** API response time <500ms (p95)
- ✅ **Target:** Dashboard load time <2 seconds
- ✅ **Target:** Data ingestion <1 hour for all sources

### Usability
- ✅ **Target:** 3 visualization types (line chart, map, comparison)
- ✅ **Target:** Export functionality (CSV, Excel)
- ✅ **Target:** Mobile-responsive design

## Next Steps After POC

1. **Expand Data Sources:**
   - Add BIS, Eurostat, ECB, Bank of Japan
   - Include high-frequency data (daily, weekly)

2. **Add Forecasting:**
   - Implement simple time series forecasting (ARIMA)
   - Compare against IMF WEO forecasts

3. **Enhance Visualization:**
   - Add more chart types (bar, scatter, heatmap)
   - Interactive filtering and drill-down
   - Customizable dashboards

4. **Deploy to Cloud:**
   - Set up AWS/Azure infrastructure
   - Implement CI/CD pipeline
   - Add monitoring and alerting

5. **User Authentication:**
   - Implement OAuth 2.0
   - Role-based access control
   - Usage analytics

## Estimated Costs

### Development
- **Time:** 4-6 weeks (1 full-stack developer)
- **Cost:** $20,000 - $30,000 (contractor rates)

### Infrastructure (Monthly)
- **Database:** $50 (managed PostgreSQL)
- **Compute:** $100 (EC2/App Service)
- **Storage:** $10 (S3/Blob Storage)
- **Total:** ~$160/month

### Annual Operating Cost: ~$2,000

---

This POC demonstrates the technical feasibility of the data aggregation component and provides a foundation for the full Archimedes Platform.
