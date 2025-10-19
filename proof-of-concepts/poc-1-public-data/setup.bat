@echo off
REM Quick Setup Script for Archimedes POC1 (Windows)

echo ==========================================
echo Archimedes POC1 - Quick Setup
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Docker is not installed
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    echo Alternative: Run without Docker - see README-NO-DOCKER.md
    exit /b 1
)

echo + Docker is installed

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo X Docker is not running
    echo Please start Docker Desktop and try again
    exit /b 1
)

echo + Docker is running
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo + .env file created
    echo.
    echo Note: You can add your FRED API key to .env for US economic data
    echo       Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html
    echo.
)

REM Start services
echo Starting services with Docker Compose...
echo.
docker-compose up -d

REM Wait for services
echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

REM Check API
echo.
echo Checking API health...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo + API is running!
) else (
    echo ~ API is starting... ^(may take a few more seconds^)
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Services running:
echo   API Documentation: http://localhost:8000/docs
echo   API Health Check:  http://localhost:8000/health
echo   Database ^(PgAdmin^): http://localhost:5050
echo      Email: admin@archimedes.com
echo      Password: admin
echo.
echo Next steps:
echo   1. Test the API: curl http://localhost:8000/health
echo   2. View docs: Open http://localhost:8000/docs in browser
echo   3. Ingest data: docker-compose exec api python ingestion.py
echo.
echo To stop: docker-compose down
echo To view logs: docker-compose logs -f
echo.
pause
