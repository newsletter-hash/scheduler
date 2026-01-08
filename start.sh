#!/bin/bash

# Start script for Instagram Reels Automation
# This script activates the virtual environment and starts the server

cd "$(dirname "$0")"

echo "🚀 Starting Instagram Reels Automation..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Start the server
echo "📡 Server will be available at: http://localhost:8000"
echo "📝 API documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --port 8000
