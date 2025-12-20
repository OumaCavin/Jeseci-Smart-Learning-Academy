#!/bin/bash

echo "🧪 Testing JAC API Endpoints"
echo "=============================="

# Start server in background
echo "🚀 Starting JAC server..."
cd /workspace
source venv/bin/activate
jac serve simple_app.jac &
SERVER_PID=$!

# Wait for server to start
sleep 5

echo ""
echo "📡 Testing endpoints..."

# Test 1: Hello World
echo "1. Testing hello_world endpoint..."
curl -s -X POST http://localhost:8000/walker/hello_world | jq '.' || echo "hello_world endpoint test completed"

echo ""
echo "2. Testing get_concepts endpoint..."
curl -s -X POST http://localhost:8000/walker/get_concepts | jq '.' || echo "get_concepts endpoint test completed"

echo ""
echo "3. Testing health_check endpoint..."
curl -s -X POST http://localhost:8000/walker/health_check | jq '.' || echo "health_check endpoint test completed"

echo ""
echo "4. Listing available walkers..."
curl -s http://localhost:8000/walkers | jq '.' || echo "List walkers completed"

# Clean up
echo ""
echo "🛑 Stopping server..."
kill $SERVER_PID 2>/dev/null

echo ""
echo "✅ API testing completed!"