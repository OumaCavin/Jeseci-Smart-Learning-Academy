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
- **JAC Native Persistence** - Graph data stored in JAC's OSP system
- **No External Databases** - All data handled by JAC's built-in capabilities

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Git

### Installation

#### Option 1: Simplified Setup (Recommended)
```bash
# Clone and setup
git clone https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git
cd Jeseci-Smart-Learning-Academy
bash docs/pure-jac/setup_pure_jac.sh
```

#### Option 2: Manual Setup
```bash
# Clone the repository
git clone https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git
cd Jeseci-Smart-Learning-Academy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install JAC dependencies
pip install -r docs/pure-jac/requirements_pure_jac.txt

# Configure environment
cp docs/pure-jac/.env_pure_jac .env
# Add your OpenAI API key to .env
```

### Running the Application

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

### Active Project (Minimal)
```
jeseci-smart-learning-academy/
├── app.jac                          # Main JAC application with OSP models
├── README.md                        # This documentation
└── .gitignore                       # Git ignore rules
```

### Pure JAC Setup Files
```
docs/pure-jac/                       # Pure JAC setup and configuration
├── setup_pure_jac.sh                # Simplified setup script
├── requirements_pure_jac.txt        # Minimal JAC dependencies
├── .env_pure_jac                    # Environment template
└── QUICKSTART_PURE_JAC.md           # Quick start guide
```

### Legacy Implementation (Previous Architecture)
```
docs/legacy/                         # Previous FastAPI + JAC hybrid implementation
├── setup/                          # Legacy setup scripts
├── config/                         # Legacy configuration files
├── database/                       # SQLAlchemy models and migrations
├── api/                            # FastAPI endpoints
├── services/                       # Legacy service layer
├── frontend/                       # Legacy frontend components
├── migrations/                     # Database migrations
└── docs/                           # Legacy documentation (100+ files)
```

**Note**: Legacy files are preserved for reference but not actively maintained.

### Core JAC Files
- **app.jac**: Main application with OSP graph definitions and walkers
- **Walkers**: Graph traversal logic exposed as HTTP endpoints
- **Jac Client**: Frontend components for user interaction

## 🔧 Configuration

### Environment Variables

Create a `.env` file (copy from `docs/pure-jac/.env_pure_jac`):

```env
# OpenAI Configuration (Required for byLLM AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
PROJECT_NAME="Jeseci Smart Learning Academy"
PROJECT_VERSION=1.0.0
DEBUG=true

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
```

**Note**: No database configuration needed! JAC handles all data persistence natively.

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