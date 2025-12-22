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

echo -e "\n${BLUE}🗄️  Database Setup for Jeseci Smart Learning Companion${NC}\n"

# Change to project root
cd "$(dirname "$0")/../.."

# Load environment variables if .env exists
if [ -f ".env" ]; then
    print_info "Loading environment variables from .env..."
    set -a  # Auto-export variables
    source .env
    set +a
fi

# =============================================================================
# PostgreSQL Setup
# =============================================================================
echo -e "\n${BLUE}Setting up PostgreSQL...${NC}\n"

# Check if psql is available
if command -v psql &> /dev/null; then
    print_status "psql found: $(which psql)"
    
    # Try to connect to the database directly
    print_info "Setting up PostgreSQL database '$POSTGRES_DB'..."
    
    # Try to create database if it doesn't exist
    if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $POSTGRES_DB;" 2>/dev/null; then
        print_status "Database '$POSTGRES_DB' created successfully"
    else
        print_status "Database '$POSTGRES_DB' already exists or will be used"
    fi
    
    # Test connection to the database
    if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" 2>/dev/null; then
        print_status "PostgreSQL connection successful"
    else
        print_warning "Could not connect to database - tables may already exist or will be created by app"
    fi
        
        # Create tables
        print_info "Running database migrations..."
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
            print_status "Database tables created successfully"
        else:
            print_warning "Table creation may have issues"
"
        
    else
        print_warning "PostgreSQL is not running or credentials are incorrect"
        print_info "To start PostgreSQL:"
        print_info "  - Linux: sudo systemctl start postgresql"
        print_info "  - macOS: brew services start postgresql"
        print_info "  - Docker: docker run -d --name postgres -e POSTGRES_PASSWORD=secret -p 5432:5432 postgres"
    fi
else
    print_warning "psql command not found"
    print_info "Please install PostgreSQL client tools or use Docker"
fi

# =============================================================================
# Neo4j Setup
# =============================================================================
echo -e "\n${BLUE}Setting up Neo4j...${NC}\n"

# Check if Neo4j tools are available
if command -v cypher-shell &> /dev/null; then
    print_status "cypher-shell found: $(which cypher-shell)"
    
    # Try to connect to Neo4j
    if echo "RETURN 1;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" &> /dev/null; then
        print_status "Neo4j connection successful"
        
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
    print_status 'Neo4j constraints created successfully')
else:
    print_warning('Constraint creation may have issues')
"
        
    else
        print_warning "Neo4j is not running or credentials are incorrect"
        print_info "To start Neo4j:"
        print_info "  - Docker: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j"
        print_info "  - Download: https://neo4j.com/download/"
    fi
else
    print_warning "cypher-shell command not found"
    print_info "Neo4j may still be accessible via Python driver"
fi

# =============================================================================
# Summary
# =============================================================================
echo -e "\n${BLUE}📊 Database Setup Summary${NC}\n"

echo "Configuration:"
echo "  PostgreSQL: $POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
echo "  Neo4j: $NEO4J_URI ($NEO4J_DATABASE)"
echo ""

echo "Next steps:"
echo "  1. Run seed data scripts to populate initial content"
echo "  2. Start the backend: jac serve backend/app.jac"
echo "  3. Access the API at http://localhost:8000"
echo ""

print_status "Database setup complete!"
