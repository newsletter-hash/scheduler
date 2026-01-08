#!/bin/bash

echo "⚠️  IMPORTANT: Link to the SCHEDULER service (NOT Postgres!)"
echo ""
echo "When prompted:"
echo "  1. Select: newsletter-hash's Projects"
echo "  2. Select: lucky-healing"
echo "  3. Select: production"
echo "  4. Select: Scheduler ⬅️  (NOT Postgres!)"
echo ""
read -p "Press ENTER when ready to link to Scheduler service..."

cd /Users/filipepeixoto/Documents/Priv/Gym\ College/automation/reels-automation

# Unlink from Postgres
railway unlink 2>/dev/null || true

# Link to project - user must select Scheduler
railway link

echo ""
echo "✅ Linked! Verifying..."
railway status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "If you see 'Service: Scheduler' above, you're good!"
echo "If you see 'Service: Postgres', run this script again and select Scheduler."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
