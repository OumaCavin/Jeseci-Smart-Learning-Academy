#!/bin/bash
# =============================================================================
# Fix PostgreSQL User Password
# =============================================================================
# This script updates the PostgreSQL user password to match the .env file
# Author: Cavin Otieno
# =============================================================================

echo "🔧 Fixing PostgreSQL User Password"
echo ""

# Load environment variables
if [ -f "../../config/.env" ]; then
    source "../../config/.env"
    echo "[✓] Loaded environment variables from config/.env"
elif [ -f "../../.env" ]; then
    source "../../.env"
    echo "[✓] Loaded environment variables from .env"
else
    echo "[!] .env file not found in config/ or project root"
    exit 1
fi

POSTGRES_USER=${POSTGRES_USER:-jeseci_user}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-secure_password_123}

echo "📋 Will update user '$POSTGRES_USER' with password from .env"
echo ""

# Update the password
echo "🔄 Updating PostgreSQL user password..."
if sudo -u postgres psql -c "ALTER USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';" 2>/dev/null; then
    echo "[✓] Password updated successfully"
else
    echo "[!] Failed to update password. Trying with sudo..."
    if sudo -u postgres psql -c "ALTER USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"; then
        echo "[✓] Password updated successfully"
    else
        echo "[!] Could not update password. You may need to:"
        echo "    1. Log in as postgres: sudo -u postgres psql"
        echo "    2. Run: ALTER USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
        echo "    3. Exit: \q"
        exit 1
    fi
fi

# Verify connection
echo ""
echo "🔍 Verifying connection..."
if PGPASSWORD="$POSTGRES_PASSWORD" psql -h localhost -p 5432 -U "$POSTGRES_USER" -d jeseci_learning_academy -c "SELECT 1;" &>/dev/null; then
    echo "[✓] PostgreSQL connection verified successfully!"
else
    echo "[!] Connection test failed. Check your .env configuration."
    exit 1
fi

echo ""
echo "✅ PostgreSQL password fixed! You can now run the setup script."
