#!/bin/bash

# Check status of all Instagram Reels Automation services

set -e

echo "═══════════════════════════════════════════════════════"
echo "  Instagram Reels Automation - Status Check"
echo "═══════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check FastAPI Server
echo -n "FastAPI Server (port 8000): "
if lsof -i :8000 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ RUNNING${NC}"
    PID=$(lsof -ti:8000)
    echo "  Process ID: $PID"
else
    echo -e "${RED}❌ NOT RUNNING${NC}"
fi

echo ""

# Check Localtunnel
echo -n "Public Tunnel (localtunnel): "
if pgrep -f "lt --port 8000" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ RUNNING${NC}"
    if [ -f /tmp/localtunnel.log ]; then
        PUBLIC_URL=$(cat /tmp/localtunnel.log | grep "your url is:" | awk '{print $4}')
        if [ -n "$PUBLIC_URL" ]; then
            echo "  URL: $PUBLIC_URL"
        fi
    fi
else
    echo -e "${RED}❌ NOT RUNNING${NC}"
fi

echo ""

# Check .env configuration
echo "Environment Configuration:"
cd "$(dirname "$0")"

if [ -f .env ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    
    # Check OpenAI API key
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        echo "  ✓ OpenAI API key configured"
    else
        echo -e "  ${YELLOW}⚠ OpenAI API key missing${NC}"
    fi
    
    # Check Instagram credentials
    if grep -q "INSTAGRAM_ACCESS_TOKEN=" .env && ! grep -q "INSTAGRAM_ACCESS_TOKEN=$" .env; then
        echo "  ✓ Instagram access token configured"
    else
        echo -e "  ${YELLOW}⚠ Instagram access token missing${NC}"
    fi
    
    if grep -q "INSTAGRAM_BUSINESS_ACCOUNT_ID=" .env && ! grep -q "INSTAGRAM_BUSINESS_ACCOUNT_ID=$" .env; then
        echo "  ✓ Instagram business account configured"
    else
        echo -e "  ${YELLOW}⚠ Instagram business account missing${NC}"
    fi
    
    # Check PUBLIC_URL_BASE
    if grep -q "PUBLIC_URL_BASE=https://" .env; then
        PUBLIC_URL=$(grep "PUBLIC_URL_BASE=" .env | cut -d'=' -f2)
        echo "  ✓ Public URL: $PUBLIC_URL"
    else
        echo -e "  ${YELLOW}⚠ Public URL not configured (using localhost)${NC}"
    fi
else
    echo -e "${RED}❌ .env file not found${NC}"
fi

echo ""

# Test endpoints
echo "Testing Endpoints:"

# Test root endpoint
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 2>/dev/null | grep -q "200"; then
    echo -e "  ${GREEN}✓${NC} Web UI: http://localhost:8000"
else
    echo -e "  ${RED}✗${NC} Web UI: Not accessible"
fi

# Test API docs
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null | grep -q "200"; then
    echo -e "  ${GREEN}✓${NC} API Docs: http://localhost:8000/docs"
else
    echo -e "  ${RED}✗${NC} API Docs: Not accessible"
fi

# Test public URL if tunnel is running
if [ -n "$PUBLIC_URL" ]; then
    if curl -s -o /dev/null -w "%{http_code}" "$PUBLIC_URL" 2>/dev/null | grep -q "200"; then
        echo -e "  ${GREEN}✓${NC} Public URL: $PUBLIC_URL"
    else
        echo -e "  ${YELLOW}⚠${NC} Public URL: Not accessible (may need IP whitelisting)"
    fi
fi

echo ""

# Check output directories
echo "Output Directories:"
for dir in output/videos output/thumbnails output/ai_backgrounds; do
    if [ -d "$dir" ]; then
        count=$(ls -1 "$dir" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${GREEN}✓${NC} $dir ($count files)"
    else
        echo -e "  ${YELLOW}⚠${NC} $dir (not created yet)"
    fi
done

echo ""

# Overall status
echo "═══════════════════════════════════════════════════════"

if lsof -i :8000 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ System is OPERATIONAL${NC}"
    echo ""
    echo "Quick Links:"
    echo "  • Web UI:    http://localhost:8000"
    echo "  • API Docs:  http://localhost:8000/docs"
    if [ -n "$PUBLIC_URL" ]; then
        echo "  • Public:    $PUBLIC_URL"
    fi
else
    echo -e "${RED}❌ System is NOT RUNNING${NC}"
    echo ""
    echo "To start services, run:"
    echo "  ./start_services.sh"
fi

echo "═══════════════════════════════════════════════════════"
