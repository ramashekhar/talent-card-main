#!/bin/bash
# FastAPI Talent Card System - Heroku Startup Script
# Handles proper Python path and module discovery for subfolder deployment

echo "🚀 Starting FastAPI Talent Card System..."

# Set working directory
cd /app/fast-api

# Set Python path to include the fast-api directory for proper imports
export PYTHONPATH="/app/fast-api:$PYTHONPATH"

# Display environment info
echo "Working directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Environment detection: ${DYNO:-local}"

# Verify critical files exist
if [ ! -f "main.py" ]; then
    echo "❌ ERROR: main.py not found in $(pwd)"
    exit 1
fi

if [ ! -d "routers" ]; then
    echo "❌ ERROR: routers/ directory not found"
    exit 1
fi

if [ ! -f "src/workday_client.py" ]; then
    echo "❌ ERROR: Workday client not found"
    exit 1
fi

echo "✅ All critical files verified"

# Start the application
echo "🎯 Starting gunicorn server..."
exec gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile -