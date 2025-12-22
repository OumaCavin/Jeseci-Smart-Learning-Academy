# 🎓 Jeseci Smart Learning Academy - Graph-Powered Adaptive Learning Platform

[![JAC Language](https://img.shields.io/badge/JAC-0.9.3-blue.svg)](https://github.com/Jaseci-Labs/jaseci)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg)](https://python.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20Database-018BFF.svg)](https://neo4j.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **An AI-powered adaptive learning portal with graph-based knowledge tracking, intelligent recommendations, and real-time progress analytics. Built with JAC programming language, Neo4j graph database, and PostgreSQL.**

## 🌟 Features

### Core Learning Features
- 🧠 **AI-Powered Learning**: Personalized learning experiences powered by OpenAI integration
- 📊 **Graph-Based Knowledge Tracking**: Neo4j-powered concept relationships and dependencies
- 🎯 **Adaptive Content**: Dynamic content generation and assessment using Large Language Models
- 📈 **Progress Analytics**: Real-time learning analytics with mastery tracking
- 🏆 **Intelligent Tutoring**: AI agents that analyze learning patterns and suggest next steps
- 🔗 **Knowledge Graph**: Object-Spatial Programming models relationships between concepts
- 💡 **Interactive Exercises**: Auto-generated quizzes and coding challenges
- 📈 **Skill Visualization**: Visual "skill map" showing mastered and weak areas

### Graph-Based Intelligence
- **Concept Dependencies**: Track prerequisite relationships between learning topics
- **Learning Path Navigation**: Smart recommendations based on completed concepts
- **Progress Traversal**: Graph-based algorithms calculate learning progress
- **Similar Concepts**: Discover related topics through graph relationships
- **User Journey Visualization**: Chronological view of learning achievements

## 🏗️ Architecture Overview

### Technology Stack

#### Backend (JAC Language + Python)
- **JAC Programming Language** (0.9.3+) - Primary development language
- **Python 3.12+** - For database drivers and AI integration
- **Object-Spatial Programming** - Graph data structures for learning models
- **Walkers** - API endpoints and graph traversal logic

#### Graph Database (Neo4j)
- **Concept Nodes**: Learning topics with metadata
- **Learning Path Nodes**: Structured curricula
- **User Nodes**: Learner profiles and progress
- **Relationship Edges**: Prerequisites, related concepts, completions

#### Relational Database (PostgreSQL)
- **User Management**: Authentication and profiles
- **Concept Metadata**: Detailed concept information
- **Progress Records**: Learning session data
- **Achievements**: Gamification tracking

#### Frontend
- **React/TypeScript** - Modern responsive UI
- **API Integration**: RESTful endpoints for data
- **Interactive Dashboard**: Real-time progress visualization

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** with pip installed
- **Git** for repository cloning
- **Neo4j** (optional, for graph features)
- **PostgreSQL** (optional, for persistence)

### Installation

#### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git
cd Jeseci-Smart-Learning-Academy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r backend/requirements.txt
pip install -r backend/database/requirements.txt

# Install JAC dependencies
pip install jaclang>=0.9.3
```

#### Step 2: Configure Environment
```bash
# Copy environment template
cp config/.env.template .env

# Edit .env with your settings
nano .env
```

Required environment variables:
```env
# OpenAI API Key (for AI features)
OPENAI_API_KEY=your_openai_api_key_here

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
```

#### Step 3: Setup Databases (Optional)

**Neo4j Setup:**
```bash
# Using Docker
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/neo4j_secure_password_2024 \
  neo4j:latest

# Or download from https://neo4j.com/download/
```

**PostgreSQL Setup:**
```bash
# Using Docker
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=jeseci_learning_academy \
  -e POSTGRES_USER=jeseci_user \
  -p 5432:5432 \
  postgres:latest

# Run database setup script
bash backend/database/setup_databases.sh
```

#### Step 4: Seed Graph Data (Optional)
```bash
# Seed the graph with sample learning data
jac serve backend/app.jac --port 8000 &
curl -X POST http://localhost:8000/walker/graph_seed
```

### Running the Application

#### Start the Backend
```bash
# Method 1: Using run.sh script
bash run.sh

# Method 2: Direct JAC serve
jac serve backend/app.jac --port 8000

# Method 3: Python with JAC compiler
python -c "from jaclang.cli import cli; cli.build('backend/app.jac')"
jac serve backend/app.jir --port 8000
```

#### Start the Frontend (Optional)
```bash
cd frontend
npm install
npm start
```

#### Access Points
- **Backend API**: http://localhost:8000
- **Walker Endpoints**: http://localhost:8000/walker/[walker_name]
- **Frontend App**: http://localhost:3000 (if running)

## 📖 Learning Portal Features

### Graph-Based Knowledge Management

#### Concept Dependencies
The platform tracks concept relationships using Neo4j:
```
Programming Basics → Variables → Control Flow → Functions → Data Structures
                                            ↓
                                    Object-Oriented Programming
                                            ↓
                                            Algorithms
```

#### Learning Path Navigation
Users follow structured paths with intelligent recommendations:
1. Complete prerequisite concepts
2. Unlock next concepts automatically
3. Get personalized suggestions based on progress

#### Progress Tracking
- **Concept Completion**: Mark topics as completed
- **Path Progress**: Calculate percentage through learning paths
- **Learning Journey**: Chronological view of achievements
- **Similar Concepts**: Discover related topics

### API Endpoints

#### Core Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/init` | GET | Initialize the application |
| `/walker/health_check` | GET | System health status |
| `/walker/user_create` | POST | Create new user |
| `/walker/user_login` | POST | User authentication |

#### Course & Content Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/courses` | GET | List all courses |
| `/walker/concepts` | GET | List all concepts |
| `/walker/learning_paths` | GET | List learning paths |

#### Graph-Based Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/graph_init` | POST | Initialize graph engine |
| `/walker/graph_seed` | POST | Seed sample data |
| `/walker/graph_concepts` | GET | Get concepts from graph |
| `/walker/graph_concept_detail` | GET | Get concept with dependencies |
| `/walker/graph_paths` | GET | Get learning paths |
| `/walker/graph_path_detail` | GET | Get path structure |
| `/walker/graph_user_progress` | POST | Get user progress |
| `/walker/graph_complete_concept` | POST | Mark concept completed |
| `/walker/graph_enroll_path` | POST | Enroll in learning path |
| `/walker/graph_recommendations` | GET | Get personalized recommendations |
| `/walker/graph_next_concept` | GET | Get next concept to learn |
| `/walker/graph_learning_journey` | GET | Get learning history |
| `/walker/graph_popular_concepts` | GET | Get trending concepts |
| `/walker/graph_stats` | GET | Get graph statistics |

#### Progress & Analytics Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/user_progress` | POST | Get user progress |
| `/walker/learning_session_start` | POST | Start learning session |
| `/walker/learning_session_end` | POST | End learning session |
| `/walker/analytics_generate` | POST | Generate analytics |

#### AI Features Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/ai_generate_content` | POST | Generate AI content |
| `/walker/chat` | POST | AI chat assistance |

### Example API Usage

#### Initialize Graph and Seed Data
```bash
# Initialize graph engine
curl -X POST http://localhost:8000/walker/graph_init

# Seed sample learning data
curl -X POST http://localhost:8000/walker/graph_seed
```

#### Get Recommendations
```bash
# Get personalized recommendations
curl "http://localhost:8000/walker/graph_recommendations?user_id=user123&limit=5"

# Response:
{
  "success": true,
  "user_id": "user123",
  "recommendations": [
    {
      "id": "functions",
      "name": "functions",
      "display_name": "Functions",
      "category": "Programming",
      "difficulty": "intermediate",
      "duration": 60
    }
  ],
  "algorithm": "prerequisite_based"
}
```

#### Complete a Concept
```bash
# Mark concept as completed
curl -X POST "http://localhost:8000/walker/graph_complete_concept?user_id=user123&concept_id=variables&score=90&time_spent=45"

# Response:
{
  "success": true,
  "user_id": "user123",
  "concept_id": "variables",
  "score": 90,
  "message": "Concept marked as completed"
}
```

#### Get Learning Journey
```bash
# Get user's learning history
curl "http://localhost:8000/walker/graph_learning_journey?user_id=user123"

# Response:
{
  "success": true,
  "user_id": "user123",
  "journey": [
    {
      "id": "prog_basics",
      "name": "programming_basics",
      "category": "Programming",
      "score": 95,
      "completed_at": 1703200000000
    }
  ],
  "category_distribution": {
    "Programming": 1
  }
}
```

## 📁 Project Structure

```
jeseci-smart-learning-academy/
├── app.jac                          # Main JAC application (compiled)
├── app.jir                          # Compiled bytecode
├── run.sh                           # Application startup script
├── setup.sh                         # Setup configuration script
├── config/
│   ├── .env                         # Environment configuration
│   └── .env.template                # Environment template
│
├── backend/
│   ├── app.jac                      # Backend API with walkers
│   ├── graph_engine.jac             # Graph-based features module
│   ├── main.py                      # Python entry point
│   ├── requirements.txt             # Python dependencies
│   ├── database/
│   │   ├── __init__.py              # Database connection managers
│   │   ├── database.jac             # Jaclang database module
│   │   ├── requirements.txt         # Database dependencies
│   │   ├── setup_databases.sh       # Database setup script
│   │   └── README.md                # Database documentation
│   └── agents/                      # AI agents
│
├── frontend/                        # React frontend application
├── docs/                            # Documentation
│   ├── legacy/                      # Legacy implementation
│   └── pure-jac/                    # Pure JAC setup files
│
└── README.md                        # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application Settings
PROJECT_NAME="Jeseci Smart Learning Academy"
PROJECT_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security
JWT_SECRET_KEY=jeseci_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (Required for AI features)
OPENAI_API_KEY=your_openai_api_key_here

# PostgreSQL (Optional)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jeseci_learning_academy
POSTGRES_USER=jeseci_user
POSTGRES_PASSWORD=secure_password_123

# Neo4j (Optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_secure_password_2024
NEO4J_DATABASE=jeseci_academy
```

### Database Setup

The application supports multiple database backends:

#### In-Memory Mode (Default)
- No external database required
- All data stored in memory
- Suitable for development and testing

#### Neo4j Graph Mode
- Install Neo4j and configure environment variables
- Run: `bash backend/database/setup_databases.sh`
- Graph-based recommendations and dependencies

#### PostgreSQL Mode
- Install PostgreSQL and create database
- Run: `bash backend/database/setup_databases.sh`
- Persistent storage for users and progress

## 🧪 Testing

### Test Backend Compilation
```bash
# Compile JAC files
python -c "from jaclang.cli import cli; cli.build('backend/app.jac')"
python -c "from jaclang.cli import cli; cli.build('backend/graph_engine.jac')"

# Expected output: Errors: 0, Warnings: 0
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/walker/health_check

# Initialize graph
curl -X POST http://localhost:8000/walker/graph_init

# Get concepts
curl http://localhost:8000/walker/graph_concepts

# Get recommendations
curl "http://localhost:8000/walker/graph_recommendations?user_id=test&limit=5"
```

### Test Graph Features
```bash
# Seed graph data
curl -X POST http://localhost:8000/walker/graph_seed

# Get graph statistics
curl http://localhost:8000/walker/graph_stats

# Get popular concepts
curl http://localhost:8000/walker/graph_popular_concepts?limit=10
```

## 📊 Monitoring & Analytics

### Learning Analytics
- **Mastery Progress**: Real-time proficiency tracking per concept
- **Learning Velocity**: Rate of concept acquisition
- **Difficulty Adaptation**: Success rate analysis
- **Knowledge Retention**: Long-term memory assessment

### System Health
- **Walker Performance**: Endpoint response times
- **Database Connectivity**: Connection pool monitoring
- **Graph Statistics**: Node and relationship counts

## 🚀 Deployment

### Development
```bash
# Start the application
bash run.sh

# Or manually
jac serve backend/app.jac --port 8000
```

### Production
```bash
# Build optimized JAC application
python -c "from jaclang.cli import cli; cli.build('backend/app.jac')"

# Deploy compiled bytecode
jac serve backend/app.jir --port 8000
```

### Docker Support
```bash
# Build container
docker build -t jeseci-academy .

# Run container
docker run -p 8000:8000 jeseci-academy
```

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** features and fix bugs
4. **Test** with compilation and API tests
5. **Submit** a pull request

### Code Standards
- **JAC Syntax**: Follow JAC language conventions
- **Python Code**: PEP 8 style guide
- **Graph Design**: Proper node and relationship modeling
- **Documentation**: Update docs for new features

### Commit Message Format
```
feat(graph): add concept dependency traversal algorithm
fix(api): resolve user progress calculation edge case
docs(readme): update setup instructions for Neo4j
refactor(database): optimize connection pooling
test(backend): add graph seed validation tests
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Cavin Otieno**  
- GitHub: [@OumaCavin](https://github.com/OumaCavin)
- Email: cavin.otieno012@gmail.com

## 🙏 Acknowledgments

- [Jaseci Labs](https://github.com/Jaseci-Labs/jaseci) for the revolutionary JAC programming language
- [Neo4j](https://neo4j.com) for powerful graph database technology
- [OpenAI](https://openai.com) for AI capabilities
- Open source community for continuous innovation in AI-powered education

## 📞 Support

For support and questions:
- 📧 Email: cavin.otieno012@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy/issues)
- 📖 Documentation: [JAC Docs](https://jaseci.org/docs/)

---

**Made with ❤️ by Cavin Otieno using JAC's native AI-powered development ecosystem with Neo4j graph intelligence**
