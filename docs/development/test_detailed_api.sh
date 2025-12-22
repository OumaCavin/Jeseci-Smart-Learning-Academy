#!/bin/bash

echo "🔍 Detailed JAC API Testing"

# Start server
jac serve learning_portal_foundation.jir > detailed_server.log 2>&1 &
SERVER_PID=$!
sleep 3

echo "📡 Testing walker details..."

# Get walker info
echo "1️⃣ Getting walker details..."
curl -s http://localhost:8000/walker/welcome_system | jq '.' 

echo ""
echo "2️⃣ Getting function details..."
curl -s http://localhost:8000/functions | jq '.'

echo ""
echo "3️⃣ Testing with POST to function endpoint..."
curl -s -X POST http://localhost:8000/function/welcome_system \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'

echo ""
echo "4️⃣ Testing with parameters..."
curl -s -X POST http://localhost:8000/walker/manage_learning_concepts \
  -H "Content-Type: application/json" \
  -d '{"action": "list_concepts", "concept_id": "test"}' | jq '.'

# Check server log
echo ""
echo "📋 Checking server log..."
tail -10 detailed_server.log

# Kill server
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo "✅ Detailed testing completed!"