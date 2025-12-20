# Jeseci Smart Learning Academy - JAC-FastAPI Integration Guide

## 🚀 **Project Overview**

**Jeseci Smart Learning Academy** is a unified full-stack AI-powered learning platform that combines the power of **JAC programming language** with **FastAPI** for seamless backend and AI agent integration.

### **Repository Information**
- **New Repository**: `https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git`
- **Original Repository**: `https://github.com/OumaCavin/Jeseci-Smart-Learning-Companion.git`
- **Git Branch**: `main`
- **Author**: Cavin Otieno
- **Email**: cavin.otieno012@gmail.com

## 🏗️ **Architecture Overview**

### **Full Stack JAC Implementation**

The Academy project follows the **official Jaseci full-stack development approach**:

```
┌─────────────────────────────────────────────────────────────┐
│                    JAC Full Stack Architecture              │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Jac Compiled)     │  Backend (JAC + FastAPI)     │
│  ┌─────────────────────────┐  │  ┌─────────────────────────┐ │
│  │ • HTML/CSS/JavaScript   │  │  │ • FastAPI (Python)      │ │
│  │ • Jac Compiled to JS    │  │  │ • JAC AI Agents         │ │
│  │ • Interactive UI        │  │  │ • PostgreSQL            │ │
│  │ • Real-time Updates     │  │  │ • Redis Caching         │ │
│  └─────────────────────────┘  │  │ • Neo4j Knowledge Graph │ │
│                              │  └─────────────────────────┘ │
│  JAC Runtime                  │                              │
│  ┌─────────────────────────┐  │  ┌─────────────────────────┐ │
│  │ • JAC Compiler          │  │  │ • AI Processing Agents  │ │
│  │ • Object-Spatial Progr. │  │  │ • Service Orchestrator  │ │
│  │ • AI-First Constructs   │  │  │ • Content Curators      │ │
│  │ • Scale-Native Features │  │  │ • Progress Trackers     │ │
│  └─────────────────────────┘  │  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🤖 **JAC-FastAPI Integration**

### **What Was Implemented**

1. **JAC-FastAPI Bridge** (`services/jac_fastapi_bridge.py`)
   - Unified interface between JAC services and FastAPI
   - Automatic JAC service registration and management
   - Python fallback when JAC compiler unavailable
   - Service execution engine with monitoring

2. **Integrated JAC Services**
   - **System Orchestrator**: Central multi-agent coordination
   - **Base Agent**: Shared functionality foundation
   - **AI Processing Agent**: AI request handling
   - **Content Curator**: Learning content management
   - **Learning Service**: Learning session management
   - **Progress Tracker**: Learning progress monitoring
   - **Quiz Master**: Assessment generation
   - **Evaluator**: Performance analysis
   **Motivator**: User engagement and motivation
   - **Multi-Agent Chat**: Agent conversation management

3. **FastAPI Integration Points**
   - `/api/v1/jac/services/status` - All services status
   - `/api/v1/jac/services/{service_name}/status` - Individual service status
   - `/api/v1/jac/services/execute` - Execute JAC services
   - `/api/v1/jac/initialize` - Initialize JAC runtime

### **Integration Architecture**

```python
# JAC-FastAPI Bridge Structure
class JACFastAPIBridge:
    def __init__(self, app: FastAPI):
        self.app = app
        self.jac_services: Dict[str, JACServiceConfig] = {}
        self.service_registry: Dict[str, Any] = {}
        self.jac_runtime = None
        self.is_initialized = False
    
    # Core Methods:
    async def initialize_jac_runtime() -> bool
    async def execute_jac_service(request: JACExecutionRequest) -> JACExecutionResponse
    async def get_all_services_status() -> Dict[str, Any]
```

## 🗄️ **Database Configuration**

### **Academy vs Companion Database Separation**

| Service | Companion Project | Academy Project |
|---------|------------------|-----------------|
| **PostgreSQL** | `jeseci_learning_companion` | `jeseci_learning_academy` |
| **Redis** | Database 0 | Database 1 |
| **Neo4j** | `neo4j` database | `jeseci_academy` database |

### **Connection Commands**

#### **Academy Project Database Access**
```bash
# PostgreSQL - Academy
psql -h localhost -U jeseci_user -d jeseci_learning_academy

# Redis - Academy (Database 1)
redis-cli -n 1 ping

# Neo4j - Academy
cypher-shell -u neo4j -p neo4j_secure_password_2024 -d jeseci_academy
```

#### **Companion Project Database Access** (unchanged)
```bash
# PostgreSQL - Companion
psql -h localhost -U jeseci_user -d jeseci_learning_companion

# Redis - Companion (Database 0)
redis-cli ping

# Neo4j - Companion
cypher-shell -u neo4j -p neo4j_secure_password_2024
```

## 🔧 **Environment Configuration**

### **Updated .env for Academy**

```env
# Database Configuration
POSTGRES_DB=jeseci_learning_academy
REDIS_DB=1

# Project Configuration
PROJECT_NAME="Jeseci Smart Learning Academy"

# JAC Configuration
ENVIRONMENT=development
JAC_RUNTIME_ENABLED=true
JAC_SERVICES_ENABLED=true
```

## 📋 **JAC Service Implementation Status**

### ✅ **Working Components**
- [x] JAC-FastAPI bridge integration
- [x] Service registry and management
- [x] JAC service execution engine
- [x] Python fallback when JAC unavailable
- [x] Service health monitoring
- [x] Database integration (PostgreSQL, Redis, Neo4j)
- [x] FastAPI endpoints for JAC services

### 🔄 **JAC Compiler Integration**
- [ ] Direct JAC compilation (requires JAC v0.9.3 installation)
- [ ] JAC service execution in JAC runtime
- [ ] Object-spatial programming features
- [ ] AI-first construct utilization

### 📝 **Next Steps for Full JAC Integration**

1. **Install JAC Compiler**
   ```bash
   pip install "jaclang>=0.9.3"
   ```

2. **Test JAC Services**
   ```bash
   # Test JAC service execution
   curl -X POST http://localhost:8000/api/v1/jac/services/execute \
        -H "Content-Type: application/json" \
        -d '{
          "service_name": "system_orchestrator",
          "walker_name": "system_orchestrator",
          "entry_point": "initialize_learning_session",
          "parameters": {"user_id": "test_user"}
        }'
   ```

3. **Monitor JAC Services**
   ```bash
   # Check all services status
   curl http://localhost:8000/api/v1/jac/services/status
   ```

## 🚀 **Running the Academy Project**

### **Development Setup**

1. **Clone Repository**
   ```bash
   git clone https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy.git
   cd Jeseci-Smart-Learning-Academy
   ```

2. **Environment Setup**
   ```bash
   # Create database
   createdb -U jeseci_user jeseci_learning_academy
   
   # Setup Neo4j database
   # Open http://localhost:7474 and run:
   # CREATE DATABASE jeseci_academy
   ```

3. **Install Dependencies**
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # JAC compiler (optional for full JAC support)
   pip install "jaclang>=0.9.3"
   ```

4. **Run Application**
   ```bash
   # Start FastAPI server
   uvicorn main:app --reload --port 8000
   
   # Or use the main JAC application
   jac serve app.jac
   ```

### **API Endpoints**

- **Root**: `http://localhost:8000/`
- **API Docs**: `http://localhost:8000/docs`
- **JAC Services**: `http://localhost:8000/api/v1/jac/services/`
- **Health Check**: `http://localhost:8000/health`

## 📊 **Service Architecture**

### **JAC Services Integration**

Each JAC service follows this pattern:

```python
# Service Configuration
JACServiceConfig(
    service_name="service_name",
    jac_file_path="services/service_name.jac",
    walker_name="walker_name",
    entry_point="function_name",
    enabled=True
)

# Service Response Format
{
    "success": True,
    "result": {
        "status": "success",
        "service_specific_data": "..."
    },
    "execution_time": 0.145,
    "service_name": "service_name"
}
```

## 🎯 **Key Benefits of JAC-FastAPI Integration**

1. **Unified Development**: Single codebase for frontend and backend
2. **AI-First Architecture**: Native support for AI agents and services
3. **Scalable Microservices**: Each JAC service is independently scalable
4. **Database Flexibility**: Support for multiple database types
5. **Real-time Capabilities**: Built-in support for real-time updates
6. **Performance Monitoring**: Integrated service health and performance tracking

## 📝 **Development Guidelines**

### **Commit Message Standards**
- Use human-readable commit messages
- Format: `type(scope): description`
- Examples:
  - `feat(jac-integration): add AI processing agent`
  - `fix(api): resolve JAC service execution timeout`
  - `docs(api): update JAC integration guide`

### **JAC Service Development**
1. Create JAC file in `services/` directory
2. Define walker with proper entry points
3. Register service in `jac_fastapi_bridge.py`
4. Test integration through FastAPI endpoints

### **Python Integration**
- JAC services can be called from Python
- Python functions can be called from JAC
- Shared data models between JAC and Python
- Unified error handling and logging

## 🛠️ **Troubleshooting**

### **JAC Not Available**
- System automatically falls back to Python implementation
- Check logs for JAC compiler availability
- Install JAC: `pip install "jaclang>=0.9.3"`

### **Database Connection Issues**
- Verify PostgreSQL, Redis, Neo4j are running
- Check database names match configuration
- Test connections using provided commands

### **Service Execution Failures**
- Check service status endpoint
- Verify JAC service file exists
- Review service-specific error logs

---

**Author**: Cavin Otieno  
**Repository**: https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy  
**Last Updated**: December 20, 2025