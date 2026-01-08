#!/bin/bash

# Instagram Reels Automation - Service Startup Script
# This script starts the FastAPI server and creates a public tunnel

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Instagram Reels Automation Services${NC}"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Python environment path
PYTHON_PATH="/Users/filipepeixoto/Documents/Priv/Gym College/automation/.venv/bin/python"

# Kill existing processes
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "lt --port 8000" 2>/dev/null || true
sleep 2

# Start FastAPI server
echo -e "${GREEN}✨ Starting FastAPI server on port 8000...${NC}"
"$PYTHON_PATH" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/fastapi.log 2>&1 &
FASTAPI_PID=$!

# Wait for server to start
echo -e "${YELLOW}⏳ Waiting for server to start...${NC}"
sleep 5

# Check if server is running
if curl -s http://localhost:8000/docs | grep -q "html"; then
    echo -e "${GREEN}✅ FastAPI server is running (PID: $FASTAPI_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  Server might not be ready yet, check logs: tail -f /tmp/fastapi.log${NC}"
fi

# Start localtunnel
echo -e "${GREEN}🌐 Starting public tunnel...${NC}"
lt --port 8000 > /tmp/localtunnel.log 2>&1 &
TUNNEL_PID=$!

# Wait for tunnel to start
sleep 3

# Get public URL
PUBLIC_URL=$(cat /tmp/localtunnel.log | grep "your url is:" | awk '{print $4}')

if [ -z "$PUBLIC_URL" ]; then
    echo -e "${YELLOW}⚠️  Could not get tunnel URL, check logs: cat /tmp/localtunnel.log${NC}"
else
    echo -e "${GREEN}✅ Public tunnel is running (PID: $TUNNEL_PID)${NC}"
    echo -e "${BLUE}🌍 Public URL: ${GREEN}$PUBLIC_URL${NC}"
    
    # Update .env file
    echo -e "${YELLOW}📝 Updating .env with public URL...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|PUBLIC_URL_BASE=.*|PUBLIC_URL_BASE=$PUBLIC_URL|g" .env
    else
        # Linux
        sed -i "s|PUBLIC_URL_BASE=.*|PUBLIC_URL_BASE=$PUBLIC_URL|g" .env
    fi
    echo -e "${GREEN}✅ .env updated${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All services are running!${NC}"
echo ""
echo -e "${BLUE}📍 Local Server:${NC}   http://localhost:8000"
echo -e "${BLUE}📍 Public URL:${NC}     $PUBLIC_URL"
echo -e "${BLUE}📍 API Docs:${NC}       http://localhost:8000/docs"
echo -e "${BLUE}📍 Web UI:${NC}         http://localhost:8000"
echo ""
echo -e "${YELLOW}💡 First-time localtunnel users:${NC}"
echo -e "   Visit $PUBLIC_URL and click 'Continue' to whitelist your IP"
echo ""
echo -e "${BLUE}📊 View logs:${NC}"
echo -e "   FastAPI:  tail -f /tmp/fastapi.log"
echo -e "   Tunnel:   cat /tmp/localtunnel.log"
echo ""
echo -e "${BLUE}🛑 Stop services:${NC}"
echo -e "   pkill -f 'uvicorn app.main:app'"
echo -e "   pkill -f 'lt --port 8000'"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
