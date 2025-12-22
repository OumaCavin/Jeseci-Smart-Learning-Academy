#!/bin/bash

echo "🎯 Testing JAC Walkers with Explicit Spawn Node"

# Start server
jac serve learning_portal_foundation.jir > spawn_server.log 2>&1 &
SERVER_PID=$!
sleep 3

echo "📡 Testing walkers with spawn node specification..."

# Test 1: Welcome system with explicit root spawn
echo "1️⃣ Testing welcome_system with root spawn..."
curl -s -X POST http://localhost:8000/walker/welcome_system \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root"}' | jq '.'

echo ""
echo "2️⃣ Testing health_check with root spawn..."
curl -s -X POST http://localhost:8000/walker/health_check \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root"}' | jq '.'

echo ""
echo "3️⃣ Testing manage_learning_concepts with root spawn..."
curl -s -X POST http://localhost:8000/walker/manage_learning_concepts \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root", "action": "list_concepts"}' | jq '.'

echo ""
echo "4️⃣ Testing manage_learning_concepts concept details..."
curl -s -X POST http://localhost:8000/walker/manage_learning_concepts \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root", "action": "get_concept_details", "concept_id": "jac_fundamentals"}' | jq '.'

echo ""
echo "5️⃣ Testing manage_user_progress with root spawn..."
curl -s -X POST http://localhost:8000/walker/manage_user_progress \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root", "action": "get_user_progress"}' | jq '.'

echo ""
echo "6️⃣ Testing get_system_stats with root spawn..."
curl -s -X POST http://localhost:8000/walker/get_system_stats \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root"}' | jq '.'

# Kill server
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo ""
echo "✅ Spawn node testing completed!"