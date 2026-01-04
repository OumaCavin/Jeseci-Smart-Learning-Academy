# API Reference

## Authentication Endpoints

### POST /walker/user_create

Create a new user account with email and password authentication.

#### Request Body

```json
{
    "username": "string (required, unique)",
    "email": "string (required, unique)",
    "password": "string (required, min 8 chars)",
    "first_name": "string (optional)",
    "last_name": "string (optional)",
    "learning_style": "string (optional, default: visual)",
    "skill_level": "string (optional, default: beginner)"
}
```

#### Response - Success (200)

```json
{
    "success": true,
    "user_id": "user_username_abc123",
    "username": "johndoe",
    "email": "john@example.com",
    "message": "User created successfully"
}
```

#### Response - Error (409 Conflict)

```json
{
    "success": false,
    "error": "Username or email already exists",
    "code": "CONFLICT",
    "message": "User registration failed"
}
```

#### Response - Error (500)

```json
{
    "success": false,
    "error": "Database connection failed",
    "code": "ERROR",
    "message": "User registration failed"
}
```

---

### POST /walker/user_login

Authenticate user and receive JWT access token.

#### Request Body

```json
{
    "username": "string (required)",
    "password": "string (required)"
}
```

Note: Username can be the actual username or email address.

#### Response - Success (200)

```json
{
    "success": true,
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
        "user_id": "user_johndoe_abc123",
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "learning_style": "visual",
        "skill_level": "beginner"
    },
    "message": "Login successful"
}
```

#### Response - Error (401 Unauthorized)

```json
{
    "success": false,
    "error": "Invalid credentials",
    "code": "UNAUTHORIZED",
    "message": "Login failed"
}
```

#### Response - Error (500)

```json
{
    "success": false,
    "error": "Database connection failed",
    "code": "ERROR",
    "message": "Login failed"
}
```

---

## Course Endpoints

### GET /walker/courses

Retrieve all available courses.

#### Response

```json
{
    "success": true,
    "courses": [
        {
            "course_id": "course_1",
            "title": "Introduction to Programming",
            "description": "Learn the fundamentals of programming with Python",
            "domain": "Computer Science",
            "difficulty": "beginner",
            "content_type": "interactive"
        }
    ],
    "total": 5
}
```

---

### POST /walker/course_create

Create a new course (requires authentication).

#### Request Body

```json
{
    "title": "string (required)",
    "description": "string (required)",
    "domain": "string (required)",
    "difficulty": "string (required)",
    "content_type": "string (optional, default: interactive)"
}
```

#### Response

```json
{
    "success": true,
    "course_id": "course_new_001",
    "title": "New Course Title",
    "message": "Course created successfully"
}
```

---

## Progress Endpoints

### POST /walker/user_progress

Get user's learning progress.

#### Request Body

```json
{
    "user_id": "string (required)"
}
```

#### Response

```json
{
    "user_id": "user_johndoe_abc123",
    "progress": {
        "courses_completed": 3,
        "lessons_completed": 15,
        "total_study_time": 450,
        "current_streak": 5,
        "average_score": 85.5
    },
    "analytics": {
        "completion_rate": 60.0,
        "total_sessions": 10,
        "completed_sessions": 3,
        "in_progress_sessions": 7,
        "average_progress": 72.0
    },
    "learning_style": "visual",
    "skill_level": "intermediate",
    "recent_activity": [
        {
            "action": "Completed lesson",
            "item": "Variables and Data Types",
            "time": "2025-12-22T10:30:00Z"
        }
    ]
}
```

---

### POST /walker/learning_session_start

Start a new learning session.

#### Request Body

```json
{
    "user_id": "string (required)",
    "module_id": "string (required)"
}
```

#### Response

```json
{
    "success": true,
    "session_id": "session_user_module_001",
    "user_id": "user_johndoe_abc123",
    "module_id": "mod_variables",
    "status": "active",
    "message": "Learning session started"
}
```

---

### POST /walker/learning_session_end

End a learning session and record progress.

#### Request Body

```json
{
    "session_id": "string (required)",
    "progress": "number (0.0 - 1.0)"
}
```

#### Response

```json
{
    "success": true,
    "session_id": "session_user_module_001",
    "progress": 0.75,
    "status": "completed",
    "message": "Learning session ended"
}
```

---

## AI Content Generation

### POST /walker/ai_generate_content

Generate AI-powered learning content for a concept.

#### Request Body

```json
{
    "concept_name": "string (required)",
    "domain": "string (optional, default: Computer Science)",
    "difficulty": "string (optional, default: beginner)",
    "related_concepts": ["array", "of", "strings"]
}
```

#### Response

```json
{
    "success": true,
    "concept_name": "Recursion",
    "domain": "Computer Science",
    "difficulty": "intermediate",
    "content": "AI-generated content for Recursion...",
    "related_concepts": ["Base Cases", "Stack Overflow", "Dynamic Programming"],
    "generated_at": "2025-12-22T10:30:00Z",
    "source": "ai_generator"
}
```

---

## Learning Paths

### GET /walker/learning_paths

Retrieve all available learning paths.

#### Response

```json
{
    "success": true,
    "paths": [
        {
            "id": "path_python",
            "title": "Python Mastery",
            "description": "Master Python from fundamentals to advanced concepts",
            "courses": ["course_1", "course_2", "course_4"],
            "modules": [...],
            "concepts": ["concept_oop", "concept_algo", "concept_recursion"],
            "total_modules": 8,
            "completed_modules": 2,
            "duration": "8 weeks",
            "difficulty": "beginner",
            "progress": 25
        }
    ],
    "total": 3,
    "categories": ["programming", "web-development", "programming-languages"]
}
```

---

## Graph Endpoints

### GET /walker/graph_init

Initialize graph database connection.

#### Response

```json
{
    "success": true,
    "graph_engine": "initialized",
    "neo4j_connected": true,
    "postgresql_connected": true,
    "message": "Graph Knowledge Engine ready"
}
```

---

### GET /walker/graph_concepts

Retrieve all concepts from the knowledge graph.

#### Response

```json
{
    "success": true,
    "concepts": [
        {
            "id": "prog_basics",
            "name": "programming_basics",
            "display_name": "Programming Basics",
            "category": "Programming",
            "difficulty": "beginner",
            "description": "Introduction to programming concepts",
            "duration": 30,
            "prereq_count": 0
        }
    ],
    "count": 10,
    "source": "graph_database"
}
```

---

### POST /walker/graph_recommendations

Get personalized learning recommendations.

#### Request Body

```json
{
    "user_id": "string (required)",
    "limit": "number (optional, default: 5)"
}
```

#### Response

```json
{
    "success": true,
    "user_id": "user_johndoe_abc123",
    "recommendations": [
        {
            "id": "functions",
            "name": "functions",
            "display_name": "Functions",
            "category": "Programming",
            "difficulty": "intermediate",
            "duration": 60,
            "prereq_count": 2
        }
    ],
    "count": 5,
    "algorithm": "prerequisite_based"
}
```

---

## System Endpoints

### GET /walker/health_check

Check system health and database connectivity.

#### Response

```json
{
    "service": "Jeseci Smart Learning Academy API",
    "status": "healthy",
    "version": "7.0.0",
    "timestamp": "2025-12-22T10:30:00Z",
    "database_status": "connected",
    "ai_status": "available",
    "architecture": "Pure Jaclang Backend"
}
```

---

### GET /walker/init

Get API initialization information and available endpoints.

#### Response

```json
{
    "message": "Welcome to Jeseci Smart Learning Academy API!",
    "status": "initialized",
    "version": "7.0.0",
    "architecture": "Pure Jaclang Backend",
    "endpoints": {
        "health": "GET /walker/health_check",
        "init": "GET /walker/init",
        "auth": "POST /walker/user_create, POST /walker/user_login",
        "courses": "GET /walker/courses",
        "progress": "POST /walker/user_progress",
        "learning": "POST /walker/learning_session_start, POST /walker/learning_session_end",
        "ai": "POST /walker/ai_generate_content",
        "analytics": "POST /walker/analytics_generate",
        "paths": "GET /walker/learning_paths",
        "concepts": "GET /walker/concepts",
        "quizzes": "GET /walker/quizzes",
        "achievements": "POST /walker/achievements",
        "chat": "POST /walker/chat"
    }
}
```

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Invalid or missing authentication |
| 409 | Conflict | Resource already exists |
| 500 | Internal Error | Server-side error |

## Rate Limiting

Currently, no rate limiting is implemented. Future versions will include:
- 100 requests/minute for authenticated users
- 20 requests/minute for unauthenticated users

## Authentication

All protected endpoints require JWT authentication:

```
Authorization: Bearer <access_token>
```

Tokens expire after 30 minutes. Use the `/walker/user_login` endpoint to obtain a new token.
