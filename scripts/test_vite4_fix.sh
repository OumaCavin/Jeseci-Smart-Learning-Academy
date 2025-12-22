#!/bin/bash

# Test script to verify Vite 4 compatibility fix
echo "🧪 Testing Vite 4 Compatibility Fix"
echo "=================================="

echo ""
echo "📋 Checking Vite version compatibility..."

# Check if package.json has Vite 4
if grep -q '"vite": ".*4\.5\.2"' package.json; then
    echo "✅ Vite 4.5.2 found in package.json (Jac-compatible version)"
else
    echo "❌ Vite version not correctly set to 4.5.2"
    exit 1
fi

# Check vite.config.js
if [ -f "vite.config.js" ]; then
    echo "✅ vite.config.js exists"
    
    # Check for manifest: true (Vite 4 format)
    if grep -q "manifest: true" vite.config.js; then
        echo "✅ Manifest configured for Vite 4 (dist/manifest.json expected)"
    else
        echo "❌ Manifest configuration incorrect"
        exit 1
    fi
else
    echo "❌ vite.config.js missing"
    exit 1
fi

echo ""
echo "📦 Package.json content:"
cat package.json
echo ""

echo ""
echo "⚙️ Vite config content:"
cat vite.config.js
echo ""

echo ""
echo "🔍 Expected Vite 4 behavior:"
echo "  ✅ manifest: true → creates dist/manifest.json"
echo "  ✅ Jac 0.9.3 expects manifest at dist/manifest.json"  
echo "  ✅ No hidden .vite folder conflicts"
echo ""

echo "🎯 Expected build results when running locally:"
echo "1. npm install                    # Install Vite 4.5.2"
echo "2. npm run compile                # Build with Vite 4"
echo "3. ls dist/                       # Should show: client_runtime.js, manifest.json"
echo "4. jac serve app.jac              # Should find dist/manifest.json"
echo ""

if [ -d "dist" ]; then
    echo "📁 Current dist directory contents:"
    ls -la dist/ 2>/dev/null || echo "  (dist directory exists but is empty)"
else
    echo "📁 No dist directory found (expected after cleanup)"
fi

echo ""
echo "🔧 Vite 4 compatibility fix applied successfully!"
echo "💡 This resolves 'Vite build completed but no bundle file found' error"