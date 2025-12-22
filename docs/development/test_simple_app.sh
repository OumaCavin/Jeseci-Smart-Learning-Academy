#!/bin/bash

echo "🧪 Testing Simple App to understand spawning behavior"

# Start server
jac serve simple_app.jir > simple_server.log 2>&1 &
SERVER_PID=$!
sleep 3

echo "📡 Testing simple app walkers..."

# Test hello_world walker
echo "1️⃣ Testing hello_world..."
curl -s -X POST http://localhost:8000/walker/hello_world \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'

# Test get_concepts walker
echo "2️⃣ Testing get_concepts..."
curl -s -X POST http://localhost:8000/walker/get_concepts \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'

# Test health_check walker
echo "3️⃣ Testing health_check..."
curl -s -X POST http://localhost:8000/walker/health_check \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.'

# List walkers
echo "4️⃣ Listing walkers..."
curl -s http://localhost:8000/walkers | jq '.'

# Kill server
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo "✅ Simple app test completed!"