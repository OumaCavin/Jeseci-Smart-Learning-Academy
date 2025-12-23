#!/bin/bash
# =============================================================================
# Database Setup Script for Jeseci Smart Learning Companion
# =============================================================================
# This script sets up PostgreSQL and Neo4j databases for the application.
# Author: Cavin Otieno
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_section() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN} $1 ${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

echo -e "\n${BLUE}🗄️  Database Setup for Jeseci Smart Learning Companion${NC}\n"

# Change to project root
cd "$(dirname "$0")/../.."

# Load environment variables if .env exists
if [ -f ".env" ]; then
    print_info "Loading environment variables from .env..."
    set -a  # Auto-export variables
    source .env
    set +a
else
    print_warning ".env file not found. Using default configuration."
fi

# =============================================================================
# PostgreSQL Setup
# =============================================================================
print_section "PostgreSQL Database Setup"

# Check if psql is available
if command -v psql &> /dev/null; then
    print_status "psql found: $(which psql)"
    
    print_info "Connecting to PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
    print_info "Target database: $POSTGRES_DB"
    print_info "User: $POSTGRES_USER"
    echo ""
    
    # Try to create database if it doesn't exist
    print_info "Creating database '$POSTGRES_DB' if it doesn't exist..."
    if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $POSTGRES_DB;" 2>/dev/null; then
        print_status "Database '$POSTGRES_DB' created successfully"
    else
        print_info "Database '$POSTGRES_DB' already exists"
    fi
    
    # Test connection to the database
    print_section "Testing PostgreSQL Connection"
    if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1 AS connection_test;" 2>/dev/null; then
        print_status "PostgreSQL connection successful!"
        
        # Show database tables
        print_section "PostgreSQL Tables"
        print_info "Checking for existing tables in '$POSTGRES_DB'..."
        echo ""
        
        TABLES=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" 2>/dev/null)
        
        if [ -n "$TABLES" ]; then
            echo -e "${GREEN}Existing tables in database:${NC}"
            echo "$TABLES" | while read -r table; do
                table=$(echo "$table" | xargs)
                if [ -n "$table" ]; then
                    echo -e "  ${GREEN}✓${NC} $table"
                fi
            done
            echo ""
        else
            print_info "No tables found in database (tables will be created)"
        fi
        
        # Create tables
        print_section "Creating Database Tables"
        print_info "Running database migrations to create tables..."
        echo ""
        
        python -c "
import sys
sys.path.insert(0, 'backend')
from database import postgres_manager

# Create tables for the learning platform
tables = '''
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS concepts (
    concept_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    difficulty_level VARCHAR(50),
    description TEXT,
    lesson_content TEXT,
    lesson_generated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_paths (
    path_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    difficulty VARCHAR(50),
    estimated_duration INT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_path_concepts (
    id SERIAL PRIMARY KEY,
    path_id VARCHAR(50) REFERENCES learning_paths(path_id),
    concept_id VARCHAR(50) REFERENCES concepts(concept_id),
    sequence_order INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_concept_progress (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    concept_id VARCHAR(50) REFERENCES concepts(concept_id),
    progress_percent INT DEFAULT 0,
    mastery_level INT DEFAULT 0,
    time_spent_minutes INT DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    UNIQUE(user_id, concept_id)
);

CREATE TABLE IF NOT EXISTS user_learning_paths (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    path_id VARCHAR(50) REFERENCES learning_paths(path_id),
    progress_percent INT DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS achievements (
    achievement_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    criteria TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    achievement_id VARCHAR(50) REFERENCES achievements(achievement_id),
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    attempt_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    concept_id VARCHAR(50) REFERENCES concepts(concept_id),
    score INT,
    total_questions INT,
    time_taken_seconds INT,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

result = postgres_manager.execute_query(tables)
if result:
    print('[✓] All database tables created successfully')
else:
    print('[!] Table creation may have issues')
"
        
        echo ""
        print_status "PostgreSQL setup completed successfully"
        
    else
        print_error "Could not connect to PostgreSQL database"
        print_warning "Tables may already exist or will be created by the application"
        print_info ""
        print_info "To start PostgreSQL:"
        echo "  ${CYAN}• Linux:${NC}      sudo systemctl start postgresql"
        echo "  ${CYAN}• macOS:${NC}     brew services start postgresql"
        echo "  ${CYAN}• Docker:${NC}    docker run -d --name postgres -e POSTGRES_PASSWORD=secret -p 5432:5432 postgres"
        echo ""
    fi
        
else
    print_error "PostgreSQL client (psql) not found"
    print_info "Please install PostgreSQL to continue"
    print_info "Download: https://www.postgresql.org/download/"
fi

# =============================================================================
# Neo4j Setup
# =============================================================================
print_section "Neo4j Graph Database Setup"

# Check if Neo4j tools are available
if command -v cypher-shell &> /dev/null; then
    print_status "cypher-shell found: $(which cypher-shell)"
    
    print_info "Connecting to Neo4j at $NEO4J_URI..."
    print_info "Database: $NEO4J_DATABASE"
    print_info "User: $NEO4J_USER"
    echo ""
    
    # Try to connect to Neo4j
    print_info "Testing Neo4j connection..."
    NEO4J_RESULT=$(echo "RETURN 1 AS test;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" 2>&1)
    NEO4J_EXIT=$?
    
    if echo "$NEO4J_RESULT" | grep -q "1 row\|test" && [ $NEO4J_EXIT -eq 0 ]; then
        print_status "Neo4j connection successful!"
        echo ""
        
        # Show existing nodes
        print_info "Querying Neo4j for existing nodes..."
        echo ""
        
        NODE_COUNT=$(echo "MATCH (n) RETURN count(n) AS count;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" 2>/dev/null | grep -E "^[0-9]+$" | head -1 || echo "0")
        
        if [ "$NODE_COUNT" -gt 0 ] 2>/dev/null; then
            print_status "Found $NODE_COUNT nodes in Neo4j database"
        else
            print_info "No nodes found in database (will be created by application)"
        fi
        
        echo ""
        
        # Create constraints
        print_info "Creating Neo4j constraints..."
        python -c "
import sys
sys.path.insert(0, 'backend')
from database import neo4j_manager

constraints = '''
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (p:LearningPath) REQUIRE p.path_id IS UNIQUE;
'''

result = neo4j_manager.execute_query(constraints)
if result is not None:
    print('[✓] Neo4j constraints created successfully')
else:
    print('[!] Constraint creation may have issues')
"
        
        echo ""
        print_status "Neo4j setup completed successfully"
        
    else
        print_error "Neo4j connection failed!"
        print_warning "Neo4j is not running or credentials are incorrect"
        echo ""
        print_info "Please check your .env file for correct Neo4j credentials:"
        echo "  ${CYAN}NEO4J_URI:${NC}      $NEO4J_URI"
        echo "  ${CYAN}NEO4J_USER:${NC}     $NEO4J_USER"
        echo "  ${CYAN}NEO4J_PASSWORD:${NC} [configured]"
        echo "  ${CYAN}NEO4J_DATABASE:${NC} $NEO4J_DATABASE"
        echo ""
        print_info "To start Neo4j:"
        echo ""
        echo "  ${CYAN}Option 1 - Using Docker:${NC}"
        echo "    docker run -d --name neo4j \\"
        echo "      -p 7474:7474 -p 7687:7687 \\"
        echo "      -e NEO4J_AUTH=$NEO4J_USER/$NEO4J_PASSWORD \\"
        echo "      -e NEO4J_PLUGINS='[\"apoc\", \"graph-data-science\"]' \\"
        echo "      neo4j"
        echo ""
        echo "  ${CYAN}Option 2 - Desktop Download:${NC}"
        echo "    Download from: https://neo4j.com/download/"
        echo "    Start Neo4j Desktop and create a new database"
        echo ""
        echo "  ${CYAN}Option 3 - System Service (Linux):${NC}"
        echo "    sudo systemctl start neo4j"
        echo ""
        print_warning "After starting Neo4j, update .env with correct credentials if needed"
    fi
else
    print_error "cypher-shell command not found"
    print_info "Neo4j may still be accessible via Python driver"
    print_info ""
    print_info "To install cypher-shell:"
    echo "  ${CYAN}• Download:${NC} https://neo4j.com/download-center/"
    echo "  ${CYAN}• Docker:${NC} docker run --rm -it --entrypoint cypher-shell neo4j:$NEO4J_VERSION"
    echo ""
fi

# =============================================================================
# Summary
# =============================================================================
print_section "📊 Database Setup Summary"

echo "Configuration:"
echo "  ${CYAN}PostgreSQL:${NC}  $POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
echo "  ${CYAN}Neo4j:${NC}       $NEO4J_URI ($NEO4J_DATABASE)"
echo ""

echo "Next steps:"
echo "  1. ${CYAN}Run seed data${NC} to populate initial content (if needed)"
echo "  2. ${CYAN}Start backend:${NC}  jac serve backend/app.jac"
echo "  3. ${CYAN}Access API:${NC}     http://localhost:8000"
echo ""

print_status "Database setup complete!"
