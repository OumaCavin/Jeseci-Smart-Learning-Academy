#!/bin/bash
#
# Database Cleanup Script for Jeseci Smart Learning Academy
# This script removes all existing tables from PostgreSQL and Neo4j
# WARNING: This will delete all data in the databases!
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Database Cleanup Script for Jeseci Smart Learning Academy${NC}"
echo -e "${YELLOW}⚠️  WARNING: This will DELETE ALL DATA in the configured databases!${NC}"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables from .env file
if [ -f "$SCRIPT_DIR/../../backend/config/.env" ]; then
    source "$SCRIPT_DIR/../../backend/config/.env"
    echo -e "${GREEN}[✓] Loaded environment variables from .env${NC}"
elif [ -f "$SCRIPT_DIR/../../.env" ]; then
    source "$SCRIPT_DIR/../../.env"
    echo -e "${GREEN}[✓] Loaded environment variables from .env${NC}"
else
    echo -e "${RED}[✗] .env file not found${NC}"
    echo "Please ensure your .env file exists in the backend/config/ or project root directory"
    exit 1
fi

# Display current configuration
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE} Current Configuration ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  PostgreSQL:"
echo -e "    Host:     ${POSTGRES_HOST:-localhost}:${POSTGRES_PORT:-5432}"
echo -e "    Database: ${POSTGRES_DB:-jeseci_learning_academy}"
echo -e "    User:     ${POSTGRES_USER:-jeseci_academy_user}"
echo ""
echo -e "  Neo4j:"
echo -e "    URI:      ${NEO4J_URI:-bolt://localhost:7687}"
echo -e "    Database: ${NEO4J_DATABASE:-neo4j}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Confirmation
read -p "Do you want to proceed with cleanup? (type 'YES' to confirm): " confirmation
if [ "$confirmation" != "YES" ]; then
    echo -e "${YELLOW}[✓] Cleanup cancelled${NC}"
    exit 0
fi

echo ""

# =============================================================================
# PostgreSQL Cleanup
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE} PostgreSQL Database Cleanup ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if PostgreSQL service is running
if ! sudo -n pg_isready -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5432}" 2>/dev/null; then
    echo -e "${YELLOW}[i] Starting PostgreSQL service...${NC}"
    sudo service postgresql start 2>/dev/null || sudo systemctl start postgresql 2>/dev/null || true
    sleep 2
fi

# Get PostgreSQL superuser
PG_SUPERUSER="${PG_SUPERUSER:-postgres}"
PG_DATABASE="${POSTGRES_DB:-jeseci_learning_academy}"

echo -e "${YELLOW}[i] Dropping all tables from database '${PG_DATABASE}'...${NC}"

# Method 1: Drop schema and recreate (fastest)
if sudo -u "$PG_SUPERUSER" psql -d "$PG_DATABASE" -c "SELECT 1" 2>/dev/null; then
    echo -e "${YELLOW}[i] Using DROP SCHEMA method...${NC}"
    sudo -u "$PG_SUPERUSER" psql -d "$PG_DATABASE" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" 2>/dev/null
    echo -e "${GREEN}[✓] PostgreSQL database cleaned successfully${NC}"
else
    # Method 2: Drop tables individually (safer if schema method fails)
    echo -e "${YELLOW}[i] Using individual DROP TABLE method...${NC}"
    
    TABLES=(
        "system_logs" "user_badges" "badges" "user_achievements" "achievements"
        "quiz_attempts" "quizzes" "learning_sessions" "user_lesson_progress"
        "user_learning_paths" "user_concept_progress" "lesson_concepts"
        "learning_path_concepts" "lessons" "learning_paths" "concept_content"
        "concepts" "user_learning_preferences" "user_profile" "users"
        "system_health" "ai_agents"
    )
    
    for table in "${TABLES[@]}"; do
        sudo -u "$PG_SUPERUSER" psql -d "$PG_DATABASE" -c "DROP TABLE IF EXISTS $table CASCADE;" 2>/dev/null || true
    done
    echo -e "${GREEN}[✓] PostgreSQL tables dropped successfully${NC}"
fi

# Verify cleanup
TABLE_COUNT=$(sudo -u "$PG_SUPERUSER" psql -d "$PG_DATABASE" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)
echo -e "${GREEN}[✓] Remaining tables in database: $TABLE_COUNT${NC}"

echo ""

# =============================================================================
# Neo4j Cleanup
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE} Neo4j Graph Database Cleanup ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if Neo4j is running
NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-password}"
NEO4J_DATABASE="${NEO4J_DATABASE:-neo4j}"

# Try to connect to Neo4j and clean up project data
echo -e "${YELLOW}[i] Attempting to clean Neo4j project data...${NC}"

# Create a Python script for Neo4j cleanup using labels
python3 << 'PYTHON_SCRIPT'
import sys
import os
sys.path.insert(0, 'backend')

from database.neo4j_manager import Neo4jManager
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'config', '.env'))

try:
    neo4j = Neo4jManager()
    if neo4j.connect():
        # Clear only project-specific data using labels
        if neo4j.clear_project_data():
            print("[✓] Neo4j project data cleaned successfully")
            print("    (Preserves other data in the database using different labels)")
        else:
            print("[!] Failed to clear Neo4j data")
        neo4j.disconnect()
    else:
        print("[!] Could not connect to Neo4j")
        print("    (This is optional - Neo4j Community Edition uses a single database)")
        print("    (Project data is organized using labels, so existing data won't conflict)")
except Exception as e:
    print(f"[!] Neo4j cleanup skipped: {str(e)}")
    print("    (This is optional - Neo4j will work fine with existing data)")
PYTHON_SCRIPT

echo ""

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Database Cleanup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "  1. Run the setup script to create the new schema:"
echo -e "     ${GREEN}bash backend/database/setup_databases.sh${NC}"
echo ""
echo "  2. Make sure your virtual environment is up to date:"
echo -e "     ${GREEN}uv pip install -e backend/${NC}"
echo ""
echo -e "${YELLOW}⚠️  Remember to recreate any test users or data after setup${NC}"
echo ""
