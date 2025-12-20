# 🎓 Jeseci Smart Learning Academy

[![JAC Language](https://img.shields.io/badge/JAC-0.9.3-blue.svg)](https://github.com/Jaseci-Labs/jaseci)
[![Jac Cloud](https://img.shields.io/badge/Jac%20Cloud-Ready-green.svg)](https://cloud.jaseci.org)
[![JAC Client](https://img.shields.io/badge/JAC%20Client-Frontend-purple.svg)](https://jaseci.org/docs/jac_client)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **An AI-powered adaptive learning portal built entirely with JAC programming language using Object-Spatial Programming (OSP), byLLM, and Jac Client.**

## 🌟 Features

- 🧠 **AI-Powered Learning**: Personalized learning experiences powered by `byLLM` decorators
- 🎯 **Adaptive Content**: Dynamic content generation and assessment using Large Language Models
- 📊 **Progress Analytics**: Real-time learning analytics with OSP-based mastery tracking
- 🏆 **Intelligent Tutoring**: AI agents that analyze learning patterns and suggest next steps
- 🔗 **Knowledge Graph**: Object-Spatial Programming models relationships between concepts
- 💡 **Interactive Exercises**: Auto-generated quizzes and coding challenges
- 📈 **Skill Visualization**: Visual "skill map" showing mastered and weak areas

## 🏗️ Architecture Overview

### Core JAC Features
- **Object-Spatial Programming (OSP)**: Graph-based data modeling for learning concepts
- **byLLM Integration**: AI-powered content generation and assessment
- **Jac Client**: React-style frontend components written in JAC
- **Native Web Server**: `jac serve` provides built-in HTTP endpoints

### Technology Stack

#### Backend (JAC Language)
- **JAC Programming Language** (0.9.3+) - Primary development language
- **Object-Spatial Programming** - Graph data structures for learning models
- **byLLM Decorators** - AI-powered content generation and assessment
- **Walkers** - API endpoints and graph traversal logic

#### Frontend (Jac Client)
- **Jac Client** - React-style components in JAC
- **Interactive Code Editor** - Monaco/CodeMirror integration
- **Progress Dashboards** - Real-time learning analytics visualization
- **Responsive Design** - Mobile-first user interface

#### Data Storage
- **PostgreSQL** - User data and lesson content (`jeseci_learning_academy`)
- **Redis** - Session management and caching (`database 1`)
- **Neo4j** - Knowledge graph and relationships (`jeseci_academy`)

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Git
- PostgreSQL, Redis, and Neo4j (or use Docker)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git
   cd Jeseci-Smart-Learning-Academy
   ```

2. **Install JAC Language and Jac Cloud:**
   ```bash
   pip install jaclang jac-cloud
   ```

3. **Set up databases:**
   ```bash
   # PostgreSQL
   psql -h localhost -U jeseci_user -d jeseci_learning_academy

   # Redis
   redis-cli -d 1

   # Neo4j
   cypher-shell -u neo4j -p neo4j_secure_password_2024
   # Create database: CREATE DATABASE jeseci_academy;
   ```

4. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your database credentials
   ```

### Running the Application

#### Start the JAC Application
```bash
# Start the native JAC web server
jac serve app.jac
```

The application will be available at `http://localhost:8000`

#### Key API Endpoints (via Walkers)
- `GET /functions/register_user` - User registration
- `GET /functions/get_lesson` - Retrieve learning content
- `GET /functions/generate_quiz` - AI-generated quiz creation
- `POST /functions/submit_answer` - Answer submission and assessment
- `GET /functions/update_mastery` - Progress tracking

## 📖 Learning Portal Features

### Object-Spatial Programming (OSP) Models
- **User Nodes**: Individual learner profiles and preferences
- **Concept Nodes**: Learning topics (walkers, OSP, byLLM, etc.)
- **Lesson Nodes**: Structured learning content and exercises
- **Quiz Nodes**: Auto-generated assessments and evaluations
- **Mastery Edges**: Proficiency tracking between concepts

### AI-Powered Components
- **Content Generation**: `byLLM` decorators create personalized lesson content
- **Quiz Generation**: AI generates questions based on learning objectives
- **Assessment Engine**: Intelligent evaluation of free-text answers
- **Learning Path Optimization**: AI suggests next topics based on mastery

### Adaptive Learning Logic
- **Mastery Tracking**: Real-time proficiency scoring for each concept
- **Prerequisite Analysis**: Automatic identification of knowledge gaps
- **Difficulty Adjustment**: Dynamic quiz difficulty based on performance
- **Personalized Recommendations**: AI-driven content suggestions

## 🧩 Project Structure

```
jeseci-smart-learning-academy/
├── app.jac                          # Main JAC application with OSP models
├── requirements.txt                 # Python dependencies
├── .env.template                    # Environment configuration template
├── config/                          # Configuration files
├── frontend/                        # Jac Client components
├── services/                        # JAC services and utilities
├── api/v1/                          # API endpoints (walkers)
├── components/                      # Reusable Jac Client components
├── tests/                           # JAC test suites
└── docs/                            # Documentation
```

### Core JAC Files
- **app.jac**: Main application with OSP graph definitions and walkers
- **Walkers**: Graph traversal logic exposed as HTTP endpoints
- **Jac Client**: Frontend components for user interaction

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=jeseci_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=jeseci_learning_academy

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1

NEO4J_HOST=localhost
NEO4J_PORT=7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_secure_password_2024
NEO4J_DATABASE=jeseci_academy

# Application Settings
PROJECT_NAME="Jeseci Smart Learning Academy"
DEBUG=true
```

## 🧪 Testing

### Run JAC Tests
```bash
# Test JAC syntax and compilation
jac

# Run build app.jac JAC unit tests
jac test app.jac

# Test specific walkers
jac run app.jac --walker register_user
```

### API Testing
```bash
# Test user registration
curl -X GET "http://localhost:8000/functions/register_user?name=TestUser&email=test@example.com"

# Test lesson retrieval
curl -X GET "http://localhost:8000/functions/get_lesson?concept_id=walkers"

# Test quiz generation
curl -X GET "http://localhost:8000/functions/generate_quiz?concept_id=byllm"
```

## 🎯 Learning Content Structure

### Concept Hierarchy
1. **JAC Fundamentals**
   - Variables and Data Types
   - Functions and Walkers
   - Control Flow

2. **Object-Spatial Programming**
   - Nodes and Edges
   - Graph Manipulation
   - Relationship Modeling

3. **AI Integration**
   - byLLM Decorators
   - Content Generation
   - Intelligent Assessment

4. **Jac Client Development**
   - Component Creation
   - State Management
   - Interactive UIs

### Adaptive Learning Features
- **Prerequisite Checking**: Automatic validation of concept dependencies
- **Mastery-Based Unlocking**: Progressive content access based on proficiency
- **Difficulty Scaling**: Dynamic adjustment of quiz complexity
- **Personalized Paths**: AI-driven learning sequence optimization

## 🚀 Deployment

### Development
```bash
# Start the application
jac serve app.jac
```

### Production
```bash
# Build optimized JAC application
jac build app.jac --optimize

# Deploy with Jac Cloud
jac cloud deploy app.jac
```

### Docker Support
```bash
# Build container
docker build -t jeseci-academy .

# Run container
docker run -p 8000:8000 jeseci-academy
```

## 📊 Monitoring & Analytics

### Learning Analytics
- **Mastery Progress**: Real-time proficiency tracking
- **Learning Velocity**: Rate of concept acquisition
- **Difficulty Adaptation**: Success rate analysis
- **Knowledge Retention**: Long-term memory assessment

### System Health
- **Walker Performance**: Endpoint response times
- **Database Connectivity**: Connection pool monitoring
- **AI Generation Metrics**: byLLM processing statistics

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** OSP models and walkers
4. **Test** with `jac test`
5. **Submit** a pull request

### Code Standards
- **JAC Syntax**: Follow JAC language conventions
- **OSP Design**: Use graph structures for data modeling
- **byLLM Usage**: Implement AI features responsibly
- **Documentation**: Update docs for new features

### Commit Guidelines
```
feat(osp): add new Concept node for advanced topics
fix(byllm): resolve quiz generation edge case
docs(walkers): update API endpoint documentation
test(learning): add mastery tracking tests
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Cavin Otieno**  
- GitHub: [@OumaCavin](https://github.com/OumaCavin)
- Email: cavin.otieno012@gmail.com

## 🙏 Acknowledgments

- [Jaseci Labs](https://github.com/Jaseci-Labs/jaseci) for the revolutionary JAC programming language
- [JAC Documentation](https://jaseci.org/docs/) for comprehensive guides and examples
- Open source community for continuous innovation in AI-powered education

## 📞 Support

For support and questions:
- 📧 Email: cavin.otieno012@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy/issues)
- 📖 Documentation: [JAC Docs](https://jaseci.org/docs/)

---

**Made with ❤️ by Cavin Otieno using JAC's native AI-powered development ecosystem**