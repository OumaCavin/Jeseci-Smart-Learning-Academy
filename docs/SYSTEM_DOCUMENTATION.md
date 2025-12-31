# Jeseci Smart Learning Academy - System Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [User Categories and Roles](#user-categories-and-roles)
3. [Role Hierarchy and Permissions](#role-hierarchy-and-permissions)
4. [Access Control System](#access-control-system)
5. [Backend Authorization](#backend-authorization)
6. [Frontend Role Display](#frontend-role-display)
7. [Database Schema](#database-schema)

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

## Document Information

| Property | Value |
|----------|-------|
| **Last Updated** | 2025-12-31 |
| **Author** | Development Team |
| **Version** | 1.0 |
| **Status** | Active |

---

*This documentation is maintained as part of the Jeseci Smart Learning Academy project. For updates or corrections, please submit a pull request or contact the development team.*
