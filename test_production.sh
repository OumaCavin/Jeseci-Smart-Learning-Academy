#!/bin/bash

echo "🧪 Testing JAC Learning Portal - Production Edition"

# Start server
jac serve learning_portal_production.jir > production_server.log 2>&1 &
SERVER_PID=$!
sleep 5

echo "📡 Testing production API endpoints..."

# Test 1: Production Welcome
echo "1️⃣ Testing production_welcome..."
curl -s -X POST http://localhost:8000/walker/production_welcome \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root"}' | jq '.' | head -20

echo ""
echo "2️⃣ Testing production_health_check..."
curl -s -X POST http://localhost:8000/walker/production_health_check \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root"}' | jq '.' | head -20

echo ""
echo "3️⃣ Testing production_concept_management (list)..."
curl -s -X POST http://localhost:8000/walker/production_concept_management \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root", "action": "list_production_concepts"}' | jq '.' | head -15

echo ""
echo "4️⃣ Testing production_concept_management (details)..."
curl -s -X POST http://localhost:8000/walker/production_concept_management \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root", "action": "get_concept_details", "concept_id": "jac_production_basics"}' | jq '.' | head -15

echo ""
echo "5️⃣ Testing production_learning_paths..."
curl -s -X POST http://localhost:8000/walker/production_learning_paths \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root", "action": "list_production_paths"}' | jq '.' | head -15

echo ""
echo "6️⃣ Testing production_user_progress..."
curl -s -X POST http://localhost:8000/walker/production_user_progress \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root", "action": "get_production_progress"}' | jq '.' | head -15

echo ""
echo "7️⃣ Testing production_analytics..."
curl -s -X POST http://localhost:8000/walker/production_analytics \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root"}' | jq '.' | head -15

echo ""
echo "8️⃣ Testing production_recommendations..."
curl -s -X POST http://localhost:8000/walker/production_recommendations \
  -H "Content-Type: application/json" \
  -d '{"_jac_spawn_node": "root"}' | jq '.' | head -15

# List all walkers
echo ""
echo "9️⃣ Listing all available walkers..."
curl -s http://localhost:8000/walkers | jq '.'

# Cleanup
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo ""
echo "✅ Production testing completed!"
echo "📊 Check production_server.log for detailed output"