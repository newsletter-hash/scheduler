#!/bin/bash
set -e

echo "🚀 Starting Local Development (VIEW ONLY)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  LOCAL MODE - For testing publishing, use Railway:"
echo "   https://scheduler-production-cd0b.up.railway.app"
echo ""
echo "   Why? Meta needs PUBLIC URLs to download videos."
echo "   Local = localhost (not public) ❌"
echo "   Railway = public domain ✅"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Kill existing processes
pkill -f uvicorn || true
sleep 1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "❌ uvicorn not found. Installing..."
    pip install uvicorn
fi

echo ""
echo "🚀 Starting server..."
echo ""
echo "📁 Database: SQLite (./output/schedules.db)"
echo "🌐 Local: http://localhost:8000"
echo "📄 API Docs: http://localhost:8000/docs"
echo "📅 Scheduled: http://localhost:8000/scheduled"
echo ""
echo "✅ Generate reels here"
echo "✅ Test UI here"
echo "❌ Publishing won't work (no public URL)"
echo ""
echo "📤 To actually publish → Use Railway"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Trap to clean up on exit
trap 'echo ""; echo "👋 Shutting down..."; exit 0' INT TERM

# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
