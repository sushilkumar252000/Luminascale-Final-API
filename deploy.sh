#!/bin/bash

# GFPGAN Free API Deployment Script
# Automates Docker setup and deployment

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     GFPGAN Free API - Deployment Script                    ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker & Docker Compose found"

# Check GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "⚠️  NVIDIA GPU not detected. This API requires GPU support."
    echo "   Install NVIDIA drivers: https://www.nvidia.com/Download/driverDetails.aspx"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ NVIDIA GPU detected"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
fi

# Setup .env
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "   Edit .env if needed, default is 10,000 requests/day"
else
    echo "✅ .env already exists"
fi

# Create logs directory
mkdir -p logs
echo "📁 Logs directory ready: ./logs"

# Build and start
echo ""
echo "🐳 Starting Docker containers..."
echo "   This may take 5-10 minutes on first run (downloading models)..."
echo ""

docker compose up --build -d

# Wait for API to be ready
echo ""
echo "⏳ Waiting for API to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Deployment Complete                   ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  API URL:     http://localhost:8000                         ║"
echo "║  Health:      http://localhost:8000/health                  ║"
echo "║  Docs:        http://localhost:8000/docs                    ║"
echo "║  Stats:       http://localhost:8000/stats                   ║"
echo "║                                                              ║"
echo "║  Daily Limit: 10,000 requests/IP                            ║"
echo "║                                                              ║"
echo "║  Logs:        docker compose logs -f api                    ║"
echo "║  Stop:        docker compose down                           ║"
echo "║  Restart:     docker compose restart api                    ║"
echo "║                                                              ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "🧪 Test with:"
echo ""
echo "  curl -X POST 'http://localhost:8000/enhance?scale=2' \\"
echo "    -F 'file=@test.jpg' \\"
echo "    --output enhanced.png"
echo ""

# Optional Nginx setup offer
echo "🌐 For production with Nginx:"
echo "   1. Copy nginx.conf to /etc/nginx/sites-available/"
echo "   2. Update server_name to your domain"
echo "   3. Set up SSL with Let's Encrypt"
echo "   4. Enable with: sudo a2ensite gfpgan"
echo ""

echo "📖 Full docs: See README.md"
