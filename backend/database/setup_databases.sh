#!/bin/bash
# =============================================================================
# Database Setup Script for Jeseci Smart Learning Companion
# =============================================================================
# This script sets up PostgreSQL and Neo4j databases for the application.
# Author: Cavin Otieno
# =============================================================================

set -e  # Exit on error

# Colors for output (using printf-friendly format)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

print_status() {
    printf "${GREEN}[OK]${NC} %s\n" "$1"
}

print_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1"
}

print_warning() {
    printf "${YELLOW}[WARNING]${NC} %s\n" "$1"
}

print_info() {
    printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

print_section() {
    printf "\n${CYAN}============================================================${NC}\n"
    printf "${CYAN} %s ${NC}\n" "$1"
    printf "${CYAN}============================================================${NC}\n\n"
}

print_step() {
    printf "${MAGENTA}->${NC} %s\n" "$1"
}

print_header() {
    printf "\n${BLUE}DATABASE SETUP FOR JESECI SMART LEARNING COMPANION${NC}\n\n"
}

print_header

# Change to project root
cd "$(dirname "$0")/../.."

# Load environment variables if .env exists
# Check backend/config/ directory first, then fall back to project root
ENV_FILE="backend/config/.env"
if [ -f "$ENV_FILE" ]; then
    print_info "Loading environment variables from $ENV_FILE..."
    set -a  # Auto-export variables
    source "$ENV_FILE"
    set +a
else
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
        POSTGRES_USER="jeseci_academy_user"
        POSTGRES_PASSWORD="jeseci_secure_password_2024"
        DB_SCHEMA="jeseci_academy"
        PG_SUPERUSER="postgres"
        NEO4J_URI="bolt://localhost:7687"
        NEO4J_USER="neo4j"
        NEO4J_PASSWORD="neo4j_secure_password_2024"
        NEO4J_DATABASE="neo4j"
    fi
fi

# =============================================================================
# PostgreSQL Setup
# =============================================================================
print_section "PostgreSQL Database Setup"

# Check if psql is available
if command -v psql &> /dev/null; then
    print_status "psql found: $(which psql)"
    
    print_info "Target configuration (from .env):"
    printf "  ${CYAN}Host:${NC}     %s:%s\n" "$POSTGRES_HOST" "$POSTGRES_PORT"
    printf "  ${CYAN}Database:${NC} %s\n" "$POSTGRES_DB"
    printf "  ${CYAN}User:${NC}     %s\n" "$POSTGRES_USER"
    printf "\n"
    
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
        printf "\n"
        print_info "To start PostgreSQL service:"
        printf "\n"
        printf "  ${CYAN}Ubuntu/Debian:${NC}  sudo systemctl start postgresql\n"
        printf "  ${CYAN}CentOS/RHEL:${NC}    sudo systemctl start postgresql\n"
        printf "  ${CYAN}macOS:${NC}          brew services start postgresql\n"
        printf "  ${CYAN}Windows:${NC}        Start PostgreSQL from Services\n"
        printf "\n"
    fi
    
    if [ "$PG_RUNNING" = true ]; then
        # Try to connect with configured user
        print_info "Attempting connection with configured user '$POSTGRES_USER'..."
        
        if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" &>/dev/null; then
            print_status "PostgreSQL connection successful!"
        else
            print_error "Could not connect as user '$POSTGRES_USER' to database '$POSTGRES_DB'"
            print_warning "This usually means:"
            printf "  1. The user '%s' doesn't exist yet, OR\n" "$POSTGRES_USER"
            printf "  2. The password for user '%s' doesn't match POSTGRES_PASSWORD in .env\n" "$POSTGRES_USER"
            printf "\n"
            print_info "If the user already exists with a different password, recreate it with:"
            printf "  ${CYAN}sudo -u postgres psql -c \"DROP USER IF EXISTS %s;\"${NC}\n" "$POSTGRES_USER"
            printf "\n"
            
            print_section "Creating PostgreSQL User and Database"
            print_info "Using configuration values from your .env file..."
            printf "\n"
            
            # Try to create user and database automatically
            # Note: CREATE USER can be in DO block, but CREATE DATABASE cannot
            print_info "Attempting to create user and database automatically..."
            printf "\n"
            
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
            
            # Step 3: Grant privileges on database and schema
            sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;" 2>/dev/null || true
            sudo -u postgres psql -c "GRANT ALL ON SCHEMA public TO $POSTGRES_USER;" 2>/dev/null || true
            
            # Create and grant permissions on the custom schema
            sudo -u postgres psql -d "$POSTGRES_DB" -c "CREATE SCHEMA IF NOT EXISTS $DB_SCHEMA AUTHORIZATION $POSTGRES_USER;" 2>/dev/null || true
            sudo -u postgres psql -d "$POSTGRES_DB" -c "GRANT ALL ON SCHEMA $DB_SCHEMA TO $POSTGRES_USER;" 2>/dev/null || true
            sudo -u postgres psql -d "$POSTGRES_DB" -c "ALTER SCHEMA $DB_SCHEMA OWNER TO $POSTGRES_USER;" 2>/dev/null || true
            sudo -u postgres psql -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA $DB_SCHEMA GRANT ALL ON TABLES TO $POSTGRES_USER;" 2>/dev/null || true
            sudo -u postgres psql -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA $DB_SCHEMA GRANT ALL ON SEQUENCES TO $POSTGRES_USER;" 2>/dev/null || true
            sudo -u postgres psql -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA $DB_SCHEMA GRANT ALL ON FUNCTIONS TO $POSTGRES_USER;" 2>/dev/null || true
            
            # Transfer ownership of the schema to the application user
            # This is critical - without ownership, the user cannot create tables even with GRANT ALL
            
            printf "\n"
            
            # Show manual SQL commands as backup if auto-creation failed
            if [ "$USER_CREATED" = false ] || [ "$DB_CREATED" = false ]; then
                print_step "Manual SQL Commands (if auto-creation failed):"
                printf "    ${CYAN}sudo -u postgres psql${NC}\n"
                printf "\n"
                printf "    ${CYAN}-- Create user using POSTGRES_USER and POSTGRES_PASSWORD from .env${NC}\n"
                printf "    ${GREEN}CREATE USER %s WITH PASSWORD '%s';${NC}\n" "$POSTGRES_USER" "$POSTGRES_PASSWORD"
                printf "\n"
                printf "    ${CYAN}-- Create database using POSTGRES_DB from .env${NC}\n"
                printf "    ${GREEN}CREATE DATABASE %s OWNER %s;${NC}\n" "$POSTGRES_DB" "$POSTGRES_USER"
                printf "\n"
                printf "    ${CYAN}-- Grant privileges${NC}\n"
                printf "    ${GREEN}GRANT ALL PRIVILEGES ON DATABASE %s TO %s;${NC}\n" "$POSTGRES_DB" "$POSTGRES_USER"
                printf "    ${GREEN}CREATE SCHEMA %s AUTHORIZATION %s;${NC}\n" "$DB_SCHEMA" "$POSTGRES_USER"
                printf "\n"
                printf "    ${CYAN}-- Exit psql${NC}\n"
                printf "    ${GREEN}\\q${NC}\n"
                printf "\n"
            fi
        fi
        
        # Test final connection
        print_section "Testing PostgreSQL Connection"
        if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1 AS connection_test;" &>/dev/null; then
            print_status "PostgreSQL connection successful!"
            
            # Show database tables
            print_section "PostgreSQL Tables"
            print_info "Checking for existing tables in '$POSTGRES_DB'..."
            printf "\n"
            
            TABLES=$(PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = '$DB_SCHEMA' ORDER BY table_name;" 2>/dev/null)
            
            if [ -n "$TABLES" ]; then
                printf "${GREEN}Existing tables in database:${NC}\n"
                echo "$TABLES" | while read -r table; do
                    table=$(echo "$table" | xargs)
                    if [ -n "$table" ]; then
                        printf "  ${GREEN}[OK]${NC} %s\n" "$table"
                    fi
                done
                printf "\n"
            else
                print_info "No tables found in database (tables will be created by application)"
            fi
            
            # Run table creation using centralized database initialization script
            print_section "Creating Database Tables"
            print_info "Running database initialization script..."
            printf "\n"

            # Drop existing schema objects to fix duplicate index errors (first-time setup only)
            print_info "Dropping existing schema '$DB_SCHEMA' to fix any duplicate objects..."
            sudo -u "$PG_SUPERUSER" psql -d "$POSTGRES_DB" -c "DROP SCHEMA IF EXISTS $DB_SCHEMA CASCADE;" 2>/dev/null || true

            # Create the schema fresh
            print_info "Creating schema '$DB_SCHEMA'..."
            sudo -u "$PG_SUPERUSER" psql -d "$POSTGRES_DB" -c "CREATE SCHEMA $DB_SCHEMA;" 2>/dev/null || true
            sudo -u "$PG_SUPERUSER" psql -d "$POSTGRES_DB" -c "GRANT ALL ON SCHEMA $DB_SCHEMA TO $POSTGRES_USER;" 2>/dev/null || true
            sudo -u "$PG_SUPERUSER" psql -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA $DB_SCHEMA GRANT ALL ON TABLES TO $POSTGRES_USER;" 2>/dev/null || true
            sudo -u "$PG_SUPERUSER" psql -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA $DB_SCHEMA GRANT ALL ON SEQUENCES TO $POSTGRES_USER;" 2>/dev/null || true

            # Use the centralized database initialization script
            print_step "Executing Python initialization..."
            
            # Run directly so output streams to console immediately
            python3 -c "
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
from database.initialize_database import initialize_database

try:
    success = initialize_database()
    if success:
        print('')
        print('[OK] All database tables created successfully!')
    else:
        print('[!] Some tables may not have been created')
        sys.exit(1)
except Exception as e:
    print(f'[!] Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

            # Check exit code of the previous command directly
            if [ $? -ne 0 ]; then
                printf "\n"
                print_error "Failed to create database tables"
                exit 1
            fi

            printf "\n"
            print_status "PostgreSQL setup completed successfully"
            
        else
            print_error "Could not connect to database '$POSTGRES_DB'"
            print_warning "Please create the user and database manually:"
            printf "\n"
            print_step "Step 1: Log in as PostgreSQL superuser"
            printf "    ${CYAN}sudo -u postgres psql${NC}\n"
            printf "\n"
            print_step "Step 2: Run these SQL commands (using values from your .env):"
            printf "\n"
            printf "    ${CYAN}-- Create user (using POSTGRES_USER and POSTGRES_PASSWORD)${NC}\n"
            printf "    ${GREEN}CREATE USER %s WITH PASSWORD '%s';${NC}\n" "$POSTGRES_USER" "$POSTGRES_PASSWORD"
            printf "\n"
            printf "    ${CYAN}-- Create database (using POSTGRES_DB)${NC}\n"
            printf "    ${GREEN}CREATE DATABASE %s OWNER %s;${NC}\n" "$POSTGRES_DB" "$POSTGRES_USER"
            printf "\n"
            printf "    ${CYAN}-- Grant privileges${NC}\n"
            printf "    ${GREEN}GRANT ALL PRIVILEGES ON DATABASE %s TO %s;${NC}\n" "$POSTGRES_DB" "$POSTGRES_USER"
            printf "    ${GREEN}GRANT ALL ON SCHEMA public TO %s;${NC}\n" "$POSTGRES_USER"
            printf "\n"
            printf "    ${CYAN}-- Exit psql${NC}\n"
            printf "    ${GREEN}\\q${NC}\n"
            printf "\n"
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
    printf "  ${CYAN}URI:${NC}       %s\n" "$NEO4J_URI"
    printf "  ${CYAN}Database:${NC} %s\n" "$NEO4J_DATABASE"
    printf "  ${CYAN}User:${NC}     %s\n" "$NEO4J_USER"
    printf "\n"
    
    # Try to connect to Neo4j
    print_info "Testing Neo4j connection..."
    NEO4J_RESULT=$(echo "RETURN 1 AS test;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" 2>&1)
    NEO4J_EXIT=$?
    
    if echo "$NEO4J_RESULT" | grep -q "1 row\|test" && [ $NEO4J_EXIT -eq 0 ]; then
        print_status "Neo4j connection successful!"
        printf "\n"
        
        # Show existing nodes
        print_info "Querying Neo4j for existing nodes..."
        printf "\n"
        
        NODE_COUNT=$(echo "MATCH (n) RETURN count(n) AS count;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" 2>/dev/null | grep -E "^[0-9]+" | head -1 || echo "0")
        
        if [ "$NODE_COUNT" -gt 0 ] 2>/dev/null; then
            print_status "Found $NODE_COUNT nodes in Neo4j database"
        else
            print_info "No nodes found in database (will be created by application)"
        fi
        
        printf "\n"
        
        # Create constraints and indexes using the Neo4j manager
        print_info "Creating Neo4j constraints and indexes..."
        python -c "
import sys
sys.path.insert(0, 'backend')
from database.neo4j_manager import Neo4jManager

# Create Neo4j manager instance
neo4j = Neo4jManager()

# Connect to Neo4j
if neo4j.connect():
    # Create constraints
    constraint_count = neo4j.create_constraints()
    print(f'[✓] Created {constraint_count} constraints')
    
    # Create indexes
    index_count = neo4j.create_indexes()
    print(f'[✓] Created {index_count} indexes')
    
    # Verify setup
    setup = neo4j.verify_setup()
    print(f'[✓] Neo4j setup verified: {setup[\"concept_count\"]} concepts, ' 
          f'{setup[\"learning_path_count\"]} learning paths, '
          f'{setup[\"lesson_count\"]} lessons, '
          f'{setup[\"user_count\"]} users, '
          f'{setup[\"relationship_count\"]} relationships')
    
    neo4j.disconnect()
    print('[OK] Neo4j constraints and indexes created successfully')
else:
    print('[!] Could not connect to Neo4j to create constraints')
"
        
        printf "\n"
        print_status "Neo4j setup completed successfully"
        
    else
        print_error "Neo4j connection failed despite appearing to run"
        print_warning "Check credentials in .env file"
    fi
    
else
    print_error "Neo4j is not running!"
    print_warning "Please start Neo4j using one of these methods:"
    printf "\n"
    
    print_step "Option 1: Neo4j Desktop (Recommended for Development)"
    printf "  1. Download from: https://neo4j.com/download/\n"
    printf "  2. Install and open Neo4j Desktop\n"
    printf "  3. Create a new database\n"
    printf "  4. Set password to: %s\n" "$NEO4J_PASSWORD"
    printf "  5. Update .env if connection details differ\n"
    printf "\n"
    
    print_step "Option 2: System Service (Linux)"
    printf "  ${CYAN}sudo systemctl start neo4j${NC}\n"
    printf "  ${CYAN}sudo systemctl enable neo4j${NC}  # Auto-start on boot\n"
    printf "\n"
    
    print_step "Option 3: Manual Installation (Linux)"
    printf "  # Download Neo4j Community Edition\n"
    printf "  wget https://neo4j.com/artifact.php?name=neo4j-community-5.14.0-linux.tar.gz\n"
    printf "  tar -xzf neo4j-community-5.14.0-linux.tar.gz\n"
    printf "  cd neo4j-community-5.14.0\n"
    printf "\n"
    printf "  # Configure in conf/neo4j.conf:\n"
    printf "  dbms.connector.http.listen_address=:7474\n"
    printf "  dbms.connector.bolt.listen_address=:7687\n"
    printf "  dbms.security.auth_enabled=true\n"
    printf "\n"
    printf "  # Start Neo4j\n"
    printf "  ./bin/neo4j start\n"
    printf "\n"
    
    print_step "Option 4: macOS (Homebrew)"
    printf "  ${CYAN}brew install neo4j${NC}\n"
    printf "  ${CYAN}brew services start neo4j${NC}\n"
    printf "\n"
    
    print_step "Option 5: Windows (Manual)"
    printf "  1. Download from: https://neo4j.com/download/\n"
    printf "  2. Run the installer\n"
    printf "  3. Start Neo4j from Start Menu\n"
    printf "  4. Set initial password to: %s\n" "$NEO4J_PASSWORD"
    printf "\n"
    
    print_info "After starting Neo4j, run this script again to verify connection."
fi

# =============================================================================
# Summary
# =============================================================================
print_section "DATABASE SETUP SUMMARY"

printf "Configuration (from .env):\n"
printf "  ${CYAN}PostgreSQL:${NC}  %s:%s/%s (user: %s)\n" "$POSTGRES_HOST" "$POSTGRES_PORT" "$POSTGRES_DB" "$POSTGRES_USER"
printf "  ${CYAN}Neo4j:${NC}       %s (database: %s)\n" "$NEO4J_URI" "$NEO4J_DATABASE"
printf "\n"
printf "${YELLOW}Note: Neo4j Community Edition uses a single database.${NC}\n"
printf "${YELLOW}Data is organized using labels (Concept, LearningPath, Lesson, etc.)${NC}\n"
printf "and relationship types (CONTAINS, PREREQUISITE, BELONGS_TO, etc.).\n"
printf "\n"

printf "Status:\n"
if command -v psql &> /dev/null && PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" &>/dev/null; then
    printf "  ${GREEN}[OK]${NC} %s: Connected\n" "$POSTGRES_DB"
else
    printf "  ${RED}[ERROR]${NC} %s: Not connected\n" "$POSTGRES_DB"
fi

if command -v cypher-shell &> /dev/null && echo "RETURN 1;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" &>/dev/null; then
    printf "  ${GREEN}[OK]${NC} Neo4j: Connected (using labels for data organization)\n"
else
    printf "  ${RED}[ERROR]${NC} Neo4j: Not connected\n"
fi

printf "\n"
printf "Next steps:\n"
printf "  1. ${CYAN}Ensure both databases are running and configured${NC}\n"
printf "  2. ${CYAN}Run seed data${NC} to populate initial content (if needed)\n"
printf "  3. ${CYAN}Start backend:${NC}    jac serve backend/app.jac\n"
printf "  4. ${CYAN}Access API:${NC}       http://localhost:8000\n"
printf "\n"

print_status "Database setup complete!"
