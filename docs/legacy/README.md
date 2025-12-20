# Legacy Implementation Files

This directory contains files from the previous hybrid FastAPI + JAC architecture that have been moved here for historical reference and potential future use.

## Overview

The current project uses a **pure JAC architecture** with:
- Native JAC programming language
- Object-Spatial Programming (OSP) for data modeling
- byLLM decorators for AI features
- Built-in `jac serve` HTTP server

The files in this directory were used in the previous hybrid approach.

## Directory Structure

### `/setup/`
Legacy setup scripts for the hybrid architecture:
- `setup.sh` - Full setup with databases
- `setup_virtual_env.sh` - Virtual environment setup
- `setup_git.sh` - Git repository setup
- `test_phase2_agents.sh` - Agent testing
- `commit_changes.sh` and `commit_sync.sh` - Git operations

### `/config/`
Legacy configuration files:
- `requirements.txt` - Old Python dependencies (with FastAPI, SQLAlchemy, etc.)
- `.env` and `.env.template` - Environment configurations with database settings
- `__pycache__/` - Python cache files

### `/database/`
Legacy database models and migrations (SQLAlchemy-based):
- `models/` - Database models for PostgreSQL/SQLite
- Migrations using Alembic

### `/api/`
Legacy REST API endpoints (FastAPI-based):
- `v1/` - Versioned API endpoints

### `/services/`
Legacy service layer (FastAPI integration):
- AI processing agents
- Authentication services
- Content management
- Multi-agent chat system

### `/frontend/` and `/frontend-jac/`
Legacy frontend implementations:
- React-style components
- Learning dashboard components
- Interactive modules
- Authentication components

### `/docs/`
Legacy documentation files:
- Implementation summaries
- Setup guides
- API documentation
- Feature completion reports

### `/migrations/`
Legacy database migrations using Alembic

## Why These Files Were Moved

1. **Clean Project Structure**: The root directory now contains only files needed for the pure JAC architecture
2. **Historical Reference**: These files show the evolution from hybrid to pure JAC
3. **Potential Migration**: Some components might be useful for future enhancements
4. **Code Reuse**: Services or utilities from these files could be adapted for JAC

## Current Active Files

The project now uses only these files in the root:
- `app.jac` - Main JAC application
- `setup_pure_jac.sh` - Simplified setup script
- `requirements_pure_jac.txt` - Minimal dependencies
- `.env_pure_jac` - Environment template
- `README.md` - Updated documentation
- `QUICKSTART_PURE_JAC.md` - Quick start guide

## Migration Notes

### What's Different Now
- **No FastAPI**: `jac serve` handles HTTP natively
- **No SQLAlchemy**: JAC's OSP handles data persistence
- **No Redis/Neo4j**: JAC handles all data internally
- **No Database Setup**: Everything runs from JAC

### What Stayed the Same
- OpenAI integration for AI features
- Basic project structure concepts
- Educational learning portal functionality

## Future Considerations

If you need to reference any functionality from these legacy files:
1. Check the `/docs/legacy/docs/` directory for implementation details
2. Look at `/services/` for AI agent logic that might be convertible to JAC walkers
3. Review `/database/models/` for data structure ideas for OSP nodes

## Note

This legacy code is **not maintained** and should not be used for new features. The pure JAC architecture is the current and supported approach.