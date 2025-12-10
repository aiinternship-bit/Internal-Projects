#!/bin/bash
# Quick build test script for Docker

set -e  # Exit on error

echo "🔨 Starting Docker build test..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your ANTHROPIC_API_KEY"
    exit 1
fi

echo "✓ .env file exists"
echo ""

# Build the Docker image
echo "📦 Building Docker image (this may take several minutes)..."
echo ""

docker build -t ai-interns:test . 2>&1 | tee build.log

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "To run the container:"
    echo "  docker-compose up -d"
    echo ""
    echo "Or manually:"
    echo "  docker run -d -p 5001:5001 --env-file .env ai-interns:test"
    echo ""
    echo "Build log saved to: build.log"
else
    echo ""
    echo "❌ Build failed!"
    echo "Check build.log for details"
    exit 1
fi
