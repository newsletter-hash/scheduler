#!/bin/bash
# Build React frontend for production and set USE_REACT=true

cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🔨 Building React frontend..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build complete! Files in frontend/dist/"
    echo ""
    echo "To use React frontend, set USE_REACT=true in your environment"
    echo "  export USE_REACT=true"
    echo "  ./run_local.sh"
    echo ""
    echo "Or add USE_REACT=true to your .env file or Railway environment variables"
else
    echo "❌ Build failed"
    exit 1
fi
