# Architecture Documentation Summary

## Project Overview

Jeseci Smart Learning Academy is an intelligent learning platform built with Jaclang, featuring AI-powered content generation, personalized learning paths, and comprehensive progress tracking. The system uses a dual-database strategy with PostgreSQL for relational data and Neo4j for knowledge graph operations.

**Author:** Cavin Otieno  
**License:** MIT License  
**Version:** 1.0.0

## System Architecture

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React 18 | Interactive learning interface |
| Backend | Jaclang | API server and business logic |
| Auth | bcrypt + JWT | Secure authentication |
| Relational DB | PostgreSQL | User and course data |
| Graph DB | Neo4j | Knowledge graphs and recommendations |
| AI | OpenAI API | Content generation |

### Architectural Patterns

#### Walker-Based Architecture
Jaclang's walker pattern provides a natural way to implement REST-like endpoints. Each walker handles specific functionality:

- **Auth Walkers**: user_create, user_login
- **Course Walkers**: courses, course_create
- **Progress Walkers**: user_progress, learning_session_start/end
- **Graph Walkers**: graph_concepts, graph_paths, graph_recommendations

#### Dual-Write Strategy
The system maintains data consistency across both databases:

- User and course data stored in PostgreSQL
- Concept relationships and learning paths in Neo4j
- Progress data written to both databases

### Security Implementation

#### Authentication Flow
1. User registers with username, email, and password
2. Password hashed with bcrypt (12 salt rounds)
3. User record stored in PostgreSQL
4. JWT token generated with 24-hour expiry
5. Token included in all subsequent API requests

#### Token Validation
- JWT tokens validated on every protected endpoint
- Tokens contain user_id, username, email, and expiry
- Expired tokens trigger automatic logout

### Database Design

#### PostgreSQL Schema
- **users**: Authentication and user profile data
- **courses**: Course metadata and configuration
- **progress**: Learning progress tracking
- **sessions**: Learning session records

#### Neo4j Graph Schema
- **Concept nodes**: Learning concepts with metadata
- **User nodes**: Learner profiles with progress
- **LearningPath nodes**: Curated learning sequences
- **PREREQUISITE edges**: Concept dependencies
- **RELATED_TO edges**: Cross-topic connections
- **Completed edges**: User progress on concepts

### API Design

All endpoints follow REST-like conventions:

```
GET  /walker/health_check     # System health
POST /walker/user_create      # Registration
POST /walker/user_login       # Authentication
GET  /walker/courses          # List courses
POST /walker/user_progress    # Get progress
POST /walker/ai_generate_content  # AI content
```

## Key Features

### AI-Powered Content Generation
- Automatic lesson generation using OpenAI
- Fallback to template-based content
- Concept-specific content customization

### Personalized Learning Paths
- Prerequisite-based recommendations
- Skill-level appropriate content
- Progress-based path suggestions

### Real-Time Progress Tracking
- Session duration monitoring
- Quiz score tracking
- Achievement system

### Knowledge Graph Integration
- Concept relationship visualization
- Learning path recommendations
- Progress analytics

## Performance Considerations

### Connection Pooling
- PostgreSQL: ThreadedConnectionPool with 15 connections
- Neo4j: Singleton driver with session management

### Caching Strategy
- JWT token caching for session validation
- Recommended Redis integration for session storage

### Scalability
- Stateless API design for horizontal scaling
- Database connection pooling for concurrency
- Container-ready deployment configuration

## Security Best Practices

1. **Password Storage**: bcrypt with 12 salt rounds
2. **Session Management**: JWT with 24-hour expiry
3. **Input Validation**: Server-side validation on all inputs
4. **SQL Injection Prevention**: Parameterized queries
5. **CORS Configuration**: Proper origin restrictions

## Deployment Options

### Development
```bash
# Setup
bash setup.sh

# Start backend
jac serve backend/app.jac

# Start frontend
cd frontend && npm start
```

### Production (Docker)
- Nginx reverse proxy
- Containerized services
- Persistent data volumes
- Monitoring with Prometheus/Grafana

## Documentation Resources

- [Architecture Diagrams Index](./ARCHITECTURE_DIAGRAMS_INDEX.md)
- [API Reference](./api_reference.md)
- [Onboarding Guide](./onboarding_guide.md)
- [Mermaid Diagrams](../mermaid/)

## License

MIT License - See LICENSE file for details
