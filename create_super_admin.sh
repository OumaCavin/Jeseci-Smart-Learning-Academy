#!/bin/bash
# Jeseci Smart Learning Academy - Super Admin Creation Script
# This script sets up the environment and runs the super admin creation tool

# Set PYTHONPATH to enable absolute imports
export PYTHONPATH=.

# Load environment variables from backend/config/.env
if [ -f "backend/config/.env" ]; then
    export $(cat backend/config/.env | grep -v '^#' | xargs)
    echo "✓ Loaded environment variables from backend/config/.env"
else
    echo "✗ Error: backend/config/.env file not found!"
    echo "Please make sure the .env file exists with the required database credentials."
    exit 1
fi

# Check for required environment variables
MISSING_VARS=""
for var in POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB POSTGRES_HOST; do
    if [ -z "${!var}" ]; then
        MISSING_VARS="$MISSING_VARS $var"
    fi
done

if [ -n "$MISSING_VARS" ]; then
    echo "✗ Error: Missing required environment variables:$MISSING_VARS"
    echo "Please check your backend/config/.env file."
    exit 1
fi

echo ""
echo "=================================================="
echo "   SUPER ADMIN USER CREATION"
echo "=================================================="
echo ""

# Interactive input for user details
read -p "Username: " USERNAME
while [ -z "$USERNAME" ]; do
    echo "Username cannot be empty!"
    read -p "Username: " USERNAME
done

read -p "Email: " EMAIL
while [ -z "$EMAIL" ]; do
    echo "Email cannot be empty!"
    read -p "Email: " EMAIL
done

read -s -p "Password: " PASSWORD
echo ""
while [ -z "$PASSWORD" ]; do
    echo "Password cannot be empty!"
    read -s -p "Password: " PASSWORD
    echo ""
done

read -s -p "Confirm Password: " PASSWORD_CONFIRM
echo ""
while [ "$PASSWORD" != "$PASSWORD_CONFIRM" ]; do
    echo "✗ Passwords do not match!"
    read -s -p "Password: " PASSWORD
    echo ""
    read -s -p "Confirm Password: " PASSWORD_CONFIRM
    echo ""
done

echo ""
echo "=================================================="
echo "   User Details"
echo "=================================================="
echo "   Username: $USERNAME"
echo "   Email: $EMAIL"
echo "   Role: super_admin"
echo "=================================================="
echo ""

read -p "Create this super admin user? (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Creating super administrator user..."
echo ""

# Run the super admin creation script with all required environment variables
POSTGRES_USER="$POSTGRES_USER" \
POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
POSTGRES_DB="$POSTGRES_DB" \
POSTGRES_HOST="$POSTGRES_HOST" \
    python backend/create_super_admin.py \
    --username "$USERNAME" \
    --email "$EMAIL" \
    --password "$PASSWORD"

echo ""
echo "Done."
