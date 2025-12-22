# 📡 API Reference - Jeseci Smart Learning Academy

**Author:** Cavin Otieno  
**Date:** December 20, 2025  
**Version:** 2.0 (Pure JAC Architecture)  

## 🌐 API Overview

The Jeseci Smart Learning Academy exposes all functionality through **JAC Walkers** that are automatically converted to REST API endpoints by the `jac serve` command.

### Base URL
```
http://localhost:8000
```

### Authentication
- No external authentication required
- Session-based user management via JAC walkers
- Automatic user registration and tracking

---

## 👥 User Management APIs

### Register User
**Endpoint:** `GET /functions/register_user`  
**Method:** GET  
**Description:** Register a new user and create their learning profile

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | User's full name |
| `email` | string | Yes | User's email address |
| `learning_goals` | string | No | User's learning objectives |

#### Example Request
```bash
curl "http://localhost:8000/functions/register_user?name=John Doe&email=john@example.com&learning_goals=Learn JAC programming"
```

#### Response
```json
{
  "success": true,
  "user_id": "user_123",
  "message": "User registered successfully",
  "profile": {
    "name": "John Doe",
    "email": "john@example.com",
    "learning_goals": "Learn JAC programming",
    "created_at": "2025-12-20T22:11:40Z"
  }
}
```

### Get User Profile
**Endpoint:** `GET /functions/get_user_profile`  
**Method:** GET  
**Description:** Retrieve user profile and learning progress

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User ID to retrieve |

#### Example Request
```bash
curl "http://localhost:8000/functions/get_user_profile?user_id=user_123"
```

#### Response
```json
{
  "success": true,
  "user": {
    "user_id": "user_123",
    "name": "John Doe",
    "email": "john@example.com",
    "mastery_scores": {
      "walkers": 0.75,
      "osp": 0.60,
      "byllm": 0.40
    },
    "learning_streak": 5,
    "total_lessons_completed": 12
  }
}
```

---

## 📚 Learning Content APIs

### Get Lesson
**Endpoint:** `GET /functions/get_lesson`  
**Method:** GET  
**Description:** Retrieve personalized learning content for a concept

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User ID |
| `concept_id` | string | Yes | Concept to learn (e.g., "walkers", "osp", "byllm") |

#### Example Request
```bash
curl "http://localhost:8000/functions/get_lesson?user_id=user_123&concept_id=walkers"
```

#### Response
```json
{
  "success": true,
  "lesson": {
    "concept_id": "walkers",
    "title": "Introduction to JAC Walkers",
    "content": "Walkers are the fundamental building blocks...",
    "difficulty_level": 1,
    "estimated_duration": 15,
    "prerequisites": [],
    "code_examples": [
      {
        "title": "Basic Walker Definition",
        "code": "walker hello_world {\\n    can say_hello() {\\n        print(\"Hello from JAC!\");\\n    }\\n}"
      }
    ],
    "interactive_exercises": [
      {
        "type": "code_completion",
        "prompt": "Complete the walker to print your name",
        "solution": "walker greet_user {\\n    can greet() {\\n        print(\"Hello, user!\");\\n    }\\n}"
      }
    ]
  }
}
```

### Generate Quiz
**Endpoint:** `GET /functions/generate_quiz`  
**Method:** GET  
**Description:** Generate AI-powered quiz questions for a concept

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User ID |
| `concept_id` | string | Yes | Concept for quiz generation |
| `difficulty` | string | No | Difficulty level ("easy", "medium", "hard") |

#### Example Request
```bash
curl "http://localhost:8000/functions/generate_quiz?user_id=user_123&concept_id=walkers&difficulty=medium"
```

#### Response
```json
{
  "success": true,
  "quiz": {
    "concept_id": "walkers",
    "difficulty": "medium",
    "questions": [
      {
        "id": "q1",
        "type": "multiple_choice",
        "question": "What is the primary purpose of a walker in JAC?",
        "options": [
          "To define data structures",
          "To traverse graph nodes and perform computations",
          "To create user interfaces",
          "To manage database connections"
        ],
        "correct_answer": 1,
        "explanation": "Walkers traverse graph nodes and perform computations, making them the core execution units in JAC."
      },
      {
        "id": "q2",
        "type": "code_completion",
        "question": "Complete the walker to navigate from one node to another:",
        "code_template": "walker navigate_graph {\\n    can travel_from(start_node, target_node) {\\n        # Your code here\\n    }\\n}",
        "solution": "walker navigate_graph {\\n    can travel_from(start_node, target_node) {\\n        start_node --> target_node;\\n    }\\n}"
      }
    ],
    "generated_at": "2025-12-20T22:11:40Z"
  }
}
```

---

## ✅ Assessment APIs

### Submit Answer
**Endpoint:** `POST /functions/submit_answer`  
**Method:** POST  
**Description:** Submit quiz answers and get AI-powered evaluation

#### Request Body
```json
{
  "user_id": "user_123",
  "quiz_id": "quiz_walkers_001",
  "answers": [
    {
      "question_id": "q1",
      "answer": 1,
      "response_time": 25
    },
    {
      "question_id": "q2",
      "answer": "walker navigate_graph {\\n    can travel_from(start_node, target_node) {\\n        start_node --> target_node;\\n    }\\n}",
      "response_time": 45
    }
  ]
}
```

#### Example Request
```bash
curl -X POST "http://localhost:8000/functions/submit_answer" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_123","quiz_id":"quiz_walkers_001","answers":[{"question_id":"q1","answer":1,"response_time":25}]}'
```

#### Response
```json
{
  "success": true,
  "evaluation": {
    "quiz_id": "quiz_walkers_001",
    "total_questions": 2,
    "correct_answers": 2,
    "score": 100,
    "time_taken": 70,
    "feedback": [
      {
        "question_id": "q1",
        "correct": true,
        "explanation": "Correct! Walkers traverse graph nodes and perform computations."
      },
      {
        "question_id": "q2",
        "correct": true,
        "explanation": "Excellent! The edge traversal syntax is correct."
      }
    ],
    "ai_feedback": "Outstanding performance! You have a solid understanding of walker fundamentals. Ready to move to advanced concepts?",
    "next_recommendations": [
      "Advanced walker patterns",
      "Walker state management",
      "Cross-graph navigation"
    ]
  }
}
```

---

## 📊 Progress & Analytics APIs

### Update Mastery
**Endpoint:** `GET /functions/update_mastery`  
**Method:** GET  
**Description:** Update user mastery scores based on performance

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User ID |
| `concept_id` | string | Yes | Concept to update |
| `performance_score` | float | Yes | Performance score (0.0 - 1.0) |

#### Example Request
```bash
curl "http://localhost:8000/functions/update_mastery?user_id=user_123&concept_id=walkers&performance_score=0.85"
```

#### Response
```json
{
  "success": true,
  "mastery_update": {
    "user_id": "user_123",
    "concept_id": "walkers",
    "previous_score": 0.60,
    "new_score": 0.72,
    "improvement": 0.12,
    "unlocked_concepts": [
      "advanced_walkers",
      "walker_composition"
    ],
    "learning_streak": 6
  }
}
```

### Get Learning Path
**Endpoint:** `GET /functions/get_learning_path`  
**Method:** GET  
**Description:** Get AI-generated personalized learning path

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User ID |
| `goal` | string | No | Learning goal (e.g., "master_jac", "learn_ai") |

#### Example Request
```bash
curl "http://localhost:8000/functions/get_learning_path?user_id=user_123&goal=master_jac"
```

#### Response
```json
{
  "success": true,
  "learning_path": {
    "goal": "master_jac",
    "estimated_duration": "4 weeks",
    "current_position": {
      "completed_lessons": 8,
      "total_lessons": 24,
      "current_concept": "walkers"
    },
    "recommended_sequence": [
      {
        "concept_id": "walkers",
        "status": "in_progress",
        "mastery_score": 0.72,
        "priority": "high",
        "estimated_time": "2 hours"
      },
      {
        "concept_id": "advanced_walkers",
        "status": "locked",
        "prerequisites_met": true,
        "priority": "high",
        "estimated_time": "3 hours"
      },
      {
        "concept_id": "osp_graphs",
        "status": "locked",
        "prerequisites_met": false,
        "priority": "medium",
        "estimated_time": "4 hours"
      }
    ],
    "ai_recommendations": [
      "Focus on completing walker exercises for better retention",
      "Practice edge traversal patterns",
      "Explore walker state management"
    ]
  }
}
```

---

## 🤖 AI-Powered Features

### Generate Content
**Endpoint:** `GET /functions/generate_content`  
**Method:** GET  
**Description:** AI-generate personalized learning content

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User ID |
| `topic` | string | Yes | Topic for content generation |
| `content_type` | string | No | Type ("lesson", "exercise", "explanation") |

#### Example Request
```bash
curl "http://localhost:8000/functions/generate_content?user_id=user_123&topic=walker_patterns&content_type=exercise"
```

#### Response
```json
{
  "success": true,
  "generated_content": {
    "type": "exercise",
    "topic": "walker_patterns",
    "content": {
      "title": "Advanced Walker Pattern: Chain Navigation",
      "difficulty": "advanced",
      "description": "Create a walker that can navigate through a chain of nodes and perform operations at each step.",
      "exercise": {
        "scenario": "You have a learning path graph with nodes representing concepts. Create a walker that traverses this path and logs each concept visited.",
        "starter_code": "walker learning_path_navigator {\\n    # Implement the traversal logic\\n}",
        "hints": [
          "Use graph traversal with `for` loops",
          "Consider using `node.traverse()` method",
          "Remember to track visited nodes"
        ],
        "test_cases": [
          {
            "input": "start_node with 3 connected concepts",
            "expected_output": "All 3 concepts visited and logged"
          }
        ]
      },
      "ai_generated": true,
      "personalization_level": "high"
    }
  }
}
```

---

## 📈 Analytics APIs

### Get Learning Analytics
**Endpoint:** `GET /functions/get_analytics`  
**Method:** GET  
**Description:** Retrieve comprehensive learning analytics

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | User ID |
| `timeframe` | string | No | Time period ("week", "month", "all") |

#### Example Request
```bash
curl "http://localhost:8000/functions/get_analytics?user_id=user_123&timeframe=month"
```

#### Response
```json
{
  "success": true,
  "analytics": {
    "user_id": "user_123",
    "timeframe": "month",
    "summary": {
      "lessons_completed": 15,
      "quizzes_taken": 8,
      "average_score": 0.78,
      "learning_time": "12.5 hours",
      "streak_days": 12
    },
    "concept_mastery": [
      {
        "concept": "walkers",
        "mastery_score": 0.85,
        "improvement": 0.15,
        "time_spent": "3.2 hours"
      },
      {
        "concept": "osp",
        "mastery_score": 0.62,
        "improvement": 0.08,
        "time_spent": "2.8 hours"
      }
    ],
    "learning_patterns": {
      "best_performance_time": "morning",
      "preferred_difficulty": "medium",
      "strongest_areas": ["syntax", "basic_concepts"],
      "areas_for_improvement": ["advanced_patterns", "optimization"]
    },
    "ai_insights": [
      "User shows strong pattern recognition skills",
      "Recommend more challenging exercises in walker composition",
      "Consider introducing cross-concept projects"
    ]
  }
}
```

---

## 🚀 Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_USER_ID",
    "message": "The provided user_id does not exist",
    "details": {
      "user_id": "invalid_user_123",
      "suggestion": "Register the user first using /functions/register_user"
    }
  }
}
```

### Common Error Codes
| Code | Description |
|------|-------------|
| `INVALID_USER_ID` | User ID not found |
| `CONCEPT_NOT_ACCESSIBLE` | User hasn't met prerequisites |
| `QUIZ_ALREADY_COMPLETED` | Quiz already submitted |
| `AI_SERVICE_UNAVAILABLE` | OpenAI API temporarily unavailable |
| `INVALID_INPUT` | Request parameters are invalid |

---

## 🔧 SDK and Integration

### JavaScript Client Example
```javascript
const jacAPI = {
  async registerUser(name, email, goals) {
    const response = await fetch(`/functions/register_user?name=${name}&email=${email}&learning_goals=${goals}`);
    return await response.json();
  },
  
  async getLesson(userId, conceptId) {
    const response = await fetch(`/functions/get_lesson?user_id=${userId}&concept_id=${conceptId}`);
    return await response.json();
  },
  
  async submitAnswers(userId, quizId, answers) {
    const response = await fetch('/functions/submit_answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, quiz_id: quizId, answers })
    });
    return await response.json();
  }
};
```

---

## 📚 Related Documentation

- **Architecture Overview**: `docs/architecture/architecture_overview.md`
- **Component Diagrams**: `docs/architecture/component_diagrams.md`
- **Deployment Guide**: `docs/architecture/deployment_architecture.md`
- **Developer Guide**: `docs/architecture/developer_guide.md`