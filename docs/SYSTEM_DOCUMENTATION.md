# Jeseci Smart Learning Academy - System Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Code Execution Engine](#code-execution-engine)
3. [Multi-Language Code Execution](#multi-language-code-execution)
4. [Code Snippet Version History](#code-snippet-version-history)
5. [Test Case Management](#test-case-management)
6. [Debug Session Management](#debug-session-management)
7. [Error Knowledge Base](#error-knowledge-base)
8. [User Categories and Roles](#user-categories-and-roles)
9. [Role Hierarchy and Permissions](#role-hierarchy-and-permissions)
10. [Access Control System](#access-control-system)
11. [Backend Authorization](#backend-authorization)
12. [Frontend Role Display](#frontend-role-display)
13. [Database Schema](#database-schema)
14. [API Endpoints Reference](#api-endpoints-reference)
15. [Content Generation Flow](#content-generation-flow)
16. [AI Quiz Generation Flow](#ai-quiz-generation-flow)
17. [Content View Tracking](#content-view-tracking)
18. [Security Considerations](#security-considerations)
19. [Development Notes](#development-notes)
20. [Related Documentation](#related-documentation-1)
21. [User Views, Access, and User Flow](#user-views-access-and-user-flow)
22. [Frontend API Methods Reference](#frontend-api-methods-reference)

---

## System Overview

Jeseci Smart Learning Academy is a comprehensive learning management platform built with a modern technology stack featuring:

- **Backend**: Python with Jaclang (JAC language runtime), SQLAlchemy for PostgreSQL, and Neo4j for graph-based content
- **Frontend**: React-based admin dashboard with TypeScript
- **Database**: Hybrid storage using PostgreSQL (relational data) and Neo4j (graph relationships)
- **Authentication**: JWT-based authentication with role-based access control (RBAC)
- **Code Execution Engine**: Multi-language code execution, version control, testing, and debugging platform

---

## Code Execution Engine

### Overview

The Jeseci Smart Learning Academy Code Execution Engine is a comprehensive platform for executing, testing, and debugging code within a secure sandboxed environment. This engine powers interactive coding exercises, automated assessments, and step-through debugging sessions for learners studying programming concepts. The system provides a complete development environment that enables students to write, run, test, and debug code directly within the learning platform, with intelligent error detection and solution recommendations.

### Architecture Components

The Code Execution Engine consists of several integrated components that work together to provide a seamless coding experience. The execution runtime handles multi-language code execution supporting Python, JavaScript, and Jac languages, with configurable timeout limits and resource quotas for each language. The version control system automatically tracks changes to code snippets, maintaining a complete history of edits with the ability to rollback to any previous version. The testing framework enables educators to create test cases that validate student code, providing immediate feedback on correctness and performance. The debugging system provides real-time debugging capabilities with breakpoints, step-through control, and variable inspection. The error knowledge base maintains a repository of common error patterns and their solutions, helping students learn from their mistakes and understand how to fix common programming errors.

**Core Modules Location**: The code execution engine is implemented in `backend/code_execution.py` for the execution logic and `backend/code_execution_store.py` for data persistence and management operations. The database schema for code execution features is defined in `backend/database/initialize_database.py`, with dedicated tables for code snippets, versions, test cases, test results, debug sessions, and the error knowledge base.

### Security Model

The code execution engine implements a comprehensive security model to protect the platform while providing a realistic coding environment. All code executes within a sandboxed environment with resource isolation, preventing malicious or erroneous code from affecting the host system or other users. Execution timeout limits are configurable per language, with Python and JavaScript defaulting to 30 seconds and Jac language defaulting to 60 seconds due to its more complex runtime requirements. Memory and CPU quotas are enforced per execution, with Python and JavaScript allocations of 256MB and Jac allocations of 512MB to accommodate its graph-based execution model. Network access is restricted to prevent code from making external connections, though standard library functions that don't require network access remain available. Input sanitization and validation ensure that user-provided code and inputs are properly validated before execution, preventing injection attacks and other security vulnerabilities.

### Frontend Integration

The frontend provides a comprehensive code editing experience through the `CodeEditor.tsx` component located in `frontend/src/components/`. The editor features a language selector dropdown that allows users to switch between Python, JavaScript, and Jac languages, with syntax highlighting appropriate for each language. A version history panel displays all saved versions of the current code snippet, enabling users to compare changes and restore previous versions with a single click. The test case management panel allows users to create, edit, and run test cases directly within the editor interface. Debug controls provide step-through functionality including step over, step into, and step out operations, along with variable inspection and call stack visualization. The output console displays execution results, errors, and debugging information in a clearly formatted manner.

---

## Multi-Language Code Execution

### Supported Languages

The Code Execution Engine supports three programming languages, each with specific runtime configurations optimized for educational use. Python serves as the primary language for general programming education, leveraging the extensive Python standard library and providing access to commonly used modules for data manipulation, string processing, and mathematical operations. JavaScript support enables web development education, allowing students to write and execute JavaScript code with Node.js runtime features. The Jac language is the platform's native language, supporting the unique object-spatial programming paradigm that forms the foundation of the Jaseci development environment.

| Language | Runtime | Default Timeout | Memory Limit | Use Case |
|----------|---------|-----------------|--------------|----------|
| **Python** | Python 3.x | 30 seconds | 256 MB | General programming, data science, automation |
| **JavaScript** | Node.js | 30 seconds | 256 MB | Web development, server-side scripting |
| **Jac** | Jaclang Runtime | 60 seconds | 512 MB | Object-spatial programming, graph-based development |

### Execution API

The code execution endpoint provides a unified interface for executing code in any supported language. The system automatically routes the request to the appropriate runtime based on the specified language parameter, handles input and output streams, enforces resource limits, and returns structured results including output, errors, and execution metrics.

**Endpoint**: `POST /walker/execute_code`

**Request Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | string | Yes | Source code to execute |
| `language` | string | Yes | Programming language identifier (python, javascript, jac) |
| `input` | string | No | Standard input to pass to the program |
| `timeout` | integer | No | Custom execution timeout in seconds |

**Example Request**:

```json
{
    "code": "print('Hello, World!')\nprint(2 + 2)",
    "language": "python",
    "input": "",
    "timeout": 30
}
```

**Response Structure**:

| Field | Type | Description |
|-------|------|-------------|
| `output` | string | Standard output from the program |
| `error` | string | Standard error output or runtime error message |
| `execution_time` | float | Execution duration in seconds |
| `memory_used` | integer | Peak memory usage in bytes |
| `success` | boolean | Whether execution completed without errors |

**Example Response**:

```json
{
    "success": true,
    "output": "Hello, World!\n4",
    "error": "",
    "execution_time": 0.045,
    "memory_used": 15234
}
```

### Language-Specific Features

**Python Execution**: Python code executes in an isolated environment with access to the standard library including `os`, `json`, `math`, `random`, `re`, `datetime`, `collections`, `itertools`, and `functools` modules. Third-party packages are not available by default to maintain security and consistency across executions. The execution environment supports both Python 3 syntax and common patterns used in educational contexts.

**JavaScript Execution**: JavaScript code runs in a Node.js environment with access to core modules such as `console`, `process` (limited), `Buffer`, and `util`. File system access is restricted for security purposes, but string manipulation, mathematical operations, and JSON processing work as expected. The environment is suitable for teaching JavaScript fundamentals, asynchronous programming concepts, and Node.js development patterns.

**Jac Execution**: Jac language execution leverages the native Jaclang runtime with full support for object-spatial programming features including nodes, walkers, edges, and graphs. The extended timeout and memory limits accommodate the graph-based execution model. This enables teaching of the unique Jaseci paradigm alongside traditional programming concepts.

---

## Code Snippet Version History

### Overview

The version history system automatically tracks changes to code snippets, maintaining a complete audit trail of edits made by users. This feature enables students to review their progress over time, compare different versions of their code, and restore previous states when needed. Educators can also use version history to review student work and understand the evolution of their coding approach.

### Data Model

The version history is stored in the `snippet_versions` table within the `jeseci_academy` schema. Each version represents a snapshot of a code snippet at a specific point in time, capturing the complete code content, the author of the change, and optional descriptive information about what was modified.

**Database Schema**:

```sql
CREATE TABLE jeseci_academy.snippet_versions (
    id SERIAL PRIMARY KEY,
    version_id VARCHAR(100) UNIQUE NOT NULL,
    snippet_id VARCHAR(100) REFERENCES jeseci_academy.code_snippets(snippet_id),
    version_number INTEGER NOT NULL,
    code_content TEXT NOT NULL,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_description TEXT,
    UNIQUE(snippet_id, version_number)
);
```

**Field Descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `version_id` | VARCHAR(100) | Unique identifier for this version |
| `snippet_id` | VARCHAR(100) | Reference to the parent code snippet |
| `version_number` | INTEGER | Sequential version number within the snippet |
| `code_content` | TEXT | Complete source code at this version |
| `created_by` | VARCHAR(100) | User who created this version |
| `created_at` | TIMESTAMP | Timestamp of version creation |
| `change_description` | TEXT | Optional description of changes made |

### Version Management API

The system provides a comprehensive set of API endpoints for managing version history. These endpoints enable listing versions, creating new snapshots, retrieving specific versions, and rolling back to previous states. All endpoints require authentication and validate that the requesting user has access to the associated code snippet.

**Version Management Endpoints**:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/snippet_versions` | GET | List all versions for a snippet |
| `/walker/snippet_versions` | POST | Create a new version snapshot |
| `/walker/snippet_versions/{id}` | GET | Get specific version details |
| `/walker/snippet_rollback` | POST | Rollback to a previous version |
| `/walker/snippet_compare` | POST | Compare two versions (diff) |

**List Versions Request**:

```json
{
    "snippet_id": "snippet_abc123"
}
```

**List Versions Response**:

```json
{
    "success": true,
    "versions": [
        {
            "version_id": "ver_001",
            "version_number": 1,
            "created_by": "student_123",
            "created_at": "2026-01-03T10:00:00Z",
            "change_description": "Initial version"
        },
        {
            "version_id": "ver_002",
            "version_number": 2,
            "created_by": "student_123",
            "created_at": "2026-01-03T10:15:00Z",
            "change_description": "Added function to calculate sum"
        }
    ]
}
```

### Frontend Version History Panel

The frontend provides an intuitive interface for browsing and managing version history. The version panel displays as a collapsible sidebar showing a chronological list of all saved versions. Each version entry shows the version number, creation time, and change description if provided. Users can click on any version to view its complete code content, compare it with the current version, or restore it as the current working copy. Visual diff highlighting shows additions and deletions between versions, making it easy to track changes at a glance.

---

## Test Case Management

### Overview

The test case management system enables educators to create and manage test cases that validate student code submissions. Test cases specify input data, expected output, and optional validation criteria that determine whether a student's solution is correct. The system supports multiple test cases per code snippet, including hidden test cases that students cannot see, enabling comprehensive assessment of student understanding.

### Test Case Structure

Each test case defines a single validation scenario with input parameters and expected results. Test cases can be visible to students or hidden, allowing educators to include both public tests for guidance and private tests for comprehensive evaluation. Points can be assigned to each test case, enabling weighted scoring of different aspects of a solution.

**Test Case Interface**:

```typescript
interface TestCase {
    test_id: string;
    snippet_id: string;
    test_name: string;
    input_data: string;
    expected_output: string;
    is_hidden: boolean;
    points: number;
    created_by: string;
    created_at: string;
    timeout?: number;
    description?: string;
}
```

**Field Descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `test_id` | string | Unique identifier for the test case |
| `snippet_id` | string | Reference to the associated code snippet |
| `test_name` | string | Human-readable name for the test |
| `input_data` | string | Input to pass to the student code |
| `expected_output` | string | Expected output for validation |
| `is_hidden` | boolean | Whether test is hidden from students |
| `points` | number | Points awarded for passing this test |
| `created_by` | string | Educator who created the test |
| `timeout` | number | Custom timeout for this test |
| `description` | string | Optional description of what is tested |

### Test Execution API

The test execution endpoints provide comprehensive functionality for running tests and retrieving results. The system executes each test case by running the student code with the specified input and comparing the actual output against the expected output. Results include pass/fail status, execution metrics, and detailed error information for failed tests.

**Endpoint**: `POST /walker/run_test_case`

**Request**:

```json
{
    "test_id": "test_123",
    "code": "def add(a, b): return a + b"
}
```

**Response**:

```json
{
    "passed": true,
    "actual_output": "5",
    "expected_output": "5",
    "execution_time": 0.023,
    "memory_used": 12345,
    "error": null
}
```

**Batch Test Execution Endpoint**: `POST /walker/run_tests`

Runs all test cases associated with a code snippet and returns comprehensive results including overall score, individual test results, and performance metrics.

**Response**:

```json
{
    "success": true,
    "total_tests": 5,
    "passed": 4,
    "failed": 1,
    "score": 85,
    "total_points": 100,
    "earned_points": 85,
    "results": [
        {
            "test_id": "test_001",
            "test_name": "Basic Addition",
            "passed": true,
            "actual_output": "5",
            "expected_output": "5",
            "points_earned": 20
        },
        {
            "test_id": "test_002",
            "test_name": "Negative Numbers",
            "passed": false,
            "actual_output": "-3",
            "expected_output": "-5",
            "points_earned": 0,
            "error": "Output mismatch"
        }
    ],
    "execution_time": 0.452,
    "memory_used": 23456
}
```

### Test Results Storage

Test execution results are persisted in the `test_results` table for analytics and student feedback. This enables tracking of student performance over time, identifying common misconceptions, and providing detailed feedback on code quality. The storage layer captures execution details, error messages, and performance metrics for each test run.

**Test Results Schema**:

```sql
CREATE TABLE jeseci_academy.test_results (
    id SERIAL PRIMARY KEY,
    result_id VARCHAR(100) UNIQUE NOT NULL,
    test_id VARCHAR(100) REFERENCES jeseci_academy.test_cases(test_id),
    user_id VARCHAR(100),
    actual_output TEXT,
    passed BOOLEAN NOT NULL,
    execution_time FLOAT,
    memory_used INTEGER,
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Frontend Test Case Panel

The test case management panel in the frontend provides a comprehensive interface for creating, editing, and running tests. The panel displays all test cases associated with the current code snippet, with visible tests shown to all users and hidden tests indicated with a lock icon visible only to educators. Each test case card shows the test name, input, expected output, and points value. Running tests displays progress indicators and presents detailed results with pass/fail status, execution time, and any error messages. The panel integrates seamlessly with the code editor, allowing students to write code and immediately validate their solution against test cases.

---

## Debug Session Management

### Overview

The debug session management system provides comprehensive debugging capabilities for students learning to code. The system enables step-through debugging with breakpoints, variable inspection, call stack visualization, and real-time state monitoring. Debug sessions run in isolated environments, preventing interference between concurrent debugging activities while maintaining full debugging functionality.

### Debug Session Lifecycle

A debug session progresses through several states during its lifecycle, from initialization through active debugging to termination. The system manages session state to ensure proper resource allocation and cleanup, preventing resource leaks from abandoned debugging sessions.

**Session States**:

| State | Description |
|-------|-------------|
| `initializing` | Session is being set up |
| `running` | Debug session is active, code is executing |
| `paused` | Execution paused at breakpoint or step completion |
| `terminated` | Session has ended and resources are freed |

### Debug Control API

The debug API provides comprehensive control over debugging sessions, enabling fine-grained management of execution flow and state inspection. Each endpoint serves a specific purpose in the debugging workflow, from initial session creation through active debugging to proper session termination.

**Session Management Endpoints**:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/walker/debug_start` | POST | Create new debug session, return session_id |
| `/walker/debug_end` | POST | Terminate debug session, free resources |
| `/walker/debug_breakpoints` | POST | Configure breakpoints for session |
| `/walker/debug_step_over` | POST | Execute current line, skip function calls |
| `/walker/debug_step_into` | POST | Enter function call on next line |
| `/walker/debug_step_out` | POST | Return from current function |
| `/walker/debug_continue` | POST | Run to next breakpoint |
| `/walker/debug_state` | GET | Get current debug state |
| `/walker/debug_variables` | GET | Get all visible variables |
| `/walker/debug_stack` | GET | Get call stack information |

**Start Debug Session Request**:

```json
{
    "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)\n\nprint(factorial(5))",
    "language": "python"
}
```

**Start Debug Session Response**:

```json
{
    "success": true,
    "session_id": "debug_session_abc123",
    "state": "running",
    "current_line": 6,
    "breakpoints": []
}
```

**Set Breakpoints Request**:

```json
{
    "session_id": "debug_session_abc123",
    "breakpoints": [2, 4, 6]
}
```

### Debug State Response

The debug state endpoint returns comprehensive information about the current debugging session, including the current execution position, all visible variables and their values, and the call stack showing the execution history.

**Debug State Response**:

```json
{
    "success": true,
    "session_id": "debug_session_abc123",
    "state": "paused",
    "current_line": 4,
    "variables": {
        "n": 5,
        "result": 120,
        "items": [1, 2, 3, 4, 5]
    },
    "call_stack": [
        {
            "function": "main",
            "file": "main.py",
            "line": 7
        },
        {
            "function": "factorial",
            "file": "main.py",
            "line": 4
        }
    ],
    "breakpoints": [2, 4, 6],
    "output": "5\n"
}
```

### Debug Sessions Schema

Debug session data is persisted in the `debug_sessions` table for session tracking and analytics. The schema captures session metadata, user associations, and resource usage statistics.

**Debug Sessions Schema**:

```sql
CREATE TABLE jeseci_academy.debug_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    snippet_id VARCHAR(100),
    language VARCHAR(50),
    state VARCHAR(20) DEFAULT 'initializing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    total_execution_time FLOAT DEFAULT 0
);
```

### Frontend Debug Controls

The frontend provides an intuitive debugging interface with visual controls for all debugging operations. The toolbar includes buttons for starting new debug sessions, setting and clearing breakpoints, and controlling execution flow with step over, step into, step out, and continue operations. Variable watch panels display current variable values in real-time, updating as execution progresses. The call stack panel shows the hierarchical call history with the ability to inspect frames at different levels. Source code display highlights the current execution line with visual indicators for breakpoints and the current scope. Console output shows program output alongside debug information, maintaining a clear separation between normal output and debugging messages.

---

## Error Knowledge Base

### Overview

The error knowledge base is a comprehensive repository of programming errors, their causes, and recommended solutions. The system provides intelligent error lookup functionality that matches runtime errors against known patterns and suggests appropriate fixes. This feature accelerates student learning by providing immediate, contextual help when errors occur, teaching students how to diagnose and resolve common programming problems.

### Error Classification

The knowledge base maintains a hierarchical taxonomy of error types, organizing errors by category, language, and specific patterns. This classification enables efficient lookup and provides a logical structure for browsing solutions.

**Error Categories**:

| Category | Description | Examples |
|----------|-------------|----------|
| **Syntax Errors** | Language syntax violations | Missing colon, unmatched parentheses, invalid indentation |
| **Runtime Errors** | Execution-time failures | Division by zero, null reference, index out of range |
| **Logic Errors** | Incorrect program behavior | Off-by-one errors, incorrect conditionals |
| **Import Errors** | Module and dependency issues | Module not found, circular import, missing package |
| **Type Errors** | Type-related failures | Type mismatch, unexpected type, cannot convert |
| **Memory Errors** | Resource exhaustion | Stack overflow, excessive memory allocation |
| **Permission Errors** | Access control violations | File not readable, permission denied |

### Error Lookup API

The error lookup endpoint accepts error messages and contextual information, returning matching solutions from the knowledge base ranked by confidence score. The system uses pattern matching and natural language processing to identify the most relevant solutions.

**Endpoint**: `POST /walker/error_lookup`

**Request**:

```json
{
    "error_message": "NameError: name 'x' is not defined",
    "language": "python",
    "context": "def test(): print(x)"
}
```

**Response**:

```json
{
    "success": true,
    "error_type": "NameError",
    "solutions": [
        {
            "solution_id": "sol_001",
            "title": "Variable Not Defined",
            "explanation": "The variable 'x' is used before being defined or is not in scope",
            "fix": "Define the variable before use",
            "code_example": "x = 10\nprint(x)",
            "confidence": 0.95,
            "category": "Runtime Errors"
        }
    ],
    "related_errors": [
        {
            "error_type": "UnboundLocalError",
            "similarity": 0.7
        }
    ]
}
```

### Knowledge Base Management

Authorized administrators can manage the error knowledge base through dedicated endpoints, adding new error patterns and solutions to improve the system's coverage. The management interface supports CRUD operations for error entries, solution voting for quality ranking, and bulk import functionality for adding large numbers of entries.

**Admin Management Endpoints**:

| Endpoint | Method | Required Role | Description |
|----------|--------|---------------|-------------|
| `/walker/admin_errors` | GET | content_admin | List all error patterns |
| `/walker/admin_errors` | POST | content_admin | Add new error pattern |
| `/walker/admin_errors/{id}` | PUT | content_admin | Update error entry |
| `/walker/admin_errors/{id}` | DELETE | content_admin | Delete error entry |
| `/walker/admin_solutions` | POST | content_admin | Add solution to error |
| `/walker/admin_solutions/{id}` | PUT | content_admin | Update solution |

### Knowledge Base Schema

The error knowledge base is stored across multiple tables supporting efficient lookup, categorization, and quality management of error solutions.

**Error Knowledge Base Schema**:

```sql
CREATE TABLE jeseci_academy.error_knowledge_base (
    id SERIAL PRIMARY KEY,
    error_id VARCHAR(100) UNIQUE NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_pattern TEXT NOT NULL,
    language VARCHAR(50),
    category VARCHAR(50),
    severity VARCHAR(20) DEFAULT 'info',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jeseci_academy.error_solutions (
    id SERIAL PRIMARY KEY,
    solution_id VARCHAR(100) UNIQUE NOT NULL,
    error_id VARCHAR(100) REFERENCES jeseci_academy.error_knowledge_base(error_id),
    title VARCHAR(255) NOT NULL,
    explanation TEXT NOT NULL,
    fix_description TEXT,
    code_example TEXT,
    confidence_score FLOAT DEFAULT 0.5,
    votes INTEGER DEFAULT 0,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Frontend Error Display

The frontend integrates error knowledge base results directly into the code editor interface. When a runtime error occurs, the error display panel shows the error message along with suggested solutions from the knowledge base. Each solution displays the title, explanation, and a code example demonstrating the fix. Students can apply fixes with a single click, copying the solution code directly into their editor. Related errors and similar patterns are shown for additional context, helping students understand the broader category of errors they encountered.

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

### Code Snippets Table

```sql
CREATE TABLE jeseci_academy.code_snippets (
    id SERIAL PRIMARY KEY,
    snippet_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    title VARCHAR(255),
    code_content TEXT NOT NULL,
    language VARCHAR(50) DEFAULT 'python',
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Snippet Versions Table

```sql
CREATE TABLE jeseci_academy.snippet_versions (
    id SERIAL PRIMARY KEY,
    version_id VARCHAR(100) UNIQUE NOT NULL,
    snippet_id VARCHAR(100) REFERENCES jeseci_academy.code_snippets(snippet_id),
    version_number INTEGER NOT NULL,
    code_content TEXT NOT NULL,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_description TEXT,
    UNIQUE(snippet_id, version_number)
);
```

### Test Cases Table

```sql
CREATE TABLE jeseci_academy.test_cases (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(100) UNIQUE NOT NULL,
    snippet_id VARCHAR(100) REFERENCES jeseci_academy.code_snippets(snippet_id),
    test_name VARCHAR(255) NOT NULL,
    input_data TEXT,
    expected_output TEXT,
    is_hidden BOOLEAN DEFAULT FALSE,
    points INTEGER DEFAULT 10,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
```

### Test Results Table

```sql
CREATE TABLE jeseci_academy.test_results (
    id SERIAL PRIMARY KEY,
    result_id VARCHAR(100) UNIQUE NOT NULL,
    test_id VARCHAR(100) REFERENCES jeseci_academy.test_cases(test_id),
    user_id VARCHAR(100),
    actual_output TEXT,
    passed BOOLEAN NOT NULL,
    execution_time FLOAT,
    memory_used INTEGER,
    error_message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Debug Sessions Table

```sql
CREATE TABLE jeseci_academy.debug_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    snippet_id VARCHAR(100),
    language VARCHAR(50),
    state VARCHAR(20) DEFAULT 'initializing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    total_execution_time FLOAT DEFAULT 0
);
```

### Error Knowledge Base Tables

```sql
CREATE TABLE jeseci_academy.error_knowledge_base (
    id SERIAL PRIMARY KEY,
    error_id VARCHAR(100) UNIQUE NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_pattern TEXT NOT NULL,
    language VARCHAR(50),
    category VARCHAR(50),
    severity VARCHAR(20) DEFAULT 'info',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jeseci_academy.error_solutions (
    id SERIAL PRIMARY KEY,
    solution_id VARCHAR(100) UNIQUE NOT NULL,
    error_id VARCHAR(100) REFERENCES jeseci_academy.error_knowledge_base(error_id),
    title VARCHAR(255) NOT NULL,
    explanation TEXT NOT NULL,
    fix_description TEXT,
    code_example TEXT,
    confidence_score FLOAT DEFAULT 0.5,
    votes INTEGER DEFAULT 0,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### Database Sync Behavior

The Jeseci Smart Learning Academy uses a **hybrid database architecture** with PostgreSQL for relational data and Neo4j for graph relationships. Each database serves a distinct purpose, and content created from the admin panel may sync to one or both databases depending on its nature.

#### Architecture Overview

| Database | Purpose | Use Cases |
|----------|---------|-----------|
| **PostgreSQL** | Relational data storage and admin management | Courses, Quizzes, User progress, Analytics, Learning Path metadata, Code Snippets |
| **Neo4j** | Graph-based learning experience | Concepts, Learning Paths (as nodes), Concept relationships (prerequisites, related_to) |

#### Current Sync Behavior

When content is created from the admin panel, the following sync behavior applies:

| Item | Created from Admin Panel | Syncs to PostgreSQL | Syncs to Neo4j | Rationale |
|------|-------------------------|---------------------|----------------|-----------|
| **Concepts** | ✓ Yes | ✗ No | ✓ Yes | Concepts are purely graph nodes used for learning paths and prerequisites |
| **Learning Paths** | ✓ Yes | ✓ Yes | ✓ Yes | Metadata needed for admin panel, nodes needed for student learning graph |
| **Courses** | ✓ Yes | ✓ Yes | ✗ No | Courses are operational data, not part of the learning graph |
| **Quizzes** | ✓ Yes | ✓ Yes | ✗ No | Quizzes are assessment data, not part of the learning graph |
| **Relationships** | ✓ Yes | ✗ No | ✓ Yes | Graph relationships only exist in Neo4j |
| **Code Snippets** | ✓ Yes | ✓ Yes | ✗ No | Code snippets are operational data stored in PostgreSQL |

#### Sync Behavior Details

**Concepts (Neo4j only)**
- Concepts are created directly in Neo4j as `:Concept` nodes
- The admin panel queries Neo4j directly for concept listing
- Each concept has properties: `concept_id`, `name`, `display_name`, `category`, `difficulty_level`, `domain`, `key_terms`, etc.

**Learning Paths (Both databases)**
- **PostgreSQL**: Stores path metadata (path_id, title, description, difficulty, duration)
- **Neo4j**: Creates `:LearningPath` node with `PathContains` relationships to associated concepts
- When created from admin panel, both writes happen in a single operation

**Courses and Quizzes (PostgreSQL only)**
- These are operational/transactional data types
- Used for admin management and user tracking
- Not involved in the learning graph navigation

**Code Snippets (PostgreSQL only)**
- Code snippets, test cases, and debug sessions are stored in PostgreSQL
- Version history, test results, and error knowledge base are all relational data
- Neo4j is not required for code execution features

**Relationships (Neo4j only)**
- Concept-to-concept relationships (PREREQUISITE, RELATED_TO, PART_OF, BUILDS_UPON)
- Stored as edge types in Neo4j
- Used for learning recommendations and prerequisite checking

#### Implementation Notes

The sync behavior is implemented in `backend/admin_content_store.py`:

```python
# Learning path creation syncs to both databases
def create_path(title, description, courses, concepts, difficulty, duration):
    # ... PostgreSQL insert ...
    pg_manager.execute_query(insert_query, ...)
    
    # ... Neo4j node creation ...
    neo4j_manager.execute_query(create_path_query, ...)
    
    # ... Concept linking in Neo4j ...
    for concept in concepts:
        neo4j_manager.execute_query(link_query, ...)
```

#### Admin Panel vs Seeder Comparison

| Item | Seeded by `seed.py` | Can Create via Admin Panel |
|------|---------------------|---------------------------|
| Concepts | ✓ Yes (11 concepts) | ✓ Yes |
| Learning Paths | ✓ Yes (4 paths) | ✓ Yes |
| Courses | ✓ Yes (5 courses) | ✓ Yes |
| Relationships | ✓ Yes (prerequisites, related_to) | ✓ Yes (via Relationships tab) |

---

## API Endpoints Reference

### Code Execution Endpoints

| Endpoint | Method | Required Role | Description |
|----------|--------|---------------|-------------|
| `/walker/execute_code` | POST | Any authenticated | Execute code snippet |
| `/walker/execute_batch` | POST | Any authenticated | Execute multiple snippets |
| `/walker/snippet_versions` | GET | Any authenticated | List snippet versions |
| `/walker/snippet_versions` | POST | Any authenticated | Create new version |
| `/walker/snippet_versions/{id}` | GET | Any authenticated | Get version details |
| `/walker/snippet_rollback` | POST | Any authenticated | Rollback to version |
| `/walker/snippet_compare` | POST | Any authenticated | Compare two versions |
| `/walker/test_cases` | GET | Any authenticated | List test cases |
| `/walker/test_cases` | POST | Any authenticated | Create test case |
| `/walker/run_test_case` | POST | Any authenticated | Execute single test |
| `/walker/run_tests` | POST | Any authenticated | Execute all tests |
| `/walker/debug_start` | POST | Any authenticated | Start debug session |
| `/walker/debug_end` | POST | Any authenticated | End debug session |
| `/walker/debug_breakpoints` | POST | Any authenticated | Set breakpoints |
| `/walker/debug_step_over` | POST | Any authenticated | Step over |
| `/walker/debug_step_into` | POST | Any authenticated | Step into |
| `/walker/debug_step_out` | POST | Any authenticated | Step out |
| `/walker/debug_continue` | POST | Any authenticated | Continue execution |
| `/walker/debug_state` | GET | Any authenticated | Get debug state |
| `/walker/debug_variables` | GET | Any authenticated | Get variables |
| `/walker/debug_stack` | GET | Any authenticated | Get call stack |
| `/walker/error_lookup` | POST | Any authenticated | Lookup error solutions |
| `/walker/error_submit` | POST | Any authenticated | Submit new error pattern |
| `/walker/admin_errors` | GET | content_admin | Manage error knowledge base |

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

---

## AI Quiz Generation Flow

The Jeseci Smart Learning Academy includes an AI-powered quiz generation system that automatically creates multiple-choice quizzes based on specified topics and difficulty levels. This section documents the complete flow from user request to quiz creation and storage.

### Overview

The quiz generation system leverages OpenAI's language models to produce high-quality educational quizzes with questions, answer options, correct answers, and explanatory notes. The system handles the complete lifecycle of quiz generation including prompt construction, API communication, response parsing, and persistent storage. This enables content administrators to rapidly expand the quiz inventory with consistent, well-structured assessments covering various programming concepts and technical topics.

### Request Flow

```
Content Administrator
        │
        ▼
Frontend Quiz Manager Form
  - Topic: "JAC Variables"
  - Difficulty: "beginner"
  - Question Count: 5
        │
        ▼
POST /walker/admin_quizzes_generate_ai
  Headers: Authorization: Bearer {JWT}
  Body: {
    "topic": "JAC Variables",
    "difficulty": "beginner",
    "question_count": 5
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
  - Build system prompt with quiz guidelines
  - Insert user parameters (topic, difficulty, question_count)
  - Specify output format (JSON with questions and answers)
        │
                  ▼
         OpenAI API Call
  - Endpoint: https://api.openai.com/v1/chat/completions
  - Model: gpt-4o-mini
  - Max tokens: 2000
  - Temperature: 0.7
        │
                  ▼
         Response Processing
  - Parse JSON from AI response
  - Extract questions, options, correct answers
  - Generate unique quiz_id
        │
                  ▼
         Database Storage
  - INSERT INTO quizzes
  - INSERT INTO quiz_questions (for each question)
  - Return generated quiz
        │
                  ▼
         Frontend Display
  - Show generated questions
  - Display options and explanations
  - Enable save/edit actions
```

### Database Storage

**Quizzes Table**:

```sql
CREATE TABLE jeseci_academy.quizzes (
    quiz_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    concept_id VARCHAR(100),
    passing_score INTEGER DEFAULT 70,
    time_limit_minutes INTEGER,
    max_attempts INTEGER DEFAULT 3,
    is_published BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(64),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Quiz Questions Table**:

```sql
CREATE TABLE jeseci_academy.quiz_questions (
    id SERIAL PRIMARY KEY,
    question_id VARCHAR(100) UNIQUE NOT NULL,
    quiz_id VARCHAR(100) REFERENCES jeseci_academy.quizzes(quiz_id),
    question TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_answer INTEGER NOT NULL,
    explanation TEXT,
    order_index INTEGER DEFAULT 0,
    points INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Content View Tracking

### Overview

The content view tracking system monitors and records how users interact with educational content throughout the platform. This data powers analytics dashboards, enables personalized recommendations, and provides insights into content performance and user engagement patterns.

### Recording Content Views

**Endpoint**: `POST /walker/record_content_view`

Records a single content view event with optional engagement metrics.

```bash
curl -X POST http://localhost:8000/walker/record_content_view \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "course_jac_fundamentals",
    "content_type": "course",
    "user_id": "user123",
    "session_id": null,
    "view_duration": 300,
    "device_type": "desktop",
    "browser": "Chrome"
  }'
```

---

## Security Considerations

### Role-Based Access Control (RBAC)

The system implements robust RBAC with the following principles:

1. **Principle of Least Privilege**: Users receive only the permissions necessary for their role
2. **Hierarchical Inheritance**: Higher roles automatically include lower-level permissions
3. **Centralized Permission Checks**: All permission checks go through `AdminRole.has_permission()`
4. **Database-Level Enforcement**: Database queries also respect role restrictions

### Code Execution Security

The Code Execution Engine implements additional security measures:

- **Sandboxed Execution**: Code runs in isolated containers with resource limits
- **Timeout Enforcement**: Maximum execution time prevents infinite loops
- **Memory Limits**: Memory quotas prevent excessive resource consumption
- **Network Restrictions**: No external network access from executing code
- **Input Validation**: All inputs are sanitized before execution

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

### Adding New Error Patterns

To extend the error knowledge base:

1. **Gather error information**:
   - Error type and category
   - Error pattern or message format
   - Language specificity
   - Severity level

2. **Create solution entry**:
   - Clear title and explanation
   - Detailed fix description
   - Code example demonstrating the fix
   - Confidence score based on frequency

3. **Add via admin endpoint**:
   ```bash
   POST /walker/admin_errors
   {
     "error_type": "CustomError",
     "error_pattern": "Custom error message pattern",
     "language": "python",
     "category": "Runtime Errors"
   }
   ```

4. **Add solution via admin endpoint**:
   ```bash
   POST /walker/admin_solutions
   {
     "error_id": "error_id_from_previous_call",
     "title": "Solution Title",
     "explanation": "Detailed explanation of the solution",
     "code_example": "Corrected code example",
     "fix_description": "How to apply the fix"
   }
   ```

---

## Related Documentation

- [Architecture Documentation Summary](ARCHITECTURE_DOCUMENTATION_SUMMARY.md)
- [Database Architecture](database-architecture.md)
- [API Reference](api_reference.md)
- [Admin Interface Design](ADMIN_INTERFACE_DESIGN.md)
- [Admin Interface Implementation](ADMIN_INTERFACE_IMPLEMENTATION.md)
- [Frontend Defensive Patterns Guide](../architecture/FRONTEND_DEFENSIVE_PATTERNS_GUIDE.md)

---

## User Views, Access, and User Flow

### Regular Users (Student Portal)

#### Student Portal Views

**Dashboard View**: The landing page for all regular users upon login displays a personalized overview of their learning progress, recommended content, and upcoming activities.

**Courses View**: This view presents a catalog of available courses organized by categories, difficulty levels, and learning paths.

**Concepts View**: The concepts view provides access to individual learning modules that cover specific topics within courses.

**Learning Paths View**: This view displays curated sequences of concepts and courses designed to achieve specific learning objectives.

**Profile View**: The profile section allows students to manage their account information, learning preferences, and personal settings.

**AI Lab View**: The AI Lab provides intelligent features including personalized concept recommendations, quiz generation, and adaptive learning assistance.

#### Code Editor Access

Students access the Code Editor through interactive coding exercises and practice problems. The editor provides:

- Language selection (Python, JavaScript, Jac)
- Code execution with instant feedback
- Test case validation
- Debugging capabilities
- Version history for reviewing progress

### Admin Users (Admin Portal)

#### Admin Dashboard Views

**Dashboard Overview**: The main admin dashboard presents system-wide statistics and health indicators.

**Users Management View**: This view enables administrators to manage all user accounts in the system.

**Content Management View**: The content manager provides access to all educational materials including courses, concepts, and learning paths.

**Quiz Management View**: This view presents the quiz database with options to create, edit, and delete quiz content.

**AI Lab View**: The admin AI Lab provides access to system intelligence features including recommendation algorithms, content analysis tools, and adaptive learning configuration.

**Analytics Reports View**: Comprehensive analytics dashboards present detailed reports on user behavior, content performance, and platform utilization.

#### Admin Access to Code Execution Features

Content administrators have access to:

- Creating and managing test cases for coding exercises
- Managing the error knowledge base
- Viewing debug session analytics
- Creating coding challenges with validation tests

---

## Frontend API Methods Reference

### Code Execution API Methods

| Frontend Method | Backend Walker | HTTP Endpoint | Purpose |
|-----------------|----------------|---------------|---------|
| `executeCode()` | `execute_code` | `/walker/execute_code` | Execute code snippet |
| `getSnippetVersions()` | `snippet_versions` | `/walker/snippet_versions` | List version history |
| `createSnippetVersion()` | `snippet_versions` | `/walker/snippet_versions` | Save new version |
| `rollbackSnippet()` | `snippet_rollback` | `/walker/snippet_rollback` | Restore previous version |
| `getTestCases()` | `test_cases` | `/walker/test_cases` | List test cases |
| `createTestCase()` | `test_cases` | `/walker/test_cases` | Create test case |
| `runTest()` | `run_test_case` | `/walker/run_test_case` | Execute single test |
| `runTests()` | `run_tests` | `/walker/run_tests` | Run all tests |
| `startDebugSession()` | `debug_start` | `/walker/debug_start` | Initialize debugging |
| `endDebugSession()` | `debug_end` | `/walker/debug_end` | End debugging |
| `setBreakpoints()` | `debug_breakpoints` | `/walker/debug_breakpoints` | Configure breakpoints |
| `stepOver()` | `debug_step_over` | `/walker/debug_step_over` | Step over line |
| `stepInto()` | `debug_step_into` | `/walker/debug_step_into` | Step into function |
| `stepOut()` | `debug_step_out` | `/walker/debug_step_out` | Step out of function |
| `continueDebug()` | `debug_continue` | `/walker/debug_continue` | Continue execution |
| `getDebugState()` | `debug_state` | `/walker/debug_state` | Get debug information |
| `lookupError()` | `error_lookup` | `/walker/error_lookup` | Find error solutions |

---

## Document Information

| Property | Value |
|----------|-------|
| **Last Updated** | 2026-01-03 |
| **Author** | Development Team |
| **Version** | 1.4 |
| **Status** | Active |
| **Changes** | Added complete Code Execution Engine documentation including multi-language support, version history, test case management, debug sessions, and error knowledge base |

---

*This documentation is maintained as part of the Jeseci Smart Learning Academy project. For updates or corrections, please submit a pull request or contact the development team.*


---

## 23. Database Module Guide

### Overview

The `backend/database/database.jac` module provides database connectivity for PostgreSQL and Neo4j through Python integration. It wraps Python database connection managers with Jaclang-compatible interfaces, enabling the application to work with both relational and graph databases seamlessly. This module is the foundation for all persistent data operations in the Jeseci Smart Learning Academy platform, handling everything from user management to learning path tracking and code snippet storage.

### Module Structure

The database module is structured around several key components that work together to provide a unified interface for database operations. Understanding this structure is essential for effective development and debugging. The module leverages Python's robust database connectivity through SQLAlchemy for PostgreSQL and the official Neo4j driver for graph operations, while exposing a clean Jaclang interface for use throughout the application.

**Database Nodes**

The module defines several node types that represent different aspects of the database system. These nodes serve as data containers and configuration holders, enabling type-safe and structured data management throughout the application. Each node type corresponds to a specific domain of the application's data model, from user progress tracking to learning path management.

- **DatabaseStatus**: Tracks the connection status of both PostgreSQL and Neo4j databases, including timestamps for the last connectivity check. This node is crucial for health monitoring and connection pool management, providing real-time visibility into the availability of critical database services.
- **ConceptNode**: Represents concepts in the knowledge graph with properties for concept ID, name, display name, category, difficulty level, description, and creation timestamp. These nodes form the building blocks of the learning graph, enabling sophisticated prerequisite tracking and personalized learning recommendations.
- **LearningPathNode**: Represents learning paths in the graph with metadata including path ID, title, difficulty, estimated duration, and description. Learning paths aggregate multiple concepts into coherent learning experiences, guiding students through structured educational journeys.
- **ProgressNode**: Tracks user progress on concepts with fields for user ID, concept ID, progress percentage, mastery level, and last access timestamp. This node enables the platform to remember where each student left off and provide continuity across learning sessions.
- **DatabaseConfig**: Stores database configuration parameters such as PostgreSQL host, port, database name, Neo4j URI, and database name. This configuration node centralizes all connection parameters, making it easy to modify database settings without searching through multiple files.

**Main Walker: DatabaseManager**

The `DatabaseManager` walker provides all database operations for the application. This walker must be imported and instantiated to perform database operations. The walker encapsulates all the complex logic required for database interactions, presenting a simple and consistent interface for common operations. All database operations flow through this walker, ensuring centralized error handling, connection management, and transaction control.

### Importing the Database Module

To use database functionality in your Jaclang code, import the database manager as follows. This import statement makes all database capabilities available within your module, enabling immediate access to connection management, query execution, and data manipulation operations. The import pattern follows Jaclang's standard module import conventions, ensuring consistency across the codebase.

```jac
import from database.database { DatabaseManager, test_db_connections }
```

The import brings in two primary entities: the `DatabaseManager` walker that handles all database operations, and the `test_db_connections` walker that provides a quick way to verify database connectivity. These two entities form the foundation of all database interactions in the application.

### Initialization

Before performing any database operations, initialize the database connections. This initialization process establishes connection pools, verifies connectivity, and prepares the database layer for operational use. Proper initialization is critical for application stability and performance, as it ensures that all database connections are ready before the first query is executed.

```jac
walker InitDatabase {
    can init with entry {
        manager = py_db.DualWriteManager();
        
        report {
            "initialized": True,
            "message": "Database module ready"
        };
    }
}
```

The initialization walker creates a `DualWriteManager` instance, which coordinates writes to both PostgreSQL and Neo4j simultaneously. This dual-write capability ensures that the relational and graph databases stay synchronized, preventing data inconsistencies that could arise from partial writes.

Alternatively, you can test connections without full initialization. This lightweight approach is useful for health checks and diagnostic purposes, allowing you to verify database availability without committing to a full initialization cycle.

```jac
walker test_db_connections {
    can run with entry {
        result = py_db.test_all_connections();
        report result;
    }
}
```

### PostgreSQL Operations

The database module supports various PostgreSQL operations through the `DatabaseManager` walker. PostgreSQL serves as the primary relational database for the application, storing user data, course information, quiz results, and other structured content. The module provides both low-level query execution and high-level convenience methods for common operations.

**Testing PostgreSQL Connection**

```jac
can test_postgresql with entry {
    result = py_db.test_all_connections();
    
    report {
        "connected": result['postgresql'],
        "database": "postgresql",
        "status": "healthy" if result['postgresql'] else "unavailable"
    };
}
```

This method performs a lightweight connectivity check against the PostgreSQL database. The check verifies that the database is accepting connections and responding to queries, providing a quick health indicator for monitoring and debugging purposes.

**Executing Custom Queries**

You can execute custom SQL queries using the `query_postgres` walker. This capability provides maximum flexibility for complex queries that go beyond the built-in convenience methods. When using custom queries, always use parameterized queries to prevent SQL injection attacks.

```jac
can query_postgres with entry {
    query = "SELECT * FROM users WHERE active = true";
    manager = py_db.get_postgres_manager();
    db_result = manager.execute_query(query, None);
    
    if db_result {
        report {
            "success": True,
            "data": db_result,
            "count": len(db_result)
        };
    } else {
        report {
            "success": False,
            "error": "Query execution failed"
        };
    }
}
```

**Storing Contact Messages**

The module provides a dedicated walker for storing contact form submissions. This demonstrates how the database module wraps common operations in convenient interfaces that handle all the details of query construction, parameter binding, and error handling.

```jac
can store_contact_message(contact_data: dict) -> dict {
    """Store contact form submission in PostgreSQL database"""
    
    try {
        manager = py_db.get_postgres_manager();
        
        # Insert contact message into database
        query = """
        INSERT INTO contact_messages (
            message_id, name, email, subject, message, phone, 
            contact_reason, timestamp, status, ip_address, user_agent
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
        ) RETURNING message_id
        """;
        
        params = (
            contact_data['message_id'],
            contact_data['name'],
            contact_data['email'],
            contact_data['subject'],
            contact_data['message'],
            contact_data['phone'],
            contact_data['contact_reason'],
            contact_data['timestamp'],
            contact_data['status'],
            contact_data['ip_address'],
            contact_data['user_agent']
        );
        
        result = manager.execute_query(query, params);
        
        if result and len(result) > 0 {
            return {
                "success": True,
                "message_id": result[0]['message_id'],
                "message": "Contact message stored successfully"
            };
        } else {
            return {
                "success": False,
                "error": "Failed to store contact message"
            };
        }
    } except (Exception as error) {
        std.out("Contact storage error:", error);
        return {
            "success": False,
            "error": "Database error: " + str(error)
        };
    }
}
```

**Retrieving Contact Messages**

To retrieve contact messages with optional filtering, use the `get_contact_messages` walker. This method supports pagination and status-based filtering, making it suitable for administrative interfaces that need to display message lists.

```jac
can get_contact_messages(params: dict) -> dict {
    """Retrieve contact messages from database with filtering"""
    
    try {
        manager = py_db.get_postgres_manager();
        
        limit = params.get('limit', 50);
        status_filter = params.get('status', 'all');
        
        # Build query based on status filter
        where_clause = "";
        query_params = [];
        
        if status_filter != 'all' {
            where_clause = "WHERE status = $1";
            query_params.append(status_filter);
        }
        
        query = f"""
        SELECT 
            message_id, name, email, subject, message, phone, 
            contact_reason, timestamp, status, ip_address, user_agent
        FROM contact_messages 
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT ${{len(query_params) + 1}}
        """;
        
        query_params.append(limit);
        
        result = manager.execute_query(query, tuple(query_params));
        
        # Get total count and unread count
        count_query = "SELECT COUNT(*) as total FROM contact_messages";
        unread_query = "SELECT COUNT(*) as unread FROM contact_messages WHERE status = 'pending'";
        
        total_result = manager.execute_query(count_query, None);
        unread_result = manager.execute_query(unread_query, None);
        
        return {
            "success": True,
            "messages": result or [],
            "total": total_result[0]['total'] if total_result else 0,
            "unread_count": unread_result[0]['unread'] if unread_result else 0
        };
        
    } except (Exception as error) {
        std.out("Contact retrieval error:", error);
        return {
            "success": False,
            "error": "Database error: " + str(error)
        };
    }
}
```

**Storing and Retrieving Testimonials**

The database module includes support for managing testimonials. This feature enables the platform to collect and display student testimonials, providing social proof that helps prospective students make enrollment decisions.

```jac
can store_testimonial(testimonial_data: dict) -> dict {
    """Store testimonial in PostgreSQL database"""
    
    try {
        manager = py_db.get_postgres_manager();
        
        query = """
        INSERT INTO testimonials (
            name, role, company, content, rating, avatar_url, 
            is_approved, is_active
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8
        ) RETURNING id
        """;
        
        params = (
            testimonial_data['name'],
            testimonial_data.get('role'),
            testimonial_data.get('company'),
            testimonial_data['content'],
            testimonial_data.get('rating', 5),
            testimonial_data.get('avatar_url'),
            testimonial_data.get('is_approved', False),
            True
        );
        
        result = manager.execute_query(query, params);
        
        if result and len(result) > 0 {
            return {
                "success": True,
                "id": result[0]['id'],
                "message": "Testimonial stored successfully"
            };
        } else {
            return {
                "success": False,
                "error": "Failed to store testimonial"
            };
        }
    } except (Exception as error) {
        std.out("Testimonial storage error:", error);
        return {
            "success": False,
            "error": "Database error: " + str(error)
        };
    }
}

can get_testimonials(params: dict) -> dict {
    """Retrieve approved testimonials from database"""
    
    try {
        manager = py_db.get_postgres_manager();
        
        query = """
        SELECT id, name, role, company, content, rating, avatar_url, created_at
        FROM testimonials 
        WHERE is_approved = true AND is_active = true
        ORDER BY created_at DESC
        """;
        
        result = manager.execute_query(query, None);
        
        return {
            "success": True,
            "testimonials": result or [],
            "total": len(result) if result else 0
        };
        
    } catch (Exception as error) {
        std.out("Testimonial retrieval error:", error);
        return {
            "success": False,
            "error": "Database error: " + str(error),
            "testimonials": []
        };
    }
}
```

### Neo4j Graph Database Operations

The module provides comprehensive support for Neo4j graph database operations. Neo4j serves as the knowledge graph layer, tracking concepts, their relationships, and student progress through the learning material. The graph-based approach enables sophisticated queries that would be difficult or impossible in a purely relational model.

**Testing Neo4j Connection**

```jac
can test_neo4j with entry {
    result = py_db.test_all_connections();
    
    report {
        "connected": result['neo4j'],
        "database": "neo4j",
        "status": "healthy" if result['neo4j'] else "unavailable"
    };
}
```

**Syncing Concepts to the Graph**

To sync a concept to the Neo4j graph, use the `sync_concept` walker. This operation creates or updates a concept node in the graph, ensuring that the knowledge representation stays synchronized with the application's understanding of each learning concept.

```jac
can sync_concept with entry {
    concept_id = "unique_concept_id";
    name = "concept_name";
    display_name = "Concept Display Name";
    category = "programming";
    difficulty_level = "intermediate";
    description = "Description of the concept";
    
    manager = py_db.get_dual_write_manager();
    sync_result = manager.sync_concept_to_neo4j(
        concept_id, name, display_name, category, difficulty_level, description
    );
    
    report {
        "success": sync_result != None,
        "operation": "sync_concept",
        "concept_id": concept_id
    };
}
```

**Creating Relationships**

Create relationships between concepts in the graph using the `create_relationship` walker. Relationships are the edges that connect concept nodes, forming the structure of the knowledge graph. Common relationship types include PREREQUISITE (indicating what must be learned first), RELATED_TO (showing topical connections), and BUILDS_UPON (indicating progressive learning paths).

```jac
can create_relationship with entry {
    source_id = "source_concept_id";
    target_id = "target_concept_id";
    relationship_type = "RELATED_TO";
    strength = 1;
    
    manager = py_db.get_dual_write_manager();
    result = manager.create_concept_relationship(
        source_id, target_id, relationship_type, strength
    );
    
    report {
        "success": result != None,
        "operation": "create_relationship",
        "source": source_id,
        "target": target_id,
        "type": relationship_type
    };
}
```

**Getting Personalized Recommendations**

Retrieve learning recommendations based on user progress using the `get_recommendations` walker. This is one of the most powerful features of the graph database integration, enabling personalized learning paths that adapt to each student's unique background and progress.

```jac
can get_recommendations with entry {
    user_id = "user_123";
    completed_ids = ["concept_1", "concept_2"];
    limit = 5;
    
    manager = py_db.get_dual_write_manager();
    result = manager.get_learning_recommendations(user_id, completed_ids, limit);
    
    report {
        "success": result != None,
        "data": result or [],
        "user_id": user_id,
        "limit": limit
    };
}
```

**Retrieving Concept Graphs**

Get a subgraph around a specific concept using the `get_concept_graph` walker. This operation is useful for visualizing the relationships surrounding a concept, enabling students to understand how concepts connect to each other in the broader learning context.

```jac
can get_concept_graph with entry {
    concept_id = "concept_1";
    depth = 2;
    
    manager = py_db.get_dual_write_manager();
    result = manager.get_concept_graph(concept_id, depth);
    
    report {
        "success": result != None,
        "data": result or [],
        "concept_id": concept_id,
        "depth": depth
    };
}
```

### Database Configuration

The default database configuration is defined in the `DatabaseConfig` node. These values represent the development environment defaults and can be overridden through environment variables in production deployments. Understanding these defaults is important for local development and testing.

- PostgreSQL Host: `localhost`
- PostgreSQL Port: `5432`
- PostgreSQL Database: `jeseci_learning_academy`
- Neo4j URI: `bolt://localhost:7687`
- Neo4j Database: `jeseci_academy`

To modify these settings, update the `DatabaseConfig` node in `database.jac` or set environment variables for your deployment environment. Environment variable overrides take precedence over the configuration file values, enabling easy configuration management across different deployment environments.

### Connection Management

**Getting Database Status**

```jac
can get_status with entry {
    result = py_db.test_all_connections();
    
    config = py_db.DatabaseConfig();
    
    report {
        "postgresql": {
            "connected": result['postgresql'],
            "host": config.postgres_host,
            "port": config.postgres_port,
            "database": config.postgres_db
        },
        "neo4j": {
            "connected": result['neo4j'],
            "uri": config.neo4j_uri,
            "database": config.neo4j_database
        }
    };
}
```

**Closing Connections**

Always close database connections when they are no longer needed. While the application typically manages connection pools that remain open between requests, explicit connection cleanup is important during application shutdown and in long-running processes to ensure proper resource release.

```jac
can close_connections with entry {
    py_db.close_all_connections();
    
    report {
        "success": True,
        "message": "All database connections closed"
    };
}
```

---

## 24. Git Workflow and Standards

### Branch Management

The project follows a standard branching strategy using Git. This strategy balances the need for collaboration with the requirement for code stability, enabling multiple developers to work simultaneously without interfering with each other's changes. The branching model is inspired by successful industry practices, particularly Git Flow, while remaining simple enough for small teams to manage effectively.

The project uses two primary branch types that serve distinct purposes in the development lifecycle. The main branch contains production-ready code that has been thoroughly tested and reviewed. All features and fixes are merged into this branch only after completing the full development and review cycle. This ensures that the main branch always represents a stable, deployable state of the codebase.

Feature branches are created from main for all new features, bug fixes, and improvements. These branches provide an isolated environment for development work, allowing developers to make multiple commits and run tests without affecting the shared codebase. Feature branches should be focused on a single change, making them easier to review and less likely to introduce conflicts.

**Branch Naming Convention**

Use kebab-case for branch names with category prefixes that clearly indicate the type of work being done. This convention makes it easy to identify the purpose of a branch at a glance, even when browsing a long list of branches. The prefix also helps organize branches in tools that group by prefix.

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feat/` | New features | `feat/user-authentication` |
| `fix/` | Bug fixes | `fix/database-connection-issue` |
| `docs/` | Documentation | `docs/update-api-documentation` |
| `refactor/` | Code refactoring | `refactor/code-snippet-manager` |
| `test/` | Test additions | `test/add-user-authentication-tests` |
| `chore/` | Maintenance tasks | `chore/update-dependencies` |

**Creating a Feature Branch**

```bash
# Ensure you're on the main branch
git checkout main

# Pull latest changes
git pull origin main

# Create a new feature branch
git checkout -b feat/new-feature-name

# Work on your feature, make commits
git add .
git commit -m "feat(feature-name): describe your changes"

# Push to remote
git push -u origin feat/new-feature-name
```

### Commit Message Standards

All commit messages must be human-readable and describe the work performed. Avoid system-generated messages that provide no meaningful information about the change. Good commit messages are essential for understanding the history of the codebase, debugging issues, and conducting effective code reviews.

**Commit Message Format**

```
<type>(<scope>): <description>
```

The format consists of three components: the type prefix that categorizes the change, an optional scope that identifies the affected module or component, and a concise description of what changed. This structured format enables automatic generation of changelogs and provides consistent, searchable commit messages.

**Type Prefixes**

The type prefix categorizes the nature of the change. Each type serves a specific purpose and helps maintain a clear commit history. Using the correct prefix makes it easier to find related changes and understand the evolution of the codebase.

| Type | Description | Examples |
|------|-------------|----------|
| `feat` | A new feature | New user authentication, additional report type |
| `fix` | A bug fix | Resolve null pointer exception, fix calculation error |
| `docs` | Documentation changes | Update API docs, add code comments |
| `style` | Formatting changes | Fix indentation, rename variables for clarity |
| `refactor` | Code changes that neither fix bugs nor add features | Extract method, simplify logic |
| `perf` | Performance improvements | Optimize query, reduce memory usage |
| `test` | Adding or modifying tests | Add unit tests, fix flaky test |
| `chore` | Maintenance tasks | Update dependencies, configure CI pipeline |

**Good Commit Message Examples**

```
feat(auth): add user registration with email verification
fix(database): resolve connection timeout issue in production
docs(api): update endpoint documentation for user profile
refactor(frontend): optimize code snippet manager rendering
test(api): add integration tests for authentication flow
chore(deps): update React to latest stable version
```

**Bad Commit Message Examples**

```
feat: update stuff
fix: bug fixes
Merge branch 'main' of github.com:repo/project
Message: update
```

### Author Attribution

All commits in this project are authored by **OumaCavin** (GitHub username). The git configuration ensures consistent attribution across all development work, maintaining a clear record of who made each change. This attribution is important for code review, accountability, and understanding the evolution of the codebase.

**Git Configuration Commands**

```bash
# Set user name
git config user.name "OumaCavin"

# Set user email
git config user.email "cavin.otieno012@gmail.com"

# Verify configuration
git config --get user.name
git config --get user.email

# Set main as default branch for new repos
git branch -M main

# Set push default to simple (pushes only current branch)
git config push.default simple

# Configure line ending handling (recommended for cross-platform)
git config core.autocrlf input
```

### Pushing Changes

When pushing changes to the remote repository, follow a consistent workflow that ensures all changes are properly staged and reviewed before becoming part of the shared codebase. The push operation transfers your local commits to the remote repository, making them available to other team members.

**Standard Push Workflow**

```bash
# Stage all changes
git add .

# Verify staged changes
git status

# Create a descriptive commit message
git commit -m "feat(frontend): add saved content library component"

# Push to main branch
git push -u origin main
```

**Using Personal Access Token**

For this project, you can use a Personal Access Token (PAT) directly in the push command. This approach is useful for automated scripts or when configuring CI/CD pipelines that need to push changes. The token should be treated as a secret and never committed to the repository.

```bash
# Push with PAT embedded in URL
git push https://[PAT]@github.com/username/repository.git main
```

**Pull Request Workflow**

For significant changes, create a pull request rather than pushing directly to main. Pull requests enable code review, discussion, and automated testing before changes are merged into the main branch.

1. Push your feature branch to the remote repository
2. Navigate to the repository on GitHub
3. Click "New Pull Request"
4. Select your feature branch as the source
5. Add a descriptive title and detailed description
6. Request review from relevant team members
7. Address review feedback and make additional commits if needed
8. Merge the pull request once approved

### Repository Exclusions

The following directories and files are excluded from git tracking and should not be committed to the repository. These exclusions prevent accidental commits of sensitive data, temporary files, and development artifacts that have no place in the version-controlled codebase.

| Item | Type | Reason |
|------|------|--------|
| `browser/` | Directory | Browser automation files and test artifacts |
| `tmp/` | Directory | Temporary working directory for intermediate files |
| `workspace.json` | File | Local workspace configuration |
| `user_input_files/` | Directory | User-provided input files |

These exclusions are configured in the `.gitignore` file to prevent accidental commits of sensitive or temporary data. The .gitignore file uses glob patterns to match files and directories that should be excluded from version control.

**.gitignore Configuration**

```gitignore
# Browser automation files
browser/

# Temporary working directory
tmp/

# Workspace configuration (local only)
workspace.json

# User input files directory
user_input_files/

# Python artifacts
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Node.js artifacts
node_modules/
npm-debug.log

# IDE configuration
.idea/
.vscode/
*.swp
*.swo

# OS artifacts
.DS_Store
Thumbs.db
```

---

## 25. Development Workflow

### Setting Up Development Environment

Follow these steps to set up a complete development environment for the Jeseci Smart Learning Academy project. This setup process prepares both the backend and frontend components for local development, testing, and debugging.

1. **Clone the Repository**

```bash
# Clone the repository
git clone https://github.com/your-username/jeseci-learning-academy.git
cd jeseci-learning-academy
```

2. **Install Backend Dependencies**

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

3. **Install Frontend Dependencies**

```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install
```

4. **Configure Database Connections**

Create a `.env` file in the backend directory with your database configuration:

```env
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jeseci_learning_academy
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Application Configuration
JWT_SECRET=your-jwt-secret-key
OPENAI_API_KEY=your-openai-api-key
```

5. **Initialize Database Schemas**

```bash
cd backend
python -m database.initialize_database
```

### Running the Application

**Backend Server**

```bash
cd backend
jac run app.jac
```

The backend server will start on port 8000 by default. You can access the API documentation at `http://localhost:8000/docs` when the server is running.

**Frontend Development Server**

```bash
cd frontend
npm start
```

The frontend development server will start on port 3000 and open automatically in your default browser. The server supports hot reloading, automatically refreshing the browser when you save changes.

### Testing

The project includes comprehensive test coverage for both backend and frontend components. Running tests regularly helps catch regressions and ensures that new changes don't break existing functionality.

**Backend Tests**

```bash
cd backend
python -m pytest tests/
```

**Frontend Tests**

```bash
cd frontend
npm test
```

### Code Review

Before merging changes, ensure they meet the project's quality standards. Code review is a collaborative process that improves code quality, shares knowledge among team members, and maintains consistency across the codebase.

**Pre-merge Checklist**

- All tests pass locally and in CI
- Code follows project conventions and style guidelines
- Commit messages are descriptive and follow the standard format
- Changes are properly documented with comments
- No sensitive data or secrets are included
- Relevant documentation is updated

## 26. Database Migration Management

### Overview

The Jeseci Smart Learning Academy includes an automatic database migration system that ensures the database schema remains synchronized with the application's requirements as the project evolves. Migrations are SQL scripts that modify the database structure, such as creating new tables, adding columns, or changing relationships between existing tables. The migration system tracks which migrations have been applied, preventing duplicate execution and ensuring that each database schema change is applied exactly once in the correct order.

This automatic migration feature is critical for maintaining consistency across different environments, including development, testing, and production deployments. When new team members set up their local environments or when new instances are deployed, the migration system automatically applies all pending schema changes without requiring manual intervention. This approach eliminates the common problem of database schema drift, where different environments fall out of sync due to missed manual schema updates.

### Migration File Organization

All database migration files are stored in the `backend/migrations/` directory. Each migration file follows a strict naming convention that ensures proper ordering during execution. The naming pattern consists of a three-digit numeric prefix followed by an underscore and a descriptive name ending with the `.sql` extension. This numeric prefix determines the order in which migrations are applied, with lower numbers executing before higher numbers.

The current migration files in the system include five migrations that establish various platform features. The first migration creates the sync engine tables that enable the dual-write functionality between PostgreSQL and Neo4j databases. The second migration establishes the testimonials table for storing user testimonials, while the third migration creates the notifications system including tables for user notifications and notification preferences. The fourth migration adds the user activities table for tracking user actions and engagement metrics, and the fifth migration further enhances the testimonials functionality.

**Migration Files Location**: `backend/migrations/`

**Naming Convention**: `{NNN}_descriptive_name.sql`

**Available Migrations**:

| File | Purpose |
|------|---------|
| `001_create_sync_engine_tables.sql` | Creates tables for dual-write synchronization between PostgreSQL and Neo4j |
| `002_create_testimonials_table.sql` | Establishes the testimonials table for user testimonials |
| `003_create_notifications_tables.sql` | Creates notifications and notification_preferences tables |
| `004_create_user_activities_table.sql` | Adds user activity tracking tables |
| `005_create_testimonials_table.sql` | Additional testimonials enhancements |

### Migration Tracking System

The migration system maintains a `schema_migrations` table in the database to track which migrations have been executed. This tracking table is automatically created if it does not exist when the first migration runs. The table records the filename of each applied migration along with a timestamp indicating when the migration was executed. This information allows the system to identify which migrations are pending and skip those that have already been applied.

**Schema Migrations Table Structure**:

```sql
CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

When migrations are executed, the system queries this table to determine which migrations have already been applied. Any migration file that does not appear in this table is considered pending and will be executed in order. After a migration is successfully executed, its name is inserted into the tracking table, ensuring it will not be run again in subsequent startup cycles. This mechanism provides idempotency, meaning the migration system can be run multiple times without causing errors or duplicate schema changes.

### Automatic Migration Execution

Database migrations are automatically executed when the backend application starts up. The migration function is defined in `backend/database/__init__.py` and is called when the database module is imported. This integration ensures that migrations run before any application code attempts to use the database, guaranteeing that the schema is always up to date when the application begins processing requests.

The automatic migration process follows a defined sequence of operations. First, the system identifies all SQL files in the migrations directory that match the naming pattern. These files are sorted alphabetically, which effectively orders them by their numeric prefixes. Next, the system establishes a database connection and creates the schema migrations tracking table if it does not already exist. The system then queries the tracking table to determine which migrations have already been applied, filtering the list to include only pending migrations.

For each pending migration, the system reads the SQL file, executes its contents against the database, commits the transaction, and records the migration name in the tracking table. All of these operations are wrapped in appropriate error handling that captures any exceptions, logs the error details, and rolls back the transaction to maintain database integrity. If the database is temporarily unavailable during startup, the migration call is wrapped in a try-except block that logs a warning and allows the application to continue starting, deferring migration execution until the database becomes available.

**Migration Execution Location**: `backend/database/__init__.py`

**Automatic Execution Point**: Module import in `backend/database/__init__.py`

**Startup Behavior**:

```python
# Auto-run migrations on module import
# This ensures database schema is up to date when the application starts
try:
    run_database_migrations()
except Exception as e:
    logger.warning(f"Initial migration attempt deferred: {e}")
```

### Adding New Migrations

When the application requires database schema changes, a new migration file should be created following the established conventions. The migration file must be placed in the `backend/migrations/` directory with a numeric prefix that places it in the correct execution order relative to existing migrations. The prefix should use three digits, starting from 001 and incrementing for each new migration.

To create a new migration, follow these steps. First, determine the appropriate numeric prefix for your migration by examining the existing migration files and choosing the next available number. Second, create a new SQL file with the appropriate name, such as `006_add_user_sessions_table.sql`. Third, write the SQL statements required to implement your schema change, including CREATE TABLE, ALTER TABLE, or other DDL statements. Fourth, test the migration on a development database to ensure it executes correctly and produces the expected schema changes.

**Example Migration File Structure**:

```sql
-- Migration: Add user sessions table
-- Purpose: Tracks user login sessions for security and analytics
-- Executed: Automatically on application startup

CREATE TABLE jeseci_academy.user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES jeseci_academy.users(id),
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_user_sessions_user_id ON jeseci_academy.user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON jeseci_academy.user_sessions(expires_at);
```

Each migration file should include comments documenting its purpose and any important notes about the schema changes it implements. This documentation helps future developers understand the evolution of the database schema and provides context for maintenance and troubleshooting activities. Migrations should be focused and atomic, implementing a single logical change rather than combining multiple unrelated schema modifications.

### Migration Best Practices

Following established best practices for database migrations ensures the stability and maintainability of the application's database layer. Migration files should be written to be idempotent whenever possible, meaning they can be run multiple times without causing errors or unintended effects. This is particularly important for ALTER TABLE operations, where the same column or constraint may already exist from a previous partial execution.

Always test migrations in a non-production environment before deploying them. This testing should include running the migration against a fresh database copy to verify it works correctly during initial setup, running the migration against an existing database to verify it applies cleanly to populated databases, and rolling back the migration if your database system supports rollback capabilities to ensure the reversal process works correctly.

Avoid modifying existing migration files after they have been committed and deployed. If a previously applied migration contains an error, create a new migration that corrects the issue rather than modifying the original. This approach maintains a clear audit trail of schema changes and prevents inconsistencies between environments that may have applied the migrations at different times.

---

## Document Information

| Property | Value |
|----------|-------|
| **Last Updated** | 2026-01-05 |
| **Author** | OumaCavin |
| **Version** | 1.6 |
| **Status** | Active |
| **Changes** | Added Database Migration Management documentation covering automatic migration execution, tracking system, and best practices |

---

*This documentation is maintained as part of the Jeseci Smart Learning Academy project. For updates or corrections, please submit a pull request or contact the development team.*
