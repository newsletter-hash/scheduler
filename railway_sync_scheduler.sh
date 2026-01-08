#!/bin/bash
set -e

echo "🚂 Railway Environment Setup - SCHEDULER SERVICE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  This will sync .env variables to the SCHEDULER service"
echo "   (Not the Postgres database service)"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Logging in to Railway..."
    railway login
fi

# Unlink current service
echo "🔓 Unlinking from current service..."
railway unlink -y || true

# Link to Scheduler service
echo "🔗 Linking to Scheduler service..."
echo "   👉 Select: lucky-healing > production > Scheduler"
railway link

# Verify we're linked to Scheduler
echo ""
echo "✅ Verifying service link..."
railway status

echo ""
echo "📝 Reading .env file..."

# Read .env and set variables (skip PUBLIC_URL_BASE - Railway auto-detects)
while IFS='=' read -r key value; do
    # Skip comments, empty lines, and PUBLIC_URL_BASE
    if [[ $key =~ ^#.*$ ]] || [[ -z $key ]] || [[ $key == "PUBLIC_URL_BASE" ]]; then
        continue
    fi
    
    # Remove leading/trailing whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)
    
    # Skip if value is empty
    if [[ -z $value ]]; then
        continue
    fi
    
    echo "   ✅ Setting $key"
    railway variables --set "$key=$value" || echo "   ⚠️  Failed to set $key"
done < .env

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Environment variables synced to Scheduler service!"
echo ""
echo "🔄 Railway will automatically redeploy with new variables"
echo "🌐 Your app: https://scheduler-production-cd0b.up.railway.app"
echo ""
