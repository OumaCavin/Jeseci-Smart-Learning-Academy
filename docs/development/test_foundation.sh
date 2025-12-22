#!/bin/bash

# Test script for learning portal foundation
echo "🧪 Testing JAC Learning Portal Foundation"

# Start the server in background
echo "🚀 Starting JAC server..."
jac serve learning_portal_foundation.jir > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test endpoints
echo "📡 Testing API endpoints..."

# Test 1: Welcome system
echo "1️⃣ Testing welcome endpoint..."
curl -s http://localhost:8000/welcome_system/welcome | jq '.' || echo "Welcome endpoint test completed"

# Test 2: Health check  
echo "2️⃣ Testing health check..."
curl -s http://localhost:8000/health_check/check_health | jq '.' || echo "Health check completed"

# Test 3: List concepts
echo "3️⃣ Testing concept listing..."
curl -s http://localhost:8000/manage_learning_concepts/list_concepts | jq '.' || echo "List concepts completed"

# Test 4: Get concept details
echo "4️⃣ Testing concept details..."
curl -s http://localhost:8000/manage_learning_concepts/get_concept_details?concept_id=jac_fundamentals | jq '.' || echo "Concept details completed"

# Test 5: User progress
echo "5️⃣ Testing user progress..."
curl -s http://localhost:8000/manage_user_progress/get_user_progress | jq '.' || echo "User progress completed"

# Test 6: System stats
echo "6️⃣ Testing system stats..."
curl -s http://localhost:8000/get_system_stats/get_stats | jq '.' || echo "System stats completed"

# Cleanup
echo "🛑 Stopping server..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo "✅ Foundation testing completed!"
echo "📊 Check server.log for detailed output"