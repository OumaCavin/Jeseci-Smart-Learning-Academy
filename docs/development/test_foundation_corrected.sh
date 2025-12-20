#!/bin/bash

# Test script for learning portal foundation using correct JAC API format
echo "🧪 Testing JAC Learning Portal Foundation"

# Start the server in background
echo "🚀 Starting JAC server..."
jac serve learning_portal_foundation.jir > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Test endpoints using correct JAC API format
echo "📡 Testing API endpoints..."

# Test 1: Welcome system
echo "1️⃣ Testing welcome endpoint..."
curl -s -X POST http://localhost:8000/walker/welcome_system \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.' || echo "Welcome endpoint test completed"

# Test 2: Health check  
echo "2️⃣ Testing health check..."
curl -s -X POST http://localhost:8000/walker/health_check \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.' || echo "Health check completed"

# Test 3: List concepts
echo "3️⃣ Testing concept listing..."
curl -s -X POST http://localhost:8000/walker/manage_learning_concepts \
  -H "Content-Type: application/json" \
  -d '{"action": "list_concepts"}' | jq '.' || echo "List concepts completed"

# Test 4: Get concept details
echo "4️⃣ Testing concept details..."
curl -s -X POST http://localhost:8000/walker/manage_learning_concepts \
  -H "Content-Type: application/json" \
  -d '{"action": "get_concept_details", "concept_id": "jac_fundamentals"}' | jq '.' || echo "Concept details completed"

# Test 5: User progress
echo "5️⃣ Testing user progress..."
curl -s -X POST http://localhost:8000/walker/manage_user_progress \
  -H "Content-Type: application/json" \
  -d '{"action": "get_user_progress"}' | jq '.' || echo "User progress completed"

# Test 6: System stats
echo "6️⃣ Testing system stats..."
curl -s -X POST http://localhost:8000/walker/get_system_stats \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.' || echo "System stats completed"

# Test available walkers
echo "7️⃣ Listing available walkers..."
curl -s http://localhost:8000/walkers | jq '.' || echo "Walker listing completed"

# Cleanup
echo "🛑 Stopping server..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo "✅ Foundation testing completed!"
echo "📊 Check server.log for detailed output"