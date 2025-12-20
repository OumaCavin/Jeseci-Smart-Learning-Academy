#!/bin/bash

# Test script for Phase 2 agent files
echo "Testing Phase 2 agent files compilation..."

agent_files=(
    "services/quiz_master.jac"
    "services/evaluator.jac"
    "services/progress_tracker.jac"
    "services/motivator.jac"
    "services/base_agent.jac"
    "services/multi_agent_chat.jac"
    "services/ai_processing_agent.jac"
    "services/system_orchestrator.jac"
    "services/content_curator.jac"
)

for file in "${agent_files[@]}"; do
    echo "Testing $file..."
    timeout 10s jac check "$file"
    if [ $? -eq 0 ]; then
        echo "✓ $file - SUCCESS"
    else
        echo "✗ $file - FAILED"
    fi
    echo "---"
done

echo "Testing completed."