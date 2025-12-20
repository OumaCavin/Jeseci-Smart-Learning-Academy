# 🎓 Jeseci Smart Learning Academy

[![JAC Language](https://img.shields.io/badge/JAC-0.9.3-blue.svg)](https://github.com/Jaseci-Labs/jaseci)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.124+-green.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://sqlalchemy.org)
[![SQLite](https://img.shields.io/badge/SQLite-Development-lightgrey.svg)](https://sqlite.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Production-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-Caching-red.svg)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **An AI-powered adaptive learning academy built with JAC programming language, FastAPI, and modern web technologies.**

## 🌟 Features

- 🤖 **AI-Powered Learning**: Personalized learning paths powered by intelligent AI agents
- 📊 **Progress Analytics**: Real-time learning analytics and performance tracking
- 🎯 **Adaptive Content**: Dynamic content curation based on learning patterns
- 🏆 **Gamification**: Achievement system with badges and progress rewards
- 🔐 **Enterprise Security**: Robust authentication and authorization system
- 📱 **Responsive Design**: Modern, mobile-first user interface
- 🔄 **Multi-Agent Architecture**: Specialized AI agents for different learning aspects

## 🏗️ Technology Stack

### Core Technologies
- **JAC Language** (0.9.3+) - Primary programming language
- **Python** (3.12+) - Backend development
- **FastAPI** (0.124+) - High-performance API framework
- **SQLAlchemy** (2.0+) - Database ORM

### Database & Storage
- **SQLite** - Development database (default)
- **PostgreSQL** - Production database
- **Redis** - Caching and session management
- **Neo4j** - Graph database for knowledge relationships

### Frontend & UI
- **JAC Frontend** - JAC-based frontend components
- **Modern JavaScript** - Interactive user interface
- **Responsive CSS** - Mobile-first design
- **PWA Support** - Progressive Web App capabilities

### DevOps & Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
- **Alembic** - Database migrations
- **pytest** - Testing framework

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker (optional, for full stack)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git
   cd Jeseci-Smart-Learning-Academy
   ```

2. **Set up virtual environment:**
   ```bash
   chmod +x setup_virtual_env.sh
   ./setup_virtual_env.sh
   source venv/bin/activate
   ```

3. **Install JAC language:**
   ```bash
   pip install "jaclang>=0.9.3"
   ```

4. **Initialize database:**
   ```bash
   alembic upgrade head
   ```

### Running the Application

#### Option 1: JAC Application (Primary)
```bash
# Run the main JAC application
jac serve app.jac
```

#### Option 2: FastAPI Server (Backend API)
```bash
# Run the FastAPI server
uvicorn main:app --reload --port 8000
```

#### Option 3: Docker (Full Stack)
```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps
```

### Access Points

- **JAC Application**: http://localhost:8000
- **FastAPI Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **JAC Graph Visualization**: http://localhost:8000/graph

## 📖 Documentation

### Architecture
- [System Architecture](docs/architecture/system_architecture.png)
- [Data Flow Diagram](docs/architecture/data_flow_diagram.png)
- [JAC Project Analysis](JAC_PROJECT_ANALYSIS.md)
- [JAC Validation Report](JAC_PROJECT_VALIDATION_REPORT.md)

### User Guides
- [Setup Guide](SETUP_GUIDE.md)
- [Local Setup Guide](LOCAL_SETUP_GUIDE.md)
- [End User Documentation](docs/user/end_user_guide.md)

### Development
- [Implementation Plan](docs/implementation/comprehensive_implementation_plan.md)
- [Migration Guide](docs/migration/gradual_migration_plan.md)

## 🧩 Project Structure

```
jeseci-smart-learning-academy/
├── app.jac                          # Main JAC application
├── main.py                          # FastAPI server
├── requirements.txt                 # Python dependencies
├── setup_virtual_env.sh            # Environment setup script
├── config/                          # Configuration files
├── database/                        # Database models & migrations
├── api/                             # REST API endpoints
├── frontend/                        # JAC frontend components
├── services/                        # Business logic services
├── components/                      # Reusable components
├── docs/                            # Documentation
├── migrations/                      # Database migrations
└── tests/                           # Test suites
```

## 🎯 Core Components

### JAC Application Layer
- **app.jac** - Main application controller with `app()` entry point
- **Objects** - LearningDashboard, AIChatInterface, PersonalizedRecommendations
- **Walkers** - AI processing, learning path generation, progress analytics

### FastAPI Backend
- **Authentication** - JWT-based security system
- **User Management** - Profile and preferences management
- **Learning Content** - Concept and learning path management
- **Progress Tracking** - Real-time analytics and reporting

### Database Architecture
- **SQLite** (Development) - Local testing and development
- **PostgreSQL** (Production) - Scalable production database
- **Redis** - Caching and session management
- **Neo4j** - Knowledge graph and relationship mapping

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///./jeseci_dev.db

# Production Database (uncomment for PostgreSQL)
# DATABASE_URL=postgresql://user:password@localhost:5432/jeseci_db

# Redis Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT Configuration
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=true
API_V1_STR=/api/v1
PROJECT_NAME="Jeseci Smart Learning Academy"
```

### Database Options

The application supports multiple database backends:

1. **SQLite** (Default - Development)
   ```bash
   # No additional setup required
   DATABASE_URL=sqlite:///./jeseci_dev.db
   ```

2. **PostgreSQL** (Production)
   ```bash
   # Uncomment in requirements.txt: psycopg2-binary==2.9.11
   DATABASE_URL=postgresql://user:password@localhost:5432/jeseci_db
   ```

3. **MySQL** (Alternative)
   ```bash
   # Uncomment in requirements.txt: mysql-connector-python>=8.2.0
   DATABASE_URL=mysql://user:password@localhost:3306/jeseci_db
   ```

## 🧪 Testing

### Run JAC Tests
```bash
# Test JAC syntax and compilation
jac build app.jac
jac test app.jac
```

### Run Python Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test modules
pytest tests/test_auth.py
pytest tests/test_api.py
```

### Integration Testing
```bash
# Test API endpoints
curl -X GET http://localhost:8000/health

# Test JAC application
curl -X GET http://localhost:8000/functions
```

## 📊 Monitoring & Analytics

### Health Checks
- **Database Connectivity**: Check all database connections
- **Service Status**: Monitor running services
- **Performance Metrics**: Response times and throughput

### Analytics Dashboard
- **Learning Progress**: User progress visualization
- **AI Agent Performance**: Agent efficiency metrics
- **System Health**: Real-time system monitoring

## 🚀 Deployment

### Development Deployment
```bash
# Local development
source venv/bin/activate
jac serve app.jac
uvicorn main:app --reload
```

### Production Deployment
```bash
# Docker production
docker-compose -f docker-compose.prod.yml up -d

# Kubernetes (future)
kubectl apply -f k8s/
```

### Scaling Considerations
- **Horizontal Scaling**: Multiple API instances
- **Database Sharding**: User-based data partitioning
- **Caching Strategy**: Redis cluster for high availability

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Code Standards
- **JAC Syntax**: Follow JAC language conventions
- **Python Code**: Use Black formatter and isort
- **Documentation**: Update docs for new features
- **Testing**: Add tests for new functionality

### Commit Messages
Use conventional commit format:
```
feat: add AI-powered content recommendation
fix: resolve database connection timeout
docs: update API documentation
test: add integration tests for auth module
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Cavin Otieno**  
- GitHub: [@OumaCavin](https://github.com/OumaCavin)
- Email: cavin@example.com

## 🙏 Acknowledgments

- [Jaseci Labs](https://github.com/Jaseci-Labs/jaseci) for the JAC programming language
- [FastAPI](https://fastapi.tiangolo.com) for the excellent web framework
- [SQLAlchemy](https://sqlalchemy.org) for the robust ORM
- Open source community for various libraries and tools

## 📞 Support

For support and questions:
- 📧 Email: cavin@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy/issues)
- 📖 Documentation: [Project Docs](docs/)

---

**Made with ❤️ by Cavin Otieno using JAC and modern web technologies**