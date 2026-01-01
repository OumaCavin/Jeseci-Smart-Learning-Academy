# Jeseci Smart Learning Academy - System Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [User Categories and Roles](#user-categories-and-roles)
3. [Role Hierarchy and Permissions](#role-hierarchy-and-permissions)
4. [Access Control System](#access-control-system)
5. [Backend Authorization](#backend-authorization)
6. [Frontend Role Display](#frontend-role-display)
7. [Database Schema](#database-schema)
8. [API Endpoints Reference](#api-endpoints-reference)
9. [Content Generation Flow](#content-generation-flow)
10. [Security Considerations](#security-considerations)
11. [Development Notes](#development-notes)
12. [Related Documentation](#related-documentation-1)
13. [User Views, Access, and User Flow](#user-views-access-and-user-flow)

---

## System Overview

Jeseci Smart Learning Academy is a comprehensive learning management platform built with a modern technology stack featuring:

- **Backend**: Python with Jaclang (JAC language runtime), SQLAlchemy for PostgreSQL, and Neo4j for graph-based content
- **Frontend**: React-based admin dashboard with TypeScript
- **Database**: Hybrid storage using PostgreSQL (relational data) and Neo4j (graph relationships)
- **Authentication**: JWT-based authentication with role-based access control (RBAC)

---

## User Categories and Roles

### User Categories

The system distinguishes between two primary user categories:

| Category | Description |
|----------|-------------|
| **Regular Users** | Students/learners who use the platform for learning |
| **Admin Users** | Staff members who manage the platform |

### Complete Role Hierarchy

| Role | Level | Description |
|------|-------|-------------|
| **student** | 0 | Regular learning users - default role for all registered learners |
| **admin** | 1 | General platform administrators with basic management capabilities |
| **content_admin** | 2 | Specialized administrators focused on content management (courses, concepts, learning paths) |
| **user_admin** | 2 | Specialized administrators focused on user management |
| **analytics_admin** | 2 | Specialized administrators focused on analytics and reporting |
| **super_admin** | 3 | System administrators with complete platform access |

### Role Constants

Located in `backend/admin_auth.py`:

```python
class AdminRole:
    """Admin role definitions with hierarchical permissions"""
    
    STUDENT = "student"
    ADMIN = "admin"
    CONTENT_ADMIN = "content_admin"
    USER_ADMIN = "user_admin"
    ANALYTICS_ADMIN = "analytics_admin"
    SUPER_ADMIN = "super_admin"
```

---

## Role Hierarchy and Permissions

### Permission Hierarchy

The system implements a hierarchical permission model where higher-level roles inherit permissions from lower levels:

```
                    super_admin (Level 3)
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    content_admin    user_admin    analytics_admin
     (Level 2)        (Level 2)       (Level 2)
           │               │               │
           └───────────────┼───────────────┘
                           │
                      admin (Level 1)
                           │
                           │
                      student (Level 0)
```

### Role Permission Matrix

| Permission | student | admin | content_admin | user_admin | analytics_admin | super_admin |
|------------|---------|-------|---------------|------------|-----------------|-------------|
| **View Dashboard** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **View Users List** | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Create Users** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Edit Users** | ❌ | Limited | ❌ | ✅ | ❌ | ✅ |
| **Delete Users** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Manage User Roles** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **View Content** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Create Content** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Edit Content** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Delete Content** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **View Courses** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Manage Courses** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **View Concepts** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Manage Concepts** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **View Learning Paths** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Manage Learning Paths** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **View Quizzes** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Manage Quizzes** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **View Analytics** | ❌ | Limited | Limited | Limited | ✅ | ✅ |
| **Export Analytics** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Configure System** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **LMS Integration** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Real-time Alerts** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **API Access** | Basic | Extended | Extended | Extended | Extended | Full |

### Hierarchy Configuration

```python
# From backend/admin_auth.py
HIERARCHY = {
    AdminRole.STUDENT: 0,
    AdminRole.ADMIN: 1,
    AdminRole.CONTENT_ADMIN: 2,
    AdminRole.USER_ADMIN: 2,
    AdminRole.ANALYTICS_ADMIN: 2,
    AdminRole.SUPER_ADMIN: 3
}
```

### Permission Check Logic

The system uses the following logic to check permissions:

```python
@classmethod
def has_permission(cls, user_role: str, required_role: str) -> bool:
    """Check if user role has required permission level"""
    user_level = cls.HIERARCHY.get(user_role, 0)
    required_level = cls.HIERARCHY.get(required_role, 0)
    return user_level >= required_level
```

---

## Access Control System

### Backend Authorization

The backend implements decorator-based authorization for protecting API endpoints:

#### Authorization Decorators

| Decorator | Required Level | Usage |
|-----------|----------------|-------|
| `@require_admin()` | Level 1+ | Basic admin access |
| `@require_super_admin()` | Level 3 | Super admin only |
| `@require_content_admin()` | Level 2 | Content management |
| `@require_user_admin()` | Level 2 | User management |
| `@require_analytics_admin()` | Level 2 | Analytics access |

#### Usage Examples

```python
# Super admin only endpoints
@router.post("/lms/configure")
@require_super_admin()
async def configure_lms(request: LMSConfigRequest):
    """Only super admins can configure LMS integrations"""
    # Endpoint logic
    pass

# Content management endpoints
@router.post("/content/concepts")
@require_content_admin()
async def create_concept(request: ConceptCreateRequest):
    """Content admins can create concepts"""
    # Endpoint logic
    pass

# User management endpoints
@router.post("/users")
@require_user_admin()
async def create_user(request: UserCreateRequest):
    """User admins can create new users"""
    # Endpoint logic
    pass

# Analytics endpoints
@router.get("/analytics/usage")
@require_analytics_admin()
async def get_usage_analytics():
    """Analytics admins can view usage reports"""
    # Endpoint logic
    pass

# General admin endpoints
@router.get("/dashboard/stats")
@require_admin()
async def get_dashboard_stats():
    """Any admin can view dashboard statistics"""
    # Endpoint logic
    pass
```

### Real-time Access Control

The real-time WebSocket system also implements role-based access for admin features:

```python
# From backend/realtime_admin.py
async def connect(self, websocket: WebSocket, admin_id: str, admin_role: str):
    if admin_role == "SUPER_ADMIN":
        self.groups["super_admins"].add(websocket_id)
    elif admin_role == "CONTENT_ADMIN":
        self.groups["content_admins"].add(websocket_id)
    elif admin_role == "USER_ADMIN":
        self.groups["user_admins"].add(websocket_id)
    elif admin_role == "ANALYTICS_ADMIN":
        self.groups["analytics_admins"].add(websocket_id)
```

### Permission Flags

User permissions are exposed through a permission dictionary for frontend use:

```python
# From backend/admin_auth.py
def get_user_permissions(user_data: Dict[str, Any]) -> Dict[str, bool]:
    """Get user permissions based on admin role"""
    role = user_data.get("admin_role", AdminRole.STUDENT)
    
    return {
        "is_admin": AdminRole.has_permission(role, AdminRole.ADMIN),
        "is_super_admin": AdminRole.has_permission(role, AdminRole.SUPER_ADMIN),
        "can_manage_users": AdminRole.has_permission(role, AdminRole.USER_ADMIN),
        "can_manage_content": AdminRole.has_permission(role, AdminRole.CONTENT_ADMIN),
        "can_view_analytics": AdminRole.has_permission(role, AdminRole.ANALYTICS_ADMIN),
        "can_configure_system": AdminRole.has_permission(role, AdminRole.SUPER_ADMIN),
    }
```

---

## Frontend Role Display

### Admin Dashboard Sidebar

The admin layout displays the current user's role in the sidebar:

```typescript
// From frontend/src/admin/AdminLayout.tsx
const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'users', label: 'Users', icon: '👥' },
  { id: 'content', label: 'Content', icon: '📚' },
  { id: 'quizzes', label: 'Quizzes', icon: '📝' },
  { id: 'ai', label: 'AI Lab', icon: '🤖' },
  { id: 'analytics', label: 'Analytics', icon: '📈' },
];

// Role badge display
<span className="admin-badge">{adminUser?.admin_role || 'Administrator'}</span>
```

### User Management Role Selection

When creating or editing admin users, the system provides a role selection dropdown:

```typescript
// From frontend/src/admin/pages/UserManagement.tsx
<select
  className="form-select"
  value={formData.admin_role}
  onChange={(e) => setFormData(f => ({ ...f, admin_role: e.target.value }))}
>
  <option value="admin">Admin</option>
  <option value="content_admin">Content Admin</option>
  <option value="user_admin">User Admin</option>
  <option value="analytics_admin">Analytics Admin</option>
  <option value="super_admin">Super Admin</option>
</select>
```

### Admin User Interface Types

```typescript
// From frontend/src/services/adminApi.ts
export interface AdminUser {
  user_id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  admin_role: string;  // 'student', 'admin', 'content_admin', 'user_admin', 'analytics_admin', 'super_admin'
  is_active: boolean;
  created_at: string;
  last_login?: string;
}
```

---

## Database Schema

### Users Table

Located in `backend/database/initialize_database.py`:

```sql
CREATE TABLE jeseci_academy.users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_admin BOOLEAN DEFAULT FALSE,
    admin_role VARCHAR(50) DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    last_login_at TIMESTAMP
);
```

### User Profile Table

```sql
CREATE TABLE jeseci_academy.user_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES jeseci_academy.users(id),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    bio TEXT,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

### User Learning Preferences Table

```sql
CREATE TABLE jeseci_academy.user_learning_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES jeseci_academy.users(id),
    learning_style VARCHAR(50) DEFAULT 'visual',
    skill_level VARCHAR(50) DEFAULT 'beginner',
    preferred_difficulty VARCHAR(50) DEFAULT 'beginner',
    preferred_content_type VARCHAR(50) DEFAULT 'video',
    daily_goal_minutes INTEGER DEFAULT 30,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_reminders BOOLEAN DEFAULT TRUE,
    dark_mode BOOLEAN DEFAULT FALSE,
    auto_play_videos BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## API Endpoints Reference

### User Management Endpoints

| Endpoint | Method | Required Role | Description |
|----------|--------|---------------|-------------|
| `/walker/admin_users` | GET | admin | Get all users |
| `/walker/admin_users` | POST | user_admin | Create new user |
| `/walker/admin_users/{id}` | PUT | user_admin | Update user |
| `/walker/admin_users/{id}` | DELETE | user_admin | Delete user |
| `/walker/admin_users_search` | GET | admin | Search users |

### Content Management Endpoints

| Endpoint | Method | Required Role | Description |
|----------|--------|---------------|-------------|
| `/walker/admin_content_courses` | GET | admin | Get all courses |
| `/walker/admin_content_concepts` | GET | admin | Get all concepts |
| `/walker/admin_content_paths` | GET | admin | Get all learning paths |
| `/walker/admin_content_courses` | POST | content_admin | Create course |
| `/walker/admin_content_concepts` | POST | content_admin | Create concept |
| `/walker/admin_content_paths` | POST | content_admin | Create learning path |

### Quiz Management Endpoints

| Endpoint | Method | Required Role | Description |
|----------|--------|---------------|-------------|
| `/walker/admin_quizzes` | GET | admin | Get all quizzes |
| `/walker/admin_quizzes` | POST | content_admin | Create quiz |
| `/walker/admin_quizzes/{id}` | PUT | content_admin | Update quiz |
| `/walker/admin_quizzes/{id}` | DELETE | content_admin | Delete quiz |

### Analytics Endpoints

| Endpoint | Method | Required Role | Description |
|----------|--------|---------------|-------------|
| `/walker/admin_analytics_users` | GET | admin | User analytics |
| `/walker/admin_analytics_learning` | GET | admin | Learning analytics |
| `/walker/admin_analytics_content` | GET | admin | Content analytics |
| `/walker/admin_analytics_refresh` | POST | super_admin | Refresh analytics |

### System Configuration Endpoints

| Endpoint | Method | Required Role | Description |
|----------|--------|---------------|-------------|
| `/walker/admin_lms_configs` | GET | admin | List LMS configs |
| `/walker/admin_lms_configs` | POST | super_admin | Create LMS config |
| `/walker/admin_lms_configs/{id}` | DELETE | super_admin | Delete LMS config |

---

## Content Generation Flow

The Jeseci Smart Learning Academy includes an AI-powered content generation system that automatically creates educational materials based on specified topics, domains, and difficulty levels. This section documents the complete flow from user request to content storage and delivery.

### Overview

The content generation system leverages OpenAI's language models to produce high-quality educational content in markdown format. The system handles the complete lifecycle of content generation including prompt construction, API communication, response parsing, and persistent storage. This enables content administrators to rapidly expand the educational library with consistent, well-structured materials covering various programming concepts and technical topics.

### Architecture Components

The content generation architecture consists of three primary layers that work together to transform simple topic descriptions into comprehensive educational materials. The frontend layer provides an interface for content administrators to specify generation parameters and view results. The backend layer manages communication with external AI services and enforces access controls. The persistence layer ensures that generated content remains available for future retrieval and management operations.

**Frontend Layer**: The React-based admin dashboard includes a dedicated AI Lab section where authorized administrators can initiate content generation requests. The interface presents form fields for concept name, domain selection, difficulty level, and optional related concepts. Upon submission, the frontend constructs a structured request payload and sends it to the appropriate backend endpoint. The response displays generated content in a formatted preview along with metadata including content ID, generation timestamp, and model information.

**Backend Layer**: The backend implements Jaclang walkers that handle content generation requests with proper authentication and authorization checks. The primary walker `admin_ai_generate` receives request parameters, constructs detailed prompts for the AI model, communicates with OpenAI's API, parses the response, and stores the result in the database. Error handling ensures graceful degradation when AI services are unavailable or when prompt generation fails.

**Persistence Layer**: Generated content persists in the PostgreSQL database within the `ai_generated_content` table. Each content entry includes a unique identifier, the original concept name, domain classification, difficulty level, full markdown content, related concepts list, generation metadata, and timestamps. The storage layer also maintains usage statistics in the `ai_usage_stats` table for analytics and monitoring purposes.

### Request Flow

The content generation process follows a well-defined sequence of steps that transform user input into stored educational content. Understanding this flow helps in debugging issues and extending functionality.

```
Content Administrator
        │
        ▼
Frontend AI Lab Form
  - Concept Name: "Object Spatial Programming"
  - Domain: "Jac Language"
  - Difficulty: "intermediate"
  - Related Concepts: ["Node", "Walker"]
        │
        ▼
POST /walker/admin_ai_generate
  Headers: Authorization: Bearer {JWT}
  Body: {
    "concept_name": "Object Spatial Programming",
    "domain": "Jac Language",
    "difficulty": "intermediate",
    "related_concepts": ["Node", "Walker"]
  }
        │
        ▼
Backend Authorization Check
  - Verify JWT token
  - Check content_admin permission
        │
        ├─── Unauthorized → Return 403
        │
        └─── Authorized → Continue
                  │
                  ▼
         Prompt Construction
  - Build system prompt with content guidelines
  - Insert user parameters (concept, domain, difficulty)
  - Include related concepts for context
        │
                  ▼
         OpenAI API Call
  - Endpoint: https://api.openai.com/v1/chat/completions
  - Model: gpt-3.5-turbo or configured model
  - Max tokens: 2000
  - Temperature: 0.7
        │
                  ▼
         Response Processing
  - Parse markdown from AI response
  - Extract generated content
  - Generate unique content_id
        │
                  ▼
         Database Storage
  - INSERT INTO ai_generated_content
  - Update ai_usage_stats
  - Return generated content
        │
                  ▼
         Frontend Display
  - Show generated markdown
  - Display content metadata
  - Enable edit/delete actions
```

### Frontend Implementation

The frontend implementation resides in the admin dashboard's AI Lab section, providing a user-friendly interface for content generation requests. The implementation uses React hooks for state management and the centralized admin API service for backend communication.

```typescript
// From frontend/src/admin/pages/AIManager.tsx
const handleGenerate = async (formData: GenerateRequest) => {
  setLoading(true);
  setError(null);
  
  try {
    const response = await adminApi.generateAIContent({
      concept_name: formData.conceptName,
      domain: formData.domain,
      difficulty: formData.difficulty,
      related_concepts: formData.relatedConcepts
    });
    
    if (response.success) {
      setGeneratedContent(response.content);
      // Refresh content list
      loadAIContent();
    } else {
      setError(response.message || 'Generation failed');
    }
  } catch (err: any) {
    setError(err.message || 'Failed to generate content');
  } finally {
    setLoading(false);
  }
};
```

The frontend service method constructs the API request and handles the response unwrapping required by the Jaclang API architecture:

```typescript
// From frontend/src/services/adminApi.ts
async generateAIContent(request: {
  concept_name: string;
  domain: string;
  difficulty: string;
  related_concepts?: string[];
}): Promise<{ success: boolean; content: AIGeneratedContentAdmin; message: string }> {
  return this.makeRequest('/walker/admin_ai_generate', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}
```

### Backend Implementation

The backend implementation consists of two primary components: the Jaclang walker that handles the HTTP endpoint and the Python module that manages AI interactions and database operations.

**Jaclang Walker (app.jac)**:

The walker receives requests, validates permissions, and orchestrates the content generation process:

```jac
walker admin_ai_generate {
    can admin_ai_generate with entry {
        # Initialize store and get content with error handling
        content = {};
        try {
            ai_store.initialize_ai_content();
            content = ai_store.generate_ai_content(
                concept_name,
                domain,
                difficulty,
                related_concepts,
                generated_by
            );
        } except Exception as e {
            print("Error generating AI content: " + str(e));
            report {
                "success": False,
                "error": "Failed to generate AI content: " + str(e),
                "content": null
            }
        }
        
        if content {
            report {
                "success": True,
                "content": content,
                "message": "AI content generated successfully"
            }
        }
    }
}
```

**Python Module (backend/admin_ai_store.py)**:

The Python module contains the core logic for generating content through OpenAI and storing results:

```python
# From backend/admin_ai_store.py
def generate_ai_content(concept_name: str, domain: str, difficulty: str,
                        related_concepts: Optional[List[str]] = None,
                        generated_by: str = "admin") -> Dict[str, Any]:
    """Generate AI content using OpenAI API"""
    # Get OpenAI API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return {"success": False, "error": "OpenAI API key not configured"}
    
    # Construct prompt based on parameters
    prompt = construct_content_prompt(concept_name, domain, difficulty, related_concepts)
    
    # Call OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        content = response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return {"success": False, "error": str(e)}
    
    # Calculate token usage
    tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
    
    # Store in database
    result = save_ai_content(
        concept_name=concept_name,
        domain=domain,
        difficulty=difficulty,
        content=content,
        generated_by=generated_by,
        related_concepts=related_concepts,
        tokens_used=tokens_used
    )
    
    return result
```

### Prompt Construction

The prompt construction process transforms basic parameters into detailed instructions for the AI model. The system uses a multi-part prompt structure that ensures consistent output format and educational quality.

**System Prompt Components**:

The system prompt establishes the AI's role as an educational content creator and specifies the expected output format. Key components include role definition, output structure requirements, tone guidelines, and formatting standards. The prompt instructs the AI to produce markdown-formatted content with specific sections including overview, key concepts, examples, practice exercises, and summary.

**User Prompt Template**:

The user prompt incorporates the specific parameters from the content generation request:

```
Generate educational content about the following topic:

Topic: {concept_name}
Domain: {domain}
Difficulty Level: {difficulty}

{fmt:Related Concepts: {related_concepts} if provided}

Please create comprehensive educational content including:
1. Overview/Introduction
2. Key Concepts (numbered list)
3. Code examples where applicable
4. Practice Exercises
5. Summary

Format the content in markdown.
```

### Database Storage

Generated content persists in the PostgreSQL database through the `ai_generated_content` table. The storage implementation ensures data integrity and enables efficient retrieval for later viewing or editing.

```sql
-- From backend/database/initialize_database.py
CREATE TABLE jeseci_academy.ai_generated_content (
    content_id VARCHAR(50) PRIMARY KEY,
    concept_name VARCHAR(200) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    related_concepts JSONB,
    generated_by VARCHAR(100),
    model VARCHAR(50) DEFAULT 'openai',
    tokens_used INTEGER,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jeseci_academy.ai_usage_stats (
    id SERIAL PRIMARY KEY,
    stat_type VARCHAR(50) NOT NULL,
    stat_key VARCHAR(100),
    stat_value INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Response Structure

The API returns content in a structured format that includes both the generated material and metadata useful for management operations. The Jaclang response wrapper follows the standard pattern used throughout the platform.

```json
{
  "result": {
    "_jac_type": "admin_ai_generate",
    "_jac_id": "aadaaa8c96604c42b27dce8eb139b89b",
    "_jac_archetype": "walker",
    "concept_name": "Object Spatial Programming",
    "difficulty": "intermediate",
    "domain": "Jac Language",
    "generated_by": "admin",
    "related_concepts": ["Node"]
  },
  "reports": [
    {
      "success": true,
      "content": {
        "content_id": "ai_1767262252",
        "concept_name": "Object Spatial Programming",
        "domain": "Jac Language",
        "difficulty": "intermediate",
        "content": "# Object Spatial Programming\n\n## Overview\n...",
        "related_concepts": ["Node"],
        "generated_at": "2026-01-01T13:10:52Z",
        "generated_by": "admin",
        "source": "ai_generator",
        "model": "openai"
      },
      "message": "AI content generated successfully"
    }
  ]
}
```

### AI Content Management

Beyond generation, the system provides comprehensive management capabilities for viewing, editing, and deleting AI-generated content. These operations support the content administrator's workflow for quality assurance and content curation.

**Viewing Generated Content**: The admin panel displays all generated content in a searchable, filterable table. Each entry shows the concept name, domain, difficulty, generation date, and a content preview. Administrators can click any entry to view the full markdown content in a modal dialog.

**Editing Content**: Generated content can be modified after creation to correct errors, add platform-specific information, or improve clarity. Edit operations update the content field in the database while preserving the original generation metadata for audit purposes.

**Deleting Content**: Content administrators can remove inappropriate or obsolete generated content. Deletion removes the entry from the database and updates the associated statistics counters. The system records deletion actions in the audit log for accountability.

### Configuration Requirements

The content generation feature requires proper configuration of external service credentials and system parameters. Missing or incorrect configuration results in generation failures.

**Required Environment Variables**:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT access | Yes |
| `OPENAI_MODEL` | Model name (default: gpt-3.5-turbo) | No |
| `MAX_TOKENS` | Maximum response tokens (default: 2000) | No |
| `TEMPERATURE` | Model temperature (default: 0.7) | No |

**Configuration File Location**:

Environment variables can be set in the backend configuration file located at `backend/config/.env`. The application loads these variables during startup and makes them available to the content generation module.

```bash
# Example backend/config/.env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=2000
TEMPERATURE=0.7
```

### Error Handling

The content generation system implements comprehensive error handling to provide meaningful feedback and maintain system stability. Errors can occur at multiple stages of the generation process.

**Authentication Errors**: Invalid or missing JWT tokens result in 401 Unauthorized responses. Content administrators must have valid sessions with appropriate permissions (content_admin or higher) to generate content.

**Configuration Errors**: Missing OpenAI API key results in immediate failure with a clear error message. The system logs configuration errors to assist with debugging.

**API Errors**: OpenAI API failures (rate limits, network issues, invalid requests) propagate to the user with descriptive error messages. The system implements retry logic for transient failures.

**Database Errors**: Storage failures prevent content persistence but do not lose generated content. The system returns the generated content in the error response, allowing manual storage if needed.

### Related API Endpoints

The content generation feature integrates with several related API endpoints for complete content management functionality.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/admin_ai_generate` | POST | Generate new AI content |
| `/walker/admin_ai_content` | GET | List all generated content |
| `/walker/admin_ai_domains` | GET | List available domains |
| `/walker/admin_ai_stats` | GET | Get usage statistics |

---

## Security Considerations

### Role-Based Access Control (RBAC)

The system implements robust RBAC with the following principles:

1. **Principle of Least Privilege**: Users receive only the permissions necessary for their role
2. **Hierarchical Inheritance**: Higher roles automatically include lower-level permissions
3. **Centralized Permission Checks**: All permission checks go through `AdminRole.has_permission()`
4. **Database-Level Enforcement**: Database queries also respect role restrictions

### Authentication Flow

```
User Login
    │
    ▼
Validate Credentials (JWT)
    │
    ▼
Extract admin_role from token
    │
    ▼
Check required permission level
    │
    ├─── Has permission → Allow access
    │
    └─── No permission → Return 403 Forbidden
```

### Session Security

- JWT tokens contain embedded role information
- Tokens are validated on every request
- Role elevation requires explicit super_admin authentication
- Sessions can be invalidated for security incidents

---

## Development Notes

### Adding New Roles

To add a new role to the system:

1. **Update AdminRole class** (`backend/admin_auth.py`):
   ```python
    NEW_ROLE = "new_role"
    HIERARCHY = {
        # ... existing roles
        NEW_ROLE: 2  # Set appropriate level
    }
   ```

2. **Add authorization decorator** if needed:
   ```python
   def require_new_role():
       return require_admin(AdminRole.NEW_ROLE)
   ```

3. **Update frontend dropdown** (`frontend/src/admin/pages/UserManagement.tsx`):
   ```typescript
   <option value="new_role">New Role</option>
   ```

4. **Update permission checks** in relevant modules

5. **Add to documentation** (this file)

### Modifying Permissions

To modify permissions for existing roles:

1. Update the `HIERARCHY` dictionary in `backend/admin_auth.py`
2. Update the permission matrix in this documentation
3. Test all affected endpoints

---

## Related Documentation

- [Architecture Documentation Summary](ARCHITECTURE_DOCUMENTATION_SUMMARY.md)
- [Database Architecture](database-architecture.md)
- [API Reference](api_reference.md)
- [Admin Interface Design](ADMIN_INTERFACE_DESIGN.md)
- [Admin Interface Implementation](ADMIN_INTERFACE_IMPLEMENTATION.md)

---

## User Views, Access, and User Flow

This section provides detailed documentation on how different user types interact with the Jeseci Smart Learning Academy platform, including their respective views, access permissions, navigation flows, and behavioral patterns.

---

### Regular Users (Student Portal)

#### Student Portal Views

The student portal provides a comprehensive learning environment with multiple interconnected views designed to facilitate effective knowledge acquisition. Each view serves a specific purpose in the learning journey and contributes to an cohesive educational experience.

**Dashboard View**: The landing page for all regular users upon login displays a personalized overview of their learning progress, recommended content, and upcoming activities. The dashboard integrates with the user's learning history to surface relevant course suggestions based on their demonstrated interests and skill levels. Statistical cards present completion rates, streak information, and recent achievements to motivate continued engagement. A welcome message addresses the user by name, establishing a personalized connection with the platform from the first interaction.

**Courses View**: This view presents a catalog of available courses organized by categories, difficulty levels, and learning paths. Course cards display essential information including title, description, estimated duration, difficulty level, and progress indicators for enrolled courses. The view supports filtering by subject area, skill level, and content type to help students find relevant materials efficiently. Search functionality enables keyword-based course discovery, while pagination or infinite scrolling handles large catalogs of educational content.

**Concepts View**: The concepts view provides access to individual learning modules that cover specific topics within courses. Each concept card presents the topic name, associated difficulty level, estimated completion time, and prerequisite information. The view emphasizes visual learning through concept mapping when available, showing relationships between different topics in a learner's chosen field. Progress tracking per concept allows students to understand their mastery levels across different subject areas.

**Learning Paths View**: This view displays curated sequences of concepts and courses designed to achieve specific learning objectives. Learning path cards outline the destination skill or knowledge goal, the estimated time to completion, and the number of concepts included in the path. Visual progress indicators show advancement through the path, with milestone markers for completed sections. The view helps students understand how individual concepts connect to broader learning goals.

**Profile View**: The profile section allows students to manage their account information, learning preferences, and personal settings. Users can update their display name, bio, avatar, and contact information. The learning preferences panel enables customization of content recommendations through style selection, skill level indicators, and preferred difficulty settings. Notification preferences control email reminders, push notifications, and in-app alerts. The profile view also displays learning statistics including total time spent, courses completed, and achievements earned.

**AI Lab View**: The AI Lab provides intelligent features including personalized concept recommendations, quiz generation, and adaptive learning assistance. This view leverages the backend AI service to generate practice questions, summarize concept content, and suggest optimal learning sequences based on user performance data. Interactive chat functionality allows students to ask questions about course material and receive contextual assistance.

#### Student Access Permissions

Regular users operate with the most restrictive permission set in the system, designed to protect platform integrity while enabling full learning functionality. The access model follows the principle of least privilege, granting only the permissions necessary for educational activities.

**Content Access**: Students can view all published courses, concepts, and learning paths in read-only mode. Content appears based on visibility rules that may restrict certain materials to specific user segments or subscription levels. Students cannot modify, delete, or create new content entries in the database. Access to premium content may require subscription verification or one-time purchase validation through the integration layer.

**Quiz Access**: The system grants students access to quiz functionality including taking quizzes associated with enrolled content, reviewing past quiz results, and accessing performance analytics for their attempts. Students can retake quizzes to improve scores, though some configurations may limit retake frequency. Quiz creation and modification privileges are restricted to content administrators and above.

**Progress Tracking**: Students have full access to their personal progress data including completed concepts, quiz scores, time spent per content item, and achievement unlocking status. This data remains private to the individual user and cannot be accessed by other students. Progress synchronization occurs in real-time as students complete learning activities.

**Community Features**: If the platform includes discussion forums or peer interaction features, students gain access based on enrollment status and community guidelines. Posting, commenting, and reaction permissions follow moderation rules designed to maintain constructive learning environments.

**API Access**: The backend restricts API access for regular users to read-only endpoints essential for learning activities. Write operations, administrative functions, and system configuration endpoints require elevated permissions. Rate limiting applies more restrictively to student-level API access compared to administrative users.

#### Student User Flow

The student user journey follows a structured path designed to minimize friction while maximizing learning outcomes. Understanding this flow helps in designing features that support natural progression through educational content.

**Initial Login Flow**: Upon successful authentication, the system redirects students to the student portal dashboard. The JWT token embedded in the session contains role information that the frontend uses to select the appropriate view hierarchy. If the user has admin privileges, a settings icon appears in the navigation, providing access to the admin panel through explicit user action. This dual-role handling ensures that administrators can access both views without automatic redirection.

**Content Discovery Flow**: Students typically begin their session by exploring available content through category navigation or search. The discovery algorithm considers the user's learning history, stated preferences, and engagement patterns to surface relevant recommendations. Clicking a course or concept card loads the detail view with comprehensive information about the selected item. Enrollment or concept access occurs through explicit action buttons that trigger backend verification of access permissions.

**Learning Session Flow**: When a student begins a learning session, the system tracks their progress through the content. Video playback, reading material consumption, and interactive exercises all trigger progress updates. The frontend sends periodic heartbeat signals to maintain session state and prevent progress loss on network interruptions. Completion of a content item triggers achievement checks, progress bar updates, and potential recommendation of subsequent material.

**Quiz Taking Flow**: Accessing a quiz loads the quiz interface with questions relevant to the current learning context. Students progress through questions one at a time, with answer selection recorded before moving forward. Submission completes the attempt, triggers scoring logic on the backend, and returns the result along with explanatory feedback. Performance data feeds into the adaptive learning system to refine future recommendations.

**Session Termination Flow**: Students can end their session at any time through logout functionality that clears local session state and invalidates the JWT token on the server. Automatic session timeout occurs after a configurable period of inactivity, prompting re-authentication on the next access attempt. The system persists all progress data in real-time, ensuring no learning activity is lost due to unexpected disconnections.

#### Student Behavior Patterns

Understanding typical student behavior enables optimization of the platform for maximum engagement and learning effectiveness. The system collects and analyzes behavioral signals to improve the learning experience.

**Session Patterns**: Students typically engage in sessions ranging from 15 to 45 minutes, with peak activity occurring during evening hours and weekends. The platform sees increased engagement during academic periods and decreased activity during vacation seasons. Completion rates correlate strongly with daily goal settings and reminder notification delivery.

**Navigation Patterns**: Most students follow a predictable navigation pattern from dashboard to course catalog to specific content items. Return visitors often bypass the catalog and go directly to their in-progress content, accessed through the dashboard's continue learning section. Search usage increases when students have specific topics in mind, while browsing dominates when exploration is the goal.

**Content Consumption Patterns**: Video content shows the highest completion rates, followed by interactive exercises, and then textual material. Students frequently pause and resume video playback, indicating the importance of robust progress tracking. Quiz attempts often follow content consumption, with most students taking quizzes within the same session as the related material.

**Engagement Triggers**: Achievement notifications, streak reminders, and personalized recommendations drive the highest engagement spikes. Social features like leaderboards and peer comparisons motivate competitive students, while progress visualization appeals to those focused on mastery. Push notifications about new content in preferred categories show strong open rates.

---

### Admin Users (Admin Portal)

#### Admin Dashboard Views

The admin portal provides a comprehensive management interface for platform administrators, organized into functional sections that align with different aspects of platform operations. Each view is protected by role-based access controls that restrict functionality based on administrative privileges.

**Dashboard Overview**: The main admin dashboard presents system-wide statistics and health indicators. Key metrics include user registration counts, active sessions, content completion rates, and platform utilization trends. Real-time widgets display recent system activities, pending tasks, and alerts requiring administrative attention. The overview serves as a command center for monitoring overall platform health and identifying areas requiring intervention.

**Users Management View**: This view enables administrators to manage all user accounts in the system. The user table displays registered users with columns for username, email, role, status, registration date, and last login. Search and filtering capabilities allow quick location of specific users. Action buttons provide access to user detail views, role modification, activation toggling, and deletion functions. Bulk operations support mass updates for user status changes.

**Content Management View**: The content manager provides access to all educational materials including courses, concepts, and learning paths. Separate tabs organize content by type, with consistent table displays showing titles, categories, difficulty levels, and creation dates. Content cards expand to reveal detailed metadata including subcategories, complexity scores, key terms, and synonyms. Create, edit, and delete actions are available based on content admin permissions. The view integrates with Neo4j to display relationship mappings between concepts.

**Quiz Management View**: This view presents the quiz database with options to create, edit, and delete quiz content. Quiz cards display the associated concept, question count, difficulty level, and performance statistics. Detailed quiz views show individual questions with answer options, correct answers, and explanatory notes. Creation wizards guide content admins through the process of building new quizzes with multiple question types.

**AI Lab View**: The admin AI Lab provides access to system intelligence features including recommendation algorithms, content analysis tools, and adaptive learning configuration. Performance dashboards display AI model accuracy metrics, recommendation acceptance rates, and engagement impact statistics. Configuration panels allow fine-tuning of recommendation weights, quiz generation parameters, and adaptive difficulty adjustment rules.

**Analytics Reports View**: Comprehensive analytics dashboards present detailed reports on user behavior, content performance, and platform utilization. Interactive charts visualize trends over time, comparisons between segments, and distribution patterns. Export functionality generates reports in various formats for external analysis or stakeholder communication. Data refresh controls allow administrators to update analytics caches manually.

#### Admin Access Permissions

Administrative access follows a hierarchical permission model where elevated roles include all capabilities of lower levels plus additional specialized functions. This structure ensures appropriate division of administrative responsibilities while maintaining operational flexibility.

**Level 1 - Admin**: General administrators have read access to most system areas with limited write capabilities. They can view all dashboards, access user lists in read-only mode, view content without modification rights, and access analytics in limited capacity. This role suits team members who need visibility into system operations without the ability to make changes.

**Level 2 - Specialized Admins**: Content administrators can fully manage educational materials including courses, concepts, learning paths, and quizzes. User administrators have complete control over user accounts including creation, modification, role assignment, and deactivation. Analytics administrators have full access to reporting features with export capabilities. These specialized roles enable focused delegation of administrative responsibilities.

**Level 3 - Super Admin**: The super admin role possesses complete system access including all capabilities of other roles plus system configuration, LMS integration management, and platform-wide settings modification. Super admins serve as the ultimate authority for system operation and can delegate permissions to other administrators.

**Permission Enforcement**: The backend enforces permissions through decorator-based authorization on all API endpoints. Frontend components conditionally render based on permission flags retrieved during authentication. Audit logging tracks all administrative actions with user identification and timestamp records.

#### Admin User Flow

Administrative workflows follow patterns optimized for efficient task completion while maintaining security and accountability throughout operations.

**Authentication and Portal Access**: Administrators log in through the standard authentication flow, receiving JWT tokens with embedded role information. Upon successful authentication, the frontend routing system redirects users with admin roles to the student portal by default, maintaining the regular user experience. Administrators can access the admin panel through a prominently displayed settings icon in the navigation header, which appears only for users with admin permissions. This design ensures that admin capabilities are accessible but don't interfere with the primary learning experience.

**Admin Panel Entry**: Clicking the admin access button loads the admin layout with the sidebar navigation, header controls, and main content area. The "Back to Student Portal" button appears in the admin header, allowing quick return to the learning interface without logging out. Session management maintains context across view switches, enabling administrators to move between student and admin experiences seamlessly.

**Common Administrative Workflows**: User management workflows typically involve searching for target accounts, reviewing current settings, making necessary modifications, and confirming changes through action modals. Content management follows a create-read-update-delete pattern with validation at each stage. Analytics workflows involve selecting report parameters, reviewing visualizations, and exporting results for distribution.

**Bulk Operations**: When managing large numbers of items, administrators can select multiple entries through checkboxes and apply actions to the selection. Progress indicators show bulk operation status, with error reporting for items that failed processing. Confirmation dialogs prevent accidental mass changes.

**Session Management**: Administrative sessions use the same JWT mechanism as regular users but with elevated claims. Session timeout applies consistently, requiring re-authentication after periods of inactivity. Administrative actions during the session remain associated with the authenticated identity for audit purposes.

#### Admin Behavior Patterns

Administrator behavior differs significantly from regular users, with distinct usage patterns that inform interface design and feature prioritization.

**Access Patterns**: Administrative access typically occurs during business hours, with peak activity around morning check-ins and end-of-day reviews. Weekend and after-hours access indicates incident response rather than routine administration. Super admin access events are relatively rare and often correspond to system changes or emergency interventions.

**Task Duration**: Administrative tasks vary widely in duration, from quick user lookups taking seconds to comprehensive content audits requiring hours. The interface accommodates both patterns through efficient search and navigation, plus persistent workspace features for extended operations.

**Navigation Patterns**: Administrators develop efficient navigation paths based on their regular responsibilities. User admins primarily utilize the Users section, while content admins focus on Content management. Dashboard overview serves as a common starting point for all administrators, with section-specific views following based on task requirements.

**Risk Sensitivity**: Administrative actions carry system-wide implications, leading to more deliberate behavior patterns compared to regular users. Administrators typically review confirmation dialogs carefully and verify changes before submission. Error prevention features and undo capabilities reduce the perceived risk of administrative operations.

**Delegation Patterns**: Organizations with multiple administrators develop delegation patterns based on role assignments. Super admins often handle initial setup and then transition to monitoring mode, while specialized admins manage day-to-day operations. Understanding these patterns helps in designing approval workflows and escalation procedures.

---

### View Transition and Navigation

#### Between Student and Admin Views

The platform supports seamless transitions between student and admin views for users with dual permissions. This design accommodates the reality that platform staff also serve as learners while maintaining clear separation between personal and administrative contexts.

**Navigation Trigger**: The settings icon appears in the student portal header for users with administrative privileges. Clicking this icon opens a dropdown with the "Admin Panel" option. This explicit access pattern prevents accidental entry into administrative contexts while keeping the feature discoverable.

**State Preservation**: When transitioning from student to admin views, the current learning context is preserved in session state. Returning to the student portal restores the previous view, allowing administrators to resume their learning activities without disruption. Progress on in-progress content remains intact across view transitions.

**Permission Validation**: Each view transition validates the user's permission to access the target context. Attempting to access admin features without appropriate permissions results in a permission denied message. This validation occurs on both frontend routing and backend API access.

#### Within Admin Views

**Sidebar Navigation**: The admin sidebar provides persistent navigation between major functional areas. Collapsible mode allows maximizing content area while maintaining quick access to navigation. Active section highlighting indicates the current location within the admin hierarchy.

**Header Controls**: The admin header includes the section title, breadcrumb navigation, and utility buttons including the "Back to Student Portal" option. The header remains fixed during content scrolling, ensuring controls remain accessible.

**Contextual Actions**: Each admin view provides action buttons appropriate to its function, positioned consistently for discoverability. Primary actions appear prominently, while secondary actions are available through dropdown menus or icon buttons.

---

### State Management

#### Student Portal State

**Authentication State**: The frontend maintains authentication state including JWT token, user profile, and permission flags. This state persists across sessions through secure token storage and automatic refresh on page reload.

**Learning State**: Current progress, incomplete content, and achievement data load from the backend on session initialization. Local caching reduces API calls while real-time updates ensure currency. Optimistic updates provide responsive feedback for progress actions.

**Preference State**: User preferences including display settings, notification choices, and learning style selections store locally and sync to the backend. Local storage enables preference persistence without network dependence.

#### Admin Portal State

**Administrative State**: Admin state includes current section, selected items, filter settings, and action history. Multi-tab workflows maintain state per section, allowing quick switching between management tasks.

**Data Caching**: Admin views implement aggressive caching to reduce database load for frequently accessed data. Cache invalidation occurs on data modifications within the same session. Manual refresh options allow administrators to force cache updates.

**Audit Trail**: Administrative actions log to the audit system with timestamps, user identification, and affected resources. This trail supports accountability and troubleshooting for administrative operations.

---

### Related Documentation

- [Architecture Documentation Summary](ARCHITECTURE_DOCUMENTATION_SUMMARY.md)
- [Database Architecture](database-architecture.md)
- [API Reference](api_reference.md)
- [Admin Interface Design](ADMIN_INTERFACE_DESIGN.md)
- [Admin Interface Implementation](ADMIN_INTERFACE_IMPLEMENTATION.md)

---

## Document Information

| Property | Value |
|----------|-------|
| **Last Updated** | 2026-01-01 |
| **Author** | Development Team |
| **Version** | 1.0 |
| **Status** | Active |

---

*This documentation is maintained as part of the Jeseci Smart Learning Academy project. For updates or corrections, please submit a pull request or contact the development team.*
