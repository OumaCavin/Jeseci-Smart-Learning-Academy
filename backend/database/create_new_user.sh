#!/bin/bash
# =============================================================================
# Create New Database User for Jeseci Smart Learning Academy
# =============================================================================
# This script creates a new PostgreSQL user with proper permissions
# Author: Cavin Otieno
# =============================================================================

echo "Creating new PostgreSQL user: jeseci_academy_user"
echo ""

# Load environment variables
if [ -f "backend/config/.env" ]; then
    source "backend/config/.env"
    echo "[OK] Loaded environment variables from backend/config/.env"
else
    echo "[ERROR] .env file not found"
    exit 1
fi

# Set variables
NEW_USER="jeseci_academy_user"
DB_NAME="${POSTGRES_DB:-jeseci_learning_academy}"
DB_PASSWORD="${POSTGRES_PASSWORD:-jeseci_secure_password_2024}"
PG_SUPERUSER="${PG_SUPERUSER:-postgres}"

echo "Configuration:"
echo "   Database: $DB_NAME"
echo "   New User: $NEW_USER"
echo ""

# Create the new user
echo "Creating user '$NEW_USER'..."
if sudo -u "$PG_SUPERUSER" psql -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$NEW_USER') THEN CREATE USER $NEW_USER WITH PASSWORD '$DB_PASSWORD'; END IF; END \$\$;" 2>/dev/null; then
    echo "[OK] User '$NEW_USER' created or already exists"
else
    echo "[ERROR] Failed to create user"
    exit 1
fi

# Grant privileges on the database
echo "Granting database privileges..."
sudo -u "$PG_SUPERUSER" psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $NEW_USER;" 2>/dev/null || true
sudo -u "$PG_SUPERUSER" psql -c "GRANT ALL ON SCHEMA public TO $NEW_USER;" 2>/dev/null || true
sudo -u "$PG_SUPERUSER" psql -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $NEW_USER;" 2>/dev/null || true

# Test connection
echo ""
echo "Testing connection as '$NEW_USER'..."
if PGPASSWORD="$DB_PASSWORD" psql -h localhost -p 5432 -U "$NEW_USER" -d "$DB_NAME" -c "SELECT 1 AS connection_test;" &>/dev/null; then
    echo "[OK] Connection successful!"
else
    echo "[WARNING] Connection test failed. The user might need login permissions."
    echo "    Try running: sudo -u postgres psql -c \"ALTER USER $NEW_USER WITH LOGIN;\""
fi

echo ""
echo "New user '$NEW_USER' created successfully!"
echo ""
echo "Next steps:"
echo "   1. Update backend/config/.env with:"
echo "      POSTGRES_USER=jeseci_academy_user"
echo "   2. Run setup: bash backend/database/setup_databases.sh"
