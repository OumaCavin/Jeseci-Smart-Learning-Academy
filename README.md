# Jeseci Smart Learning Academy

**Author:** Cavin Otieno  
**License:** MIT License  
**Version:** 1.0.0

An intelligent learning platform built with Jaclang, featuring AI-powered content generation, personalized learning paths, and comprehensive progress tracking.

## Features

### Core Functionality
- **User Authentication**: Secure registration and login with bcrypt password hashing and JWT tokens
- **Course Management**: Browse and enroll in courses across multiple domains
- **AI Content Generation**: Automatic lesson generation using OpenAI with template fallback
- **Progress Tracking**: Real-time learning progress and analytics
- **Knowledge Graph**: Neo4j-powered concept relationships and recommendations

### Learning Features
- **Personalized Learning Paths**: AI-driven recommendations based on progress and prerequisites
- **Interactive Quizzes**: Skill assessment and score tracking
- **Achievement System**: Gamification with badges and milestones
- **Learning Analytics**: Detailed progress reports and insights

### Technical Features
- **Jaclang Backend**: Modern walker-based API architecture
- **PostgreSQL**: Relational data storage for users and courses
- **Neo4j Graph Database**: Knowledge representation and recommendations
- **React Frontend**: Interactive user interface
- **Container-Ready**: Docker deployment support

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 16+
- Neo4j 5.x

### Installation

```bash
# Clone the repository
git clone https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git
cd Jeseci-Smart-Learning-Academy

# Setup database
bash backend/database/setup_databases.sh

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run setup script
bash setup.sh

# Start backend (Terminal 1)
jac serve backend/app.jac

# Start frontend (Terminal 2)
cd frontend && npm start
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Health**: http://localhost:8000/walker/health_check

## Project Structure

```
Jeseci-Smart-Learning-Academy/
├── backend/
│   ├── app.jac              # Main Jaclang API server
│   ├── user_auth.py         # Authentication with bcrypt/JWT
│   ├── ai_service.py        # AI content generation
│   ├── database/            # Database utilities
│   │   ├── __init__.py      # PostgreSQL & Neo4j managers
│   │   └── setup_databases.sh
│   └── agents/              # Learning agents
├── frontend/                # React application
│   ├── src/                 # Source code
│   ├── public/              # Static assets
│   └── package.json
├── docs/                    # Documentation
│   ├── api_reference.md     # API documentation
│   ├── onboarding_guide.md  # Setup guide
│   ├── ARCHITECTURE_*.md    # Architecture docs
│   ├── mermaid/             # Architecture diagrams
│   │   ├── system_arch.mmd  # System architecture
│   │   ├── auth_flow.mmd    # Authentication flow
│   │   ├── db_schema.mmd    # Database schema
│   │   └── *.mmd            # Additional diagrams
│   └── legacy/              # Historical documents
├── scripts/                 # Utility scripts
├── setup.sh                 # Environment setup
├── .env                     # Environment variables
└── README.md                # This file
```

## API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/user_create` | POST | Register new user |
| `/walker/user_login` | POST | User login |

### Courses

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/courses` | GET | List all courses |
| `/walker/course_create` | POST | Create new course |

### Progress

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/user_progress` | POST | Get user progress |
| `/walker/learning_session_start` | POST | Start learning session |
| `/walker/learning_session_end` | POST | End learning session |

### AI & Graph

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/ai_generate_content` | POST | Generate AI content |
| `/walker/graph_init` | GET | Initialize graph |
| `/walker/graph_recommendations` | POST | Get recommendations |

See [API Reference](./docs/api_reference.md) for complete documentation.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, React Router, Vite |
| Backend | Jaclang, Python 3.12 |
| Authentication | bcrypt, JWT |
| Relational DB | PostgreSQL 16+ |
| Graph DB | Neo4j 5.x |
| AI | OpenAI API |
| DevOps | Docker, Docker Compose |

## Documentation

- [Architecture Overview](./docs/ARCHITECTURE_DOCUMENTATION_SUMMARY.md)
- [API Reference](./docs/api_reference.md)
- [Onboarding Guide](./docs/onboarding_guide.md)
- [Architecture Diagrams](./docs/ARCHITECTURE_DIAGRAMS_INDEX.md)
- [Mermaid Diagrams](./docs/mermaid/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Jaclang team for the innovative programming language
- OpenAI for AI content generation capabilities
- Neo4j for graph database technology
