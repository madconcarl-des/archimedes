#!/bin/bash
# Quick Setup Script for Archimedes POC1

echo "=========================================="
echo "Archimedes POC1 - Quick Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    echo ""
    echo "Alternative: Run without Docker (see README-NO-DOCKER.md)"
    exit 1
fi

echo "✅ Docker is installed"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  Note: You can add your FRED API key to .env for US economic data"
    echo "   Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html"
    echo ""
fi

# Start services
echo "Starting services with Docker Compose..."
echo ""
docker-compose up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to start..."
sleep 5

# Check if API is responding
echo ""
echo "Checking API health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is running!"
else
    echo "⚠️  API is starting... (may take a few more seconds)"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Services running:"
echo "  📊 API Documentation: http://localhost:8000/docs"
echo "  🔍 API Health Check:  http://localhost:8000/health"
echo "  🗄️  Database (PgAdmin): http://localhost:5050"
echo "     Email: admin@archimedes.com"
echo "     Password: admin"
echo ""
echo "Next steps:"
echo "  1. Test the API: curl http://localhost:8000/health"
echo "  2. View docs: Open http://localhost:8000/docs in browser"
echo "  3. Ingest data: docker-compose exec api python ingestion.py"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
echo ""
