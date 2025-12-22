#!/bin/bash

# Test script to verify the frontend fix
echo "🧪 Testing JAC Frontend Configuration Fix"
echo "=========================================="

echo ""
echo "📋 Checking configuration files..."

# Check if required files exist
if [ -f "package.json" ]; then
    echo "✅ package.json exists"
else
    echo "❌ package.json missing"
    exit 1
fi

if [ -f "vite.config.js" ]; then
    echo "✅ vite.config.js exists"
    
    # Check if manifest is enabled
    if grep -q "manifest" vite.config.js; then
        echo "✅ Manifest configuration found in vite.config.js"
    else
        echo "❌ Manifest configuration missing"
        exit 1
    fi
else
    echo "❌ vite.config.js missing"
    exit 1
fi

if [ -f "src/client_runtime.js" ]; then
    echo "✅ src/client_runtime.js exists"
else
    echo "❌ src/client_runtime.js missing"
    exit 1
fi

echo ""
echo "📦 Checking package.json dependencies..."

# Check for required dependencies
if grep -q '"react"' package.json; then
    echo "✅ React dependency found"
else
    echo "❌ React dependency missing"
    exit 1
fi

if grep -q '"vite"' package.json; then
    echo "✅ Vite dependency found"
else
    echo "❌ Vite dependency missing"
    exit 1
fi

echo ""
echo "🔧 Configuration test complete!"
echo ""
echo "🚀 To test the fix locally:"
echo "1. Run: npm install"
echo "2. Run: jac serve app.jac"
echo "3. Visit: http://localhost:8000/page/app"
echo ""
echo "The 503 error should now be resolved!"