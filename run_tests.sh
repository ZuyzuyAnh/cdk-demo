#!/bin/bash

# Test runner script for Todo API
set -e

echo "🚀 Setting up test environment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo "🧪 Running unit tests..."
python -m pytest src/tests/unit/ -v --tb=short -m "not slow"

echo "🔗 Running integration tests..."
python -m pytest src/tests/integration/ -v --tb=short -m "not slow"

echo "📊 Running all tests with coverage..."
python -m pytest src/tests/ -v --tb=short --cov=src/app --cov-report=term-missing

echo "✅ All tests completed!"

# Optional: Run specific test categories
if [ "$1" = "unit" ]; then
    echo "🧪 Running only unit tests..."
    python -m pytest src/tests/unit/ -v
elif [ "$1" = "integration" ]; then
    echo "🔗 Running only integration tests..."
    python -m pytest src/tests/integration/ -v
elif [ "$1" = "slow" ]; then
    echo "🐌 Running slow tests..."
    python -m pytest src/tests/ -v -m "slow"
fi
