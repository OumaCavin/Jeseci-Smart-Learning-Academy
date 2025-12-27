#!/bin/bash
# =============================================================================
# Quick Database Setup Script
# For cases where you only need to setup databases
# Author: Cavin Otieno
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo -e "\n${BLUE}🗄️  Jeseci Academy - Database Setup${NC}\n"

# Load environment variables
# DO NOT manually export with xargs - it can corrupt passwords with special characters
if [ -f ".env" ]; then
    print_info "Environment file found: .env"
    print_info "Variables will be loaded by Python scripts"
else
    print_error ".env file not found!"
    exit 1
fi

# PostgreSQL Setup
echo -e "\n${BLUE}📊 PostgreSQL Setup${NC}"
if [ -n "$POSTGRES_DB" ] && [ -n "$POSTGRES_USER" ]; then
    print_info "Setting up PostgreSQL database: $POSTGRES_DB"
    
    if command_exists psql; then
        # Check if database exists
        if psql -h localhost -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$POSTGRES_DB'" | grep -q 1; then
            print_warning "Database $POSTGRES_DB already exists"
        else
            if PGPASSWORD="$POSTGRES_PASSWORD" psql -h localhost -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $POSTGRES_DB;" >/dev/null 2>&1; then
                print_status "PostgreSQL database '$POSTGRES_DB' created successfully"
            else
                print_error "Failed to create PostgreSQL database"
                print_info "Manual creation: psql -U $POSTGRES_USER -c 'CREATE DATABASE $POSTGRES_DB;'"
            fi
        fi
    else
        print_warning "PostgreSQL client not found"
    fi
else
    print_warning "PostgreSQL configuration not found in .env"
fi

# Redis Setup
echo -e "\n${BLUE}⚡ Redis Setup${NC}"
if [ -n "$REDIS_DB" ]; then
    print_info "Testing Redis database $REDIS_DB"
    
    if command_exists redis-cli; then
        if redis-cli -d "$REDIS_DB" ping >/dev/null 2>&1; then
            print_status "Redis database $REDIS_DB is ready"
        else
            print_warning "Redis database $REDIS_DB not accessible"
            print_info "Start Redis: redis-server"
        fi
    else
        print_warning "Redis client not found"
    fi
else
    print_warning "Redis configuration not found in .env"
fi

# Neo4j Setup
echo -e "\n${BLUE}🔗 Neo4j Setup${NC}"
if [ -n "$NEO4J_DATABASE" ] && [ -n "$NEO4J_USER" ]; then
    print_info "Setting up Neo4j database: $NEO4J_DATABASE"
    
    if command_exists cypher-shell; then
        if echo "SHOW DATABASES;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" | grep -q "$NEO4J_DATABASE"; then
            print_status "Neo4j database '$NEO4J_DATABASE' already exists"
        else
            if echo "CREATE DATABASE $NEO4J_DATABASE;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" >/dev/null 2>&1; then
                print_status "Neo4j database '$NEO4J_DATABASE' created successfully"
            else
                print_warning "Could not create Neo4j database"
                print_info "Manual creation: cypher-shell -u $NEO4J_USER"
                print_info "Then run: CREATE DATABASE $NEO4J_DATABASE;"
            fi
        fi
    else
        print_warning "Neo4j client (cypher-shell) not found"
    fi
else
    print_warning "Neo4j configuration not found in .env"
fi

echo -e "\n${GREEN}🎉 Database setup complete!${NC}"
echo -e "\n${BLUE}Connection Info:${NC}"
echo "PostgreSQL: $POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
echo "Redis: $REDIS_HOST:$REDIS_PORT (DB $REDIS_DB)"
echo "Neo4j: $NEO4J_URI/$NEO4J_DATABASE"