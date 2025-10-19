# Running Without Docker

If you don't have Docker installed or prefer to run the POC locally, follow these steps.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Git (optional)

## Step 1: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Setup PostgreSQL Database

### Option A: Local PostgreSQL Installation

1. **Install PostgreSQL:**
   - Windows: Download from https://www.postgresql.org/download/windows/
   - Mac: `brew install postgresql@15`
   - Linux: `sudo apt-get install postgresql-15`

2. **Create Database:**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE archimedes_poc1;
CREATE USER archimedes WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE archimedes_poc1 TO archimedes;
\q
```

3. **Initialize Schema:**
```bash
psql -U archimedes -d archimedes_poc1 -f schema.sql
```

### Option B: Use SQLite (Simpler, but limited)

For a quick test without PostgreSQL:

1. **Modify the database URL** in your `.env` file:
```bash
DATABASE_URL=sqlite:///archimedes_poc1.db
```

2. **The SQLite database will be created automatically** when you first run the API.

Note: SQLite version will have limited concurrent access and some features may not work.

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file (optional - add FRED API key for US data)
# Get free key at: https://fred.stlouisfed.org/docs/api/api_key.html
```

## Step 4: Run the API Server

```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Start the API server
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 5: Test the API

Open a new terminal and test:

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected"}

# Get countries
curl http://localhost:8000/countries

# View API documentation
# Open in browser: http://localhost:8000/docs
```

## Step 6: Ingest Data (Optional)

In a new terminal (with venv activated):

```bash
# Run data ingestion
python ingestion.py
```

This will fetch data from:
- World Bank (GDP, inflation, unemployment for G20)
- FRED (US economic indicators - requires API key)
- IMF and OECD (if configured)

**Note:** Initial data ingestion may take 5-10 minutes.

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:** Make sure virtual environment is activated and dependencies installed:
```bash
pip install -r requirements.txt
```

### Issue: "Connection to database failed"

**Solution:** Check PostgreSQL is running:
```bash
# Check if PostgreSQL is running
# Windows:
pg_ctl status

# Mac:
brew services list | grep postgresql

# Linux:
sudo systemctl status postgresql
```

### Issue: "Port 8000 already in use"

**Solution:** Use a different port:
```bash
uvicorn api:app --reload --port 8001
```

### Issue: "Database archimedes_poc1 does not exist"

**Solution:** Create the database:
```bash
psql -U postgres -c "CREATE DATABASE archimedes_poc1;"
psql -U archimedes -d archimedes_poc1 -f schema.sql
```

## Simplified Test Script

Create a file called `test_local.py`:

```python
"""
Quick test script to verify local setup
"""

import requests

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing Archimedes POC1 API...")
    print("=" * 50)

    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return False

    # Test 2: Get countries
    print("\n2. Testing countries endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/countries")
        countries = response.json()
        print(f"   Found {len(countries)} countries")
        if countries:
            print(f"   Sample: {countries[0]}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 3: Get indicators
    print("\n3. Testing indicators endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/indicators")
        indicators = response.json()
        print(f"   Found {len(indicators)} indicators")
        if indicators:
            print(f"   Sample: {indicators[0]['indicator_name']}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 50)
    print("✅ API is working!")
    print(f"📊 View full documentation: {BASE_URL}/docs")
    return True

if __name__ == "__main__":
    test_api()
```

Run it:
```bash
python test_local.py
```

## Performance Tips

### 1. Use Connection Pooling

For production, configure connection pooling in your database URL:
```python
DATABASE_URL = "postgresql://archimedes:password@localhost:5432/archimedes_poc1?pool_size=20&max_overflow=10"
```

### 2. Enable Query Caching

Add Redis for caching (optional):
```bash
pip install redis
```

### 3. Run with Multiple Workers

For better performance:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

## Next Steps

Once you have the API running:

1. **Explore API Documentation:** http://localhost:8000/docs
2. **Ingest Data:** Run `python ingestion.py`
3. **Query Data:** Use the API endpoints to query economic data
4. **Build Frontend:** Connect a React/Vue.js frontend to the API
5. **Deploy:** Move to cloud (AWS, Azure, GCP) when ready

## Alternative: Use Docker (Recommended)

Docker is much simpler and handles all dependencies:

1. **Install Docker Desktop:** https://www.docker.com/products/docker-desktop
2. **Run:** `docker-compose up -d`
3. **Done!** API available at http://localhost:8000

## System Requirements

**Minimum:**
- RAM: 4GB
- Storage: 10GB free space
- CPU: 2 cores

**Recommended:**
- RAM: 8GB+
- Storage: 50GB+ (for data growth)
- CPU: 4+ cores

## Getting Help

If you encounter issues:

1. Check the logs for errors
2. Verify all prerequisites are installed
3. Review the QUICKSTART.md guide
4. Check database connectivity
5. Ensure no port conflicts (8000, 5432)

---

**Pro Tip:** Docker setup is much easier! If possible, use `docker-compose up -d` instead of manual setup.
