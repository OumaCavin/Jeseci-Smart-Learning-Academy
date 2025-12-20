# Pure JAC Architecture Setup

This directory contains all files needed for the pure JAC architecture setup of the Jeseci Smart Learning Academy.

## Files Overview

### Setup Script
- **`setup_pure_jac.sh`** - Main setup script that automates the entire setup process
  - Creates virtual environment
  - Installs dependencies
  - Configures environment
  - Validates installation

### Dependencies
- **`requirements_pure_jac.txt`** - Minimal JAC dependencies (no external databases)
  - jaclang>=0.9.3
  - jac-cloud
  - openai>=1.12.0
  - Testing and utility packages

### Environment Configuration
- **`.env_pure_jac`** - Environment template file
  - OpenAI API key configuration
  - Application settings
  - No database configurations needed

### Documentation
- **`QUICKSTART_PURE_JAC.md`** - Quick start guide for the pure JAC setup

## Usage

### From Project Root Directory

```bash
# Run the complete setup
bash docs/pure-jac/setup_pure_jac.sh

# Or manually install
python3 -m venv venv
source venv/bin/activate
pip install -r docs/pure-jac/requirements_pure_jac.txt
cp docs/pure-jac/.env_pure_jac .env
```

### Requirements

- Python 3.12+
- Git
- OpenAI API key

## Architecture Benefits

- **No External Databases**: JAC handles all data persistence natively
- **Single Language**: Everything in JAC
- **AI-Native**: Built-in byLLM integration
- **Graph-Based**: OSP for natural data modeling
- **Built-in Server**: `jac serve` provides HTTP endpoints

## Starting the Application

After setup:

```bash
# Activate environment
source venv/bin/activate

# Start the learning portal
jac serve app.jac

# Access at http://localhost:8000
```

## Available API Endpoints

Once running, these endpoints are automatically available:
- `GET /functions/register_user` - User registration
- `GET /functions/get_lesson` - Retrieve learning content
- `GET /functions/generate_quiz` - AI-generated quizzes
- `POST /functions/submit_answer` - Answer submission
- `GET /functions/update_mastery` - Progress tracking

## Notes

- This is a **minimal setup** compared to the previous hybrid architecture
- No PostgreSQL, Redis, or Neo4j required
- All AI features powered by OpenAI through byLLM
- All data persistence handled by JAC's OSP system