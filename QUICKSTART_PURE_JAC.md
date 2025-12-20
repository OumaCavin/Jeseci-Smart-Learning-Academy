# 🚀 Pure JAC Architecture - Quick Start

## After `git pull origin main`

Run the simplified setup:

```bash
bash setup_pure_jac.sh
```

This will:
- ✅ Create/activate virtual environment
- ✅ Install JAC + OpenAI dependencies only
- ✅ Validate JAC installation
- ✅ Print next steps

## 🎯 **Why No Databases?**

### **JAC's Native Capabilities**
- **Graph Persistence**: JAC's OSP handles data natively
- **HTTP Server**: `jac serve` built-in web server
- **Session Management**: Walkers handle state
- **No External Dependencies**: Everything in JAC

## 📋 **Minimal Setup**

### Option 1: Complete Setup
```bash
bash setup_pure_jac.sh
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install JAC dependencies
pip install -r requirements_pure_jac.txt

# Start application
jac serve app.jac
```

## 🚀 **Start Application**

```bash
# Activate environment
source venv/bin/activate

# Start learning portal
jac serve app.jac

# Access at http://localhost:8000
```

## 📊 **Available Features**

### **AI-Powered Learning**
- **Content Generation**: `byLLM` decorators
- **Adaptive Quizzes**: AI-generated assessments
- **Personalized Paths**: Intelligent learning recommendations

### **Native Graph Data**
- **OSP Models**: User, Concept, Lesson nodes
- **Mastery Tracking**: Edge relationships
- **Progress Analytics**: Real-time learning data

### **API Endpoints** (Auto-generated)
- `GET /functions/register_user`
- `GET /functions/get_lesson`
- `GET /functions/generate_quiz`
- `POST /functions/submit_answer`
- `GET /functions/update_mastery`

## 🏗️ **Architecture Benefits**

- **Single Language**: Everything in JAC
- **No Database Setup**: JAC handles persistence
- **AI-First**: Native byLLM integration
- **Graph-Native**: OSP for natural data modeling
- **Built-in Server**: HTTP endpoints from walkers

## 🆘 **Troubleshooting**

### JAC Command Not Found
```bash
source venv/bin/activate
# Restart shell to update PATH
```

### OpenAI API Issues
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY
```

### Port Already in Use
```bash
# Use different port
jac serve app.jac --port 8001
```

## 📁 **Key Files**

- `app.jac` - Main JAC application with OSP models
- `requirements_pure_jac.txt` - Minimal dependencies
- `.env_pure_jac` - Environment template
- `setup_pure_jac.sh` - Simplified setup script