#!/bin/bash
# =============================================================================
# Jeseci Smart Learning Academy - Complete Setup Script
# Pure JAC Architecture Setup with Database Creation
# Author: Cavin Otieno
# Date: December 20, 2025
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}🚀 $1${NC}\n"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if file exists
file_exists() {
    [ -f "$1" ]
}

# Function to check if directory exists
dir_exists() {
    [ -d "$1" ]
}

# Function to check if service is running
check_service() {
    if command_exists psql; then
        if psql -h localhost -U postgres -d postgres -c "SELECT 1" >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to create PostgreSQL database
create_postgres_db() {
    local db_name="$1"
    local db_user="$2"
    local db_password="$3"
    
    print_info "Creating PostgreSQL database: $db_name"
    
    # Try to create database
    if command_exists psql; then
        # Check if database exists
        if psql -h localhost -U "$db_user" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$db_name'" | grep -q 1; then
            print_warning "Database $db_name already exists"
            return 0
        fi
        
        # Create database
        if PGPASSWORD="$db_password" psql -h localhost -U "$db_user" -d postgres -c "CREATE DATABASE $db_name;" >/dev/null 2>&1; then
            print_status "PostgreSQL database '$db_name' created successfully"
        else
            print_warning "Could not create PostgreSQL database (might need admin privileges)"
            print_info "Please create manually: psql -U $db_user -c 'CREATE DATABASE $db_name;'"
        fi
    else
        print_warning "PostgreSQL client not found - skipping database creation"
    fi
}

# Function to create Redis database
create_redis_db() {
    local db_num="$1"
    
    print_info "Setting up Redis database $db_num"
    
    if command_exists redis-cli; then
        if redis-cli -d "$db_num" ping >/dev/null 2>&1; then
            print_status "Redis database $db_num is ready"
        else
            print_warning "Redis database $db_num not accessible"
            print_info "Please ensure Redis is running: redis-server"
        fi
    else
        print_warning "Redis client not found - skipping Redis setup"
    fi
}

# Function to create Neo4j database
create_neo4j_db() {
    local db_name="$1"
    local neo4j_user="$2"
    local neo4j_password="$3"
    
    print_info "Creating Neo4j database: $db_name"
    
    if command_exists cypher-shell; then
        # Try to create database using cypher-shell
        if echo "CREATE DATABASE $db_name;" | cypher-shell -u "$neo4j_user" -p "$neo4j_password" >/dev/null 2>&1; then
            print_status "Neo4j database '$db_name' created successfully"
        else
            # Try alternative method
            if echo "SHOW DATABASES;" | cypher-shell -u "$neo4j_user" -p "$neo4j_password" | grep -q "$db_name"; then
                print_status "Neo4j database '$db_name' already exists"
            else
                print_warning "Could not create Neo4j database"
                print_info "Please create manually: cypher-shell -u $neo4j_user"
                print_info "Then run: CREATE DATABASE $db_name;"
            fi
        fi
    else
        print_warning "Neo4j client (cypher-shell) not found - skipping database creation"
    fi
}

# Main setup function
main() {
    print_header "Jeseci Smart Learning Academy - Complete Setup"
    print_info "Setting up pure JAC architecture with database creation"
    
    # Check prerequisites
    print_header "Checking Prerequisites"
    
    # Check Python 3
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.12+ first."
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_status "Python version: $python_version"
    
    # Check pip
    if ! command_exists pip; then
        print_error "pip is not available. Please ensure pip is installed with Python."
        exit 1
    fi
    
    # Check if we're in the project root
    if ! file_exists "app.jac"; then
        print_error "app.jac not found. Please run this script from the project root directory."
        exit 1
    fi
    
    if ! file_exists "requirements.txt"; then
        print_error "requirements.txt not found. Please run this script from the project root directory."
        exit 1
    fi
    
    print_status "All prerequisites met!"
    
    # Step 1: Virtual Environment Setup
    print_header "Step 1: Virtual Environment Setup"
    
    if dir_exists "venv"; then
        print_warning "Virtual environment 'venv' already exists"
        read -p "Do you want to remove and recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf venv
        else
            print_info "Using existing virtual environment"
        fi
    fi
    
    if ! dir_exists "venv"; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_status "Virtual environment created"
    fi
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_status "Virtual environment activated"
    else
        print_error "Virtual environment activation script not found"
        exit 1
    fi
    
    # Step 2: Install Dependencies
    print_header "Step 2: Installing Dependencies"
    
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    print_info "Installing requirements.txt..."
    pip install -r requirements.txt
    
    print_status "All dependencies installed successfully!"
    
    # Step 3: Database Setup
    print_header "Step 3: Database Setup"
    
    # Load environment variables if .env exists
    if file_exists ".env"; then
        print_info "Loading environment variables from .env..."
        export $(grep -v '^#' .env | xargs)
    else
        print_warning ".env file not found - using default values"
    fi
    
    # Create PostgreSQL database
    if [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_DB" ]; then
        create_postgres_db "$POSTGRES_DB" "$POSTGRES_USER" "$POSTGRES_PASSWORD"
    fi
    
    # Setup Redis
    if [ -n "$REDIS_DB" ]; then
        create_redis_db "$REDIS_DB"
    fi
    
    # Create Neo4j database
    if [ -n "$NEO4J_USER" ] && [ -n "$NEO4J_DATABASE" ]; then
        create_neo4j_db "$NEO4J_DATABASE" "$NEO4J_USER" "$NEO4J_PASSWORD"
    fi
    
    # Step 4: Validation
    print_header "Step 4: Installation Validation"
    
    print_info "Installed packages:"
    if pip show jaclang >/dev/null 2>&1; then
        jac_version=$(pip show jaclang | grep Version | cut -d' ' -f2)
        print_status "JAC Language: $jac_version"
    else
        print_warning "JAC Language not installed"
    fi
    
    if pip show jac-cloud >/dev/null 2>&1; then
        print_status "Jac Cloud: Installed"
    fi
    
    if pip show openai >/dev/null 2>&1; then
        openai_version=$(pip show openai | grep Version | cut -d' ' -f2)
        print_status "OpenAI: $openai_version"
    fi
    
    # Test JAC installation
    print_info "Testing JAC installation..."
    if command -v jac >/dev/null 2>&1; then
        jac_ver=$(jac --version 2>&1 || echo "Version check failed")
        print_status "JAC command available: $jac_ver"
    else
        print_warning "JAC command not found in PATH - restart your shell to update PATH"
    fi
    
    # Check database connectivity
    print_info "Checking database connectivity..."
    
    # PostgreSQL
    if command_exists psql && [ -n "$POSTGRES_USER" ]; then
        if PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_SERVER" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1" >/dev/null 2>&1; then
            print_status "PostgreSQL connection: OK"
        else
            print_warning "PostgreSQL connection: Failed"
            print_info "Check if PostgreSQL is running and credentials are correct"
        fi
    fi
    
    # Redis
    if command_exists redis-cli; then
        if redis-cli ping >/dev/null 2>&1; then
            print_status "Redis connection: OK"
        else
            print_warning "Redis connection: Failed"
            print_info "Check if Redis is running: redis-server"
        fi
    fi
    
    # Neo4j
    if command_exists cypher-shell && [ -n "$NEO4J_USER" ]; then
        if echo "RETURN 1;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" >/dev/null 2>&1; then
            print_status "Neo4j connection: OK"
        else
            print_warning "Neo4j connection: Failed"
            print_info "Check if Neo4j is running and credentials are correct"
        fi
    fi
    
    # Final Instructions
    print_header "🎉 Setup Complete! Next Steps"
    
    echo -e "${GREEN}Your Jeseci Smart Learning Academy is ready to run!${NC}"
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1. 🔧 Activate the virtual environment (if not already active):"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. 🚀 Start the JAC application:"
    echo "   jac serve app.jac"
    echo ""
    echo "3. 🌐 Access your learning portal:"
    echo "   http://localhost:8000"
    echo ""
    echo "4. 📊 API Endpoints (Walkers):"
    echo "   - GET /functions/register_user"
    echo "   - GET /functions/get_lesson"
    echo "   - GET /functions/generate_quiz"
    echo "   - POST /functions/submit_answer"
    echo "   - GET /functions/update_mastery"
    echo ""
    echo "🔧 Configuration:"
    echo "   - Environment: .env file"
    echo "   - Databases: PostgreSQL, Redis, Neo4j"
    echo "   - AI Integration: OpenAI API configured"
    echo ""
    echo "💡 Tips:"
    echo "   - All walkers are automatically exposed as API endpoints"
    echo "   - AI features powered by byLLM decorators"
    echo "   - Graph-based learning data using OSP (Object-Spatial Programming)"
    echo ""
    echo "🆘 Need Help?"
    echo "   - Documentation: README.md"
    echo "   - Database setup: See .env template"
    echo "   - Issues: Check logs in terminal"
    echo ""
    echo -e "${GREEN}Happy Learning! 🎓${NC}"
}

# Run main function
main "$@"