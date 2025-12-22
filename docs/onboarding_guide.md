# Onboarding Guide

Welcome to Jeseci Smart Learning Academy! This guide will help you set up your development environment and get started with the project.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 18+ | Frontend build tools |
| PostgreSQL | 16+ | Relational database |
| Neo4j | 5.x | Graph database |
| Git | 2.0+ | Version control |

### Recommended Tools

- **uv**: Fast Python package manager
- **Docker**: Container deployment
- **VS Code**: Development IDE
- **Postman**: API testing

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git
cd Jeseci-Smart-Learning-Academy
```

### 2. Database Setup

#### PostgreSQL Setup

```bash
# Start PostgreSQL service
sudo systemctl start postgresql

# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE jeseci_learning_academy;
CREATE USER jeseci_user WITH PASSWORD 'secure_password_123';
ALTER USER jeseci_user CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE jeseci_learning_academy TO jeseci_user;

# Exit psql
\q
```

#### Neo4j Setup

```bash
# Start Neo4j service
sudo systemctl start neo4j

# Access Neo4j browser
# URL: http://localhost:7474
# Default username: neo4j
# Default password: neo4j_secure_password_2024
```

#### Run Database Setup Script

```bash
# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run setup script
bash backend/database/setup_databases.sh
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jeseci_learning_academy
POSTGRES_USER=jeseci_user
POSTGRES_PASSWORD=secure_password_123

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_secure_password_2024
NEO4J_DATABASE=jeseci_academy

# JWT Configuration
JWT_SECRET_KEY=jeseci_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Application Settings
ENVIRONMENT=development
DEBUG=true
```

### 4. Backend Setup

```bash
# Run the setup script (installs dependencies)
bash setup.sh

# Activate virtual environment
source venv/bin/activate

# Start the Jaclang backend
jac serve backend/app.jac

# Backend will be available at http://localhost:8000
```

### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Frontend will be available at http://localhost:3000
```

## Project Structure

```
Jeseci-Smart-Learning-Academy/
├── backend/
│   ├── app.jac           # Main Jaclang API
│   ├── user_auth.py      # Authentication module
│   ├── database/         # Database utilities
│   ├── agents/           # Agent implementations
│   └── ai_service.py     # AI content generation
├── frontend/
│   ├── src/              # React source code
│   ├── public/           # Static assets
│   └── package.json      # Frontend dependencies
├── docs/                 # Documentation
│   ├── mermaid/          # Architecture diagrams
│   ├── api_reference.md  # API documentation
│   └── onboarding_guide.md
├── scripts/              # Utility scripts
└── .env                  # Environment configuration
```

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

```bash
# Python linting
cd backend
flake8 .

# JavaScript linting
cd frontend
npm run lint
```

### Building for Production

```bash
# Frontend production build
cd frontend
npm run build

# Backend compiled output
jac build backend/app.jac
```

## Common Issues

### PostgreSQL Connection Failed

1. Verify PostgreSQL is running: `sudo systemctl status postgresql`
2. Check credentials in `.env` file
3. Ensure database exists: `sudo -u postgres psql -l`
4. Check port is not blocked by firewall

### Neo4j Connection Issues

1. Verify Neo4j is running: `sudo systemctl status neo4j`
2. Check credentials match in `.env`
3. Clear browser cache if using Neo4j browser
4. Check Bolt port 7687 is accessible

### Jaclang Compilation Errors

1. Ensure Python 3.12+ is installed: `python3 --version`
2. Update dependencies: `uv pip install -e backend/pyproject.toml`
3. Check for syntax errors in `.jac` files
4. Review Jaclang documentation

### Frontend Build Failures

1. Clear node_modules: `rm -rf frontend/node_modules`
2. Reinstall dependencies: `cd frontend && npm install`
3. Check Node.js version compatibility
4. Review console for specific errors

## API Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/walker/health_check

# User registration
curl -X POST http://localhost:8000/walker/user_create \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"securepass123"}'

# User login
curl -X POST http://localhost:8000/walker/user_login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"securepass123"}'
```

### Using Postman

1. Import the OpenAPI spec from `docs/api_reference.md`
2. Create a new collection for Jeseci API
3. Set up environment variables for base URL and tokens
4. Test all endpoints in the collection

## Deployment

### Docker Deployment

```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production Checklist

- [ ] Change all default passwords
- [ ] Set JWT_SECRET_KEY to a secure random value
- [ ] Configure SSL/TLS certificates
- [ ] Set up database backups
- [ ] Configure monitoring and alerts
- [ ] Review security settings
- [ ] Test in staging environment

## Getting Help

### Documentation

- [README.md](./README.md) - Project overview
- [API Reference](./api_reference.md) - Complete API documentation
- [Architecture Diagrams](./ARCHITECTURE_DIAGRAMS_INDEX.md) - Visual architecture

### Resources

- Jaclang Documentation: https://jaclang.github.io/jac/
- React Documentation: https://react.dev/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Neo4j Documentation: https://neo4j.com/docs/

### Community

- GitHub Issues: Report bugs and feature requests
- GitHub Discussions: Ask questions and share ideas
