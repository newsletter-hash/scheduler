#!/bin/bash

# Stop all automation services

set -e

echo "🛑 Stopping Instagram Reels Automation Services..."

# Kill FastAPI server
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "✅ FastAPI server stopped" || echo "ℹ️  FastAPI server not running"

# Kill localtunnel
pkill -f "lt --port 8000" 2>/dev/null && echo "✅ Localtunnel stopped" || echo "ℹ️  Localtunnel not running"

echo ""
echo "✅ All services stopped"
