# 🚀 Quick Start Guide

## After `git pull origin main`

Run this complete setup:

```bash
bash setup.sh
```

This will:
- ✅ Create/activate virtual environment
- ✅ Install all dependencies
- ✅ Setup databases with error handling
- ✅ Validate installation
- ✅ Print next steps

## Manual Steps (Alternative)

If you prefer manual setup:

### 1. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup Databases Only
```bash
bash setup_databases.sh
```

### 3. Start Application
```bash
jac serve app.jac
```

## 🔧 Database Configuration

Your `.env` file contains:
- **PostgreSQL**: `jeseci_learning_academy` 
- **Redis**: Database `1`
- **Neo4j**: `jeseci_academy`

## 📊 Access Points

- **Application**: http://localhost:8000
- **API Endpoints**: http://localhost:8000/functions/*

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Start Redis  
redis-server

# Start Neo4j
neo4j start
```

### JAC Command Not Found
```bash
# Restart shell or update PATH
source venv/bin/activate
```

## 📋 Available Commands

After setup, these commands are available:

```bash
# Start the learning portal
jac serve app.jac

# Test JAC installation
jac --version

# Run database setup only
bash setup_databases.sh

# Full setup (virtual env + dependencies + databases)
bash setup.sh
```