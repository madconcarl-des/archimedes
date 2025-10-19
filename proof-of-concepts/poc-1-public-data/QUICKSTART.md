# Archimedes POC1: Quick Start Guide

## Prerequisites

- **Docker** and **Docker Compose** installed (recommended)
  - OR **Python 3.11+** and **PostgreSQL 15+** installed locally
- **FRED API Key** (free): [Get one here](https://fred.stlouisfed.org/docs/api/api_key.html)

## Option 1: Quick Start with Docker (Recommended)

### Step 1: Clone and Setup

```bash
cd proof-of-concepts/poc-1-public-data

# Copy environment file and add your FRED API key
cp .env.example .env
# Edit .env and add your FRED_API_KEY

# Alternatively, export it directly:
export FRED_API_KEY=your_actual_api_key_here
```

### Step 2: Start All Services

```bash
# Start database and API
docker-compose up -d

# Check logs
docker-compose logs -f api
```

The database schema will be automatically initialized on first run.

### Step 3: Verify Services

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected"}
```

### Step 4: Ingest Data

```bash
# Run data ingestion (one-time or manually)
docker-compose exec api python ingestion.py

# This will fetch data from:
# - World Bank (G20 countries, GDP/inflation/unemployment)
# - FRED (US economic indicators)
# - IMF and OECD (if configured)
```

### Step 5: Query the API

```bash
# Get list of countries
curl http://localhost:8000/countries

# Get list of indicators
curl http://localhost:8000/indicators

# Get GDP data for USA
curl "http://localhost:8000/timeseries/USA/NY.GDP.MKTP.KD.ZG"

# Compare unemployment across countries
curl "http://localhost:8000/compare?indicator_code=SL.UEM.TOTL.ZS&country_codes=USA,CHN,JPN,DEU"
```

### Step 6: Access PgAdmin (Optional)

Open http://localhost:5050 in your browser:
- **Email:** admin@archimedes.com
- **Password:** admin

Add server connection:
- **Host:** postgres
- **Port:** 5432
- **Database:** archimedes_poc1
- **Username:** archimedes
- **Password:** password

### Stop Services

```bash
docker-compose down
# To also remove data:
docker-compose down -v
```

---

## Option 2: Local Development Setup

### Step 1: Setup PostgreSQL

```bash
# Create database
createdb archimedes_poc1

# Or using psql:
psql -c "CREATE DATABASE archimedes_poc1;"

# Initialize schema
psql -d archimedes_poc1 -f schema.sql
```

### Step 2: Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your database connection and FRED API key
```

### Step 3: Run Data Ingestion

```bash
python ingestion.py
```

This will take 5-10 minutes to fetch all data from public APIs.

### Step 4: Start API Server

```bash
uvicorn api:app --reload --port 8000
```

### Step 5: Test the API

Open http://localhost:8000/docs in your browser to see interactive API documentation.

---

## API Endpoints Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/countries` | GET | List all countries |
| `/indicators` | GET | List all indicators |
| `/data` | GET | Get observations with filters |
| `/timeseries/{country_code}/{indicator_code}` | GET | Get time series data |
| `/compare` | GET | Compare indicator across countries |

### Example API Calls

#### 1. Get All Countries

```bash
curl http://localhost:8000/countries
```

Response:
```json
[
  {
    "country_code": "USA",
    "country_name": "United States",
    "region": "North America",
    "income_level": "High income"
  },
  ...
]
```

#### 2. Get GDP Time Series for USA

```bash
curl "http://localhost:8000/timeseries/USA/NY.GDP.MKTP.KD.ZG?start_year=2020"
```

Response:
```json
{
  "country_code": "USA",
  "country_name": "United States",
  "indicator_code": "NY.GDP.MKTP.KD.ZG",
  "indicator_name": "GDP growth (annual %)",
  "data": [
    {"date": "2020-01-01", "value": -2.77},
    {"date": "2021-01-01", "value": 5.95},
    {"date": "2022-01-01", "value": 1.94},
    {"date": "2023-01-01", "value": 2.53}
  ]
}
```

#### 3. Compare Unemployment Across G7

```bash
curl "http://localhost:8000/compare?indicator_code=SL.UEM.TOTL.ZS&country_codes=USA,JPN,DEU,GBR,FRA,ITA,CAN"
```

Response:
```json
{
  "indicator_code": "SL.UEM.TOTL.ZS",
  "comparison": [
    {
      "country_code": "ITA",
      "country_name": "Italy",
      "date": "2023-01-01",
      "value": 7.6
    },
    {
      "country_code": "FRA",
      "country_name": "France",
      "date": "2023-01-01",
      "value": 7.1
    },
    ...
  ]
}
```

---

## Scheduling Automated Data Updates

### Using Cron (Linux/Mac)

```bash
# Add to crontab (run daily at 6 AM)
crontab -e

# Add this line:
0 6 * * * cd /path/to/poc-1-public-data && /path/to/venv/bin/python ingestion.py >> /var/log/archimedes-ingestion.log 2>&1
```

### Using Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set Trigger: Daily at 6:00 AM
4. Action: Start a program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `C:\path\to\poc-1-public-data\ingestion.py`

### Using Apache Airflow (Production)

```python
# dags/archimedes_ingestion_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from ingestion import DataIngestionService

default_args = {
    'owner': 'archimedes',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'archimedes_daily_ingestion',
    default_args=default_args,
    description='Daily economic data ingestion',
    schedule_interval='0 6 * * *',  # 6 AM UTC
    catchup=False
)

def run_ingestion(**context):
    service = DataIngestionService(
        database_url=os.getenv('DATABASE_URL'),
        fred_api_key=os.getenv('FRED_API_KEY')
    )
    service.run_daily_ingestion(
        countries=['USA', 'CHN', 'JPN', 'DEU', 'GBR', 'FRA', 'IND', 'BRA', 'CAN', 'AUS'],
        indicators={
            'worldbank': ['NY.GDP.MKTP.KD.ZG', 'FP.CPI.TOTL.ZG', 'SL.UEM.TOTL.ZS'],
            'fred': ['GDP', 'CPIAUCSL', 'UNRATE']
        },
        start_year=2000,
        end_year=datetime.now().year
    )

ingestion_task = PythonOperator(
    task_id='fetch_economic_data',
    python_callable=run_ingestion,
    dag=dag
)
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Connect to database manually
docker-compose exec postgres psql -U archimedes -d archimedes_poc1
```

### API Not Responding

```bash
# Check API logs
docker-compose logs api

# Restart API
docker-compose restart api

# Check if port 8000 is in use
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### Data Ingestion Failures

Common issues:
1. **API rate limits:** World Bank and OECD have rate limits. Add delays between requests.
2. **Network timeouts:** Increase timeout in `ingestion.py`:
   ```python
   response = requests.get(endpoint, timeout=60)  # Increase from 30 to 60 seconds
   ```
3. **Invalid API keys:** Verify your FRED API key is correct
4. **Data format changes:** External APIs sometimes change their response format. Check logs for parsing errors.

### Database Performance

If queries are slow:

```sql
-- Check if indexes exist
\di

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM v_observations WHERE country_code = 'USA';

-- Rebuild indexes if needed
REINDEX TABLE observations;

-- Update statistics
ANALYZE observations;
```

---

## Next Steps

### Expand Data Sources

Add more APIs to `ingestion.py`:

```python
def fetch_bis_data(self, ...):
    """Fetch from Bank for International Settlements"""
    # Implementation

def fetch_ecb_data(self, ...):
    """Fetch from European Central Bank"""
    # Implementation
```

### Add Data Validation

```python
# In ingestion.py
def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
    """Validate data quality before saving"""
    # Check for outliers
    df = df[df['value'].between(
        df['value'].quantile(0.01),
        df['value'].quantile(0.99)
    )]

    # Check for duplicates
    df = df.drop_duplicates(subset=['country_code', 'indicator', 'date'])

    return df
```

### Build a Frontend

Create a React dashboard:

```bash
npx create-react-app archimedes-dashboard
cd archimedes-dashboard

# Install charting libraries
npm install recharts axios react-router-dom

# Start development
npm start
```

---

## Production Deployment

### Deploy to AWS

1. **Database:** Use RDS PostgreSQL
2. **API:** Deploy to ECS Fargate or App Runner
3. **Scheduler:** Use EventBridge for cron jobs

```bash
# Example Terraform for RDS
resource "aws_db_instance" "archimedes" {
  identifier           = "archimedes-poc1"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  db_name              = "archimedes_poc1"
  username             = "archimedes"
  password             = var.db_password
  publicly_accessible  = false
  skip_final_snapshot  = true
}
```

### Deploy to Azure

1. **Database:** Use Azure Database for PostgreSQL
2. **API:** Deploy to Azure Container Instances or App Service
3. **Scheduler:** Use Azure Functions with Timer Trigger

### Monitor with Prometheus

```yaml
# docker-compose.yml - add monitoring
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

---

## Performance Benchmarks

Expected performance on t3.medium (2 vCPU, 4GB RAM):

| Metric | Target | Typical |
|--------|--------|---------|
| API response time (simple query) | <500ms | ~200ms |
| API response time (complex query) | <2s | ~800ms |
| Data ingestion (all sources) | <60min | ~30min |
| Database size (1 year data) | - | ~500MB |
| Concurrent users | 100+ | - |

---

## Support and Resources

- **Documentation:** See `/docs` folder
- **API Docs:** http://localhost:8000/docs (when running)
- **Database Schema:** See `schema.sql`
- **Issues:** Create issue in GitHub repository

---

## License

[Choose appropriate license - MIT, Apache 2.0, etc.]

---

## Contributors

- [Your Name/Organization]
- Built as Proof of Concept for Archimedes Platform

