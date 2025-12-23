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
MAGENTA='\033[0;35m'
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

print_step() {
    echo -e "${MAGENTA}→${NC} $1"
}

echo -e "\n${BLUE}🗄️  Database Setup for Jeseci Smart Learning Companion${NC}\n"

# Change to project root
cd "$(dirname "$0")/../.."

# Load environment variables if .env exists
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    print_info "Loading environment variables from $ENV_FILE..."
    set -a  # Auto-export variables
    source "$ENV_FILE"
    set +a
else
    print_warning "$ENV_FILE file not found. Using default configuration."
    # Set defaults
    POSTGRES_HOST="localhost"
    POSTGRES_PORT="5432"
    POSTGRES_DB="jeseci_learning_academy"
    POSTGRES_USER="jeseci_user"
    POSTGRES_PASSWORD="secure_password_123"
    NEO4J_URI="bolt://localhost:7687"
    NEO4J_USER="neo4j"
    NEO4J_PASSWORD="neo4j_secure_password_2024"
    NEO4J_DATABASE="neo4j"
fi

# =============================================================================
# PostgreSQL Setup
# =============================================================================
print_section "PostgreSQL Database Setup"

# Check if psql is available
if command -v psql &> /dev/null; then
    print_status "psql found: $(which psql)"
    
    print_info "Target configuration (from .env):"
    echo "  ${CYAN}Host:${NC}     $POSTGRES_HOST:$POSTGRES_PORT"
    echo "  ${CYAN}Database:${NC} $POSTGRES_DB"
    echo "  ${CYAN}User:${NC}     $POSTGRES_USER"
    echo ""
    
    # First, check if PostgreSQL service is running
    print_info "Checking PostgreSQL service status..."
    PG_RUNNING=false
    
    # Check if we can connect as postgres user
    if sudo -u postgres psql -c "SELECT 1;" &>/dev/null; then
        PG_RUNNING=true
        print_status "PostgreSQL service is running"
    elif psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U postgres -c "SELECT 1;" &>/dev/null; then
        PG_RUNNING=true
        print_status "PostgreSQL service is running (accessible via network)"
    else
        print_warning "PostgreSQL service may not be running"
        echo ""
        print_info "To start PostgreSQL service:"
        echo ""
        echo "  ${CYAN}• Ubuntu/Debian:${NC}  sudo systemctl start postgresql"
        echo "  ${CYAN}• CentOS/RHEL:${NC}    sudo systemctl start postgresql"
        echo "  ${CYAN}• macOS:${NC}          brew services start postgresql"
        echo "  ${CYAN}• Windows:${NC}        Start PostgreSQL from Services"
        echo ""
    fi
    
    if [ "$PG_RUNNING" = true ]; then
        # Try to connect with configured user
        print_info "Attempting connection with configured user '$POSTGRES_USER'..."
        
        if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" &>/dev/null; then
            print_status "PostgreSQL connection successful!"
        else
            print_error "Could not connect as user '$POSTGRES_USER' to database '$POSTGRES_DB'"
            print_warning "This usually means:"
            echo "  1. The user '$POSTGRES_USER' doesn't exist yet, OR"
            echo "  2. The password for user '$POSTGRES_USER' doesn't match POSTGRES_PASSWORD in .env"
            echo ""
            print_info "If the user already exists with a different password, recreate it with:"
            echo "  ${CYAN}sudo -u postgres psql -c \"DROP USER IF EXISTS $POSTGRES_USER;\"${NC}"
            echo ""
            
            print_section "Creating PostgreSQL User and Database"
            print_info "Using configuration values from your .env file..."
            echo ""
            
            # Try to create user and database automatically
            # Note: CREATE USER can be in DO block, but CREATE DATABASE cannot
            print_info "Attempting to create user and database automatically..."
            echo ""
            
            # Step 1: Create user (using DO block)
            USER_CREATED=false
            if sudo -u postgres psql -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$POSTGRES_USER') THEN CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD'; END IF; END \$\$;" 2>/dev/null; then
                print_status "User '$POSTGRES_USER' created or already exists"
                USER_CREATED=true
            else
                print_warning "Could not create user. It may already exist or you lack permissions."
            fi
            
            # Step 2: Create database (separate command, cannot be in transaction block)
            DB_CREATED=false
            if sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB';" 2>/dev/null | grep -q 1; then
                print_info "Database '$POSTGRES_DB' already exists"
                DB_CREATED=true
            else
                if sudo -u postgres psql -c "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;" 2>/dev/null; then
                    print_status "Database '$POSTGRES_DB' created successfully"
                    DB_CREATED=true
                else
                    print_warning "Could not create database. It may already exist or you lack permissions."
                fi
            fi
            
            # Step 3: Grant privileges
            sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;" 2>/dev/null || true
            sudo -u postgres psql -c "GRANT ALL ON SCHEMA public TO $POSTGRES_USER;" 2>/dev/null || true
            
            echo ""
            
            # Show manual SQL commands as backup if auto-creation failed
            if [ "$USER_CREATED" = false ] || [ "$DB_CREATED" = false ]; then
                print_step "Manual SQL Commands (if auto-creation failed):"
                echo "    ${CYAN}sudo -u postgres psql${NC}"
                echo ""
                echo "    ${CYAN}-- Create user using POSTGRES_USER and POSTGRES_PASSWORD from .env${NC}"
                echo "    ${GREEN}CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';${NC}"
                echo ""
                echo "    ${CYAN}-- Create database using POSTGRES_DB from .env${NC}"
                echo "    ${GREEN}CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;${NC}"
                echo ""
                echo "    ${CYAN}-- Grant privileges${NC}"
                echo "    ${GREEN}GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;${NC}"
                echo "    ${GREEN}GRANT ALL ON SCHEMA public TO $POSTGRES_USER;${NC}"
                echo ""
                echo "    ${CYAN}-- Exit psql${NC}"
                echo "    ${GREEN}\\q${NC}"
                echo ""
            fi
        fi
        
        # Test final connection
        print_section "Testing PostgreSQL Connection"
        if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1 AS connection_test;" &>/dev/null; then
            print_status "PostgreSQL connection successful!"
            
            # Show database tables
            print_section "PostgreSQL Tables"
            print_info "Checking for existing tables in '$POSTGRES_DB'..."
            echo ""
            
            TABLES=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" 2>/dev/null)
            
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
                print_info "No tables found in database (tables will be created by application)"
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
            print_error "Could not connect to database '$POSTGRES_DB'"
            print_warning "Please create the user and database manually:"
            echo ""
            print_step "Step 1: Log in as PostgreSQL superuser"
            echo "    ${CYAN}sudo -u postgres psql${NC}"
            echo ""
            print_step "Step 2: Run these SQL commands (using values from your .env):"
            echo ""
            echo "    ${CYAN}-- Create user (using POSTGRES_USER and POSTGRES_PASSWORD)${NC}"
            echo "    ${GREEN}CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';${NC}"
            echo ""
            echo "    ${CYAN}-- Create database (using POSTGRES_DB)${NC}"
            echo "    ${GREEN}CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;${NC}"
            echo ""
            echo "    ${CYAN}-- Grant privileges${NC}"
            echo "    ${GREEN}GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;${NC}"
            echo "    ${GREEN}GRANT ALL ON SCHEMA public TO $POSTGRES_USER;${NC}"
            echo ""
            echo "    ${CYAN}-- Exit psql${NC}"
            echo "    ${GREEN}\\q${NC}"
            echo ""
        fi
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

# Check if Neo4j is running via different methods
neo4j_running=false

# Method 1: Check via cypher-shell
if command -v cypher-shell &> /dev/null; then
    if echo "RETURN 1;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" &>/dev/null; then
        neo4j_running=true
    fi
fi

# Method 2: Check via neo4j command
if command -v neo4j &> /dev/null; then
    if neo4j status &>/dev/null; then
        neo4j_running=true
    fi
fi

if [ "$neo4j_running" = true ]; then
    print_status "Neo4j is running and accessible"
    
    print_info "Target configuration (from .env):"
    echo "  ${CYAN}URI:${NC}       $NEO4J_URI"
    echo "  ${CYAN}Database:${NC} $NEO4J_DATABASE"
    echo "  ${CYAN}User:${NC}     $NEO4J_USER"
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
        
        NODE_COUNT=$(echo "MATCH (n) RETURN count(n) AS count;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" 2>/dev/null | grep -E "^[0-9]+" | head -1 || echo "0")
        
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
        print_error "Neo4j connection failed despite appearing to run"
        print_warning "Check credentials in .env file"
    fi
    
else
    print_error "Neo4j is not running!"
    print_warning "Please start Neo4j using one of these methods:"
    echo ""
    
    print_step "Option 1: Neo4j Desktop (Recommended for Development)"
    echo "  1. Download from: https://neo4j.com/download/"
    echo "  2. Install and open Neo4j Desktop"
    echo "  3. Create a new database"
    echo "  4. Set password to: $NEO4J_PASSWORD"
    echo "  5. Update .env if connection details differ"
    echo ""
    
    print_step "Option 2: System Service (Linux)"
    echo "  ${CYAN}sudo systemctl start neo4j${NC}"
    echo "  ${CYAN}sudo systemctl enable neo4j${NC}  # Auto-start on boot"
    echo ""
    
    print_step "Option 3: Manual Installation (Linux)"
    echo "  # Download Neo4j Community Edition"
    echo "  wget https://neo4j.com/artifact.php?name=neo4j-community-5.14.0-linux.tar.gz"
    echo "  tar -xzf neo4j-community-5.14.0-linux.tar.gz"
    echo "  cd neo4j-community-5.14.0"
    echo ""
    echo "  # Configure in conf/neo4j.conf:"
    echo "  dbms.connector.http.listen_address=:7474"
    echo "  dbms.connector.bolt.listen_address=:7687"
    echo "  dbms.security.auth_enabled=true"
    echo ""
    echo "  # Start Neo4j"
    echo "  ./bin/neo4j start"
    echo ""
    
    print_step "Option 4: macOS (Homebrew)"
    echo "  ${CYAN}brew install neo4j${NC}"
    echo "  ${CYAN}brew services start neo4j${NC}"
    echo ""
    
    print_step "Option 5: Windows (Manual)"
    echo "  1. Download from: https://neo4j.com/download/"
    echo "  2. Run the installer"
    echo "  3. Start Neo4j from Start Menu"
    echo "  4. Set initial password to: $NEO4J_PASSWORD"
    echo ""
    
    print_info "After starting Neo4j, run this script again to verify connection."
fi

# =============================================================================
# Summary
# =============================================================================
print_section "📊 Database Setup Summary"

echo "Configuration (from .env):"
echo "  ${CYAN}PostgreSQL:${NC}  $POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB (user: $POSTGRES_USER)"
echo "  ${CYAN}Neo4j:${NC}       $NEO4J_URI (database: $NEO4J_DATABASE)"
echo ""

echo "Status:"
if command -v psql &> /dev/null && PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" &>/dev/null; then
    echo "  ${GREEN}✓${NC} $POSTGRES_DB: Connected"
else
    echo "  ${RED}✗${NC} $POSTGRES_DB: Not connected"
fi

if command -v cypher-shell &> /dev/null && echo "RETURN 1;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" &>/dev/null; then
    echo "  ${GREEN}✓${NC} Neo4j: Connected"
else
    echo "  ${RED}✗${NC} Neo4j: Not connected"
fi

echo ""
echo "Next steps:"
echo "  1. ${CYAN}Ensure both databases are running and configured${NC}"
echo "  2. ${CYAN}Run seed data${NC} to populate initial content (if needed)"
echo "  3. ${CYAN}Start backend:${NC}    jac serve backend/app.jac"
echo "  4. ${CYAN}Access API:${NC}       http://localhost:8000"
echo ""

print_status "Database setup complete!"
