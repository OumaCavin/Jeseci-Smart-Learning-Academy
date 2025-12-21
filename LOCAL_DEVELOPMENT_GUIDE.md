# Jeseci Smart Learning Academy - Local Development Setup

## 🚀 Complete Setup for Local Development

### Prerequisites
- Node.js v18.19.0 or later
- npm v9.0.0 or later
- Python 3.12+ with Jaclang installed
- Git

### Installation Steps

#### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd Jeseci-Smart-Learning-Academy

# Copy the local development files
cp local_package.json package.json
cp local_vite.config.js vite.config.js
cp -r src_local src
chmod +x local_run.sh
cp local_run.sh run.sh
```

#### 2. Install Dependencies
```bash
# Install Node.js dependencies
npm install

# Install Jaclang (if not already installed)
pip install jaclang
```

#### 3. Development Workflow
```bash
# Start full development environment (frontend + backend)
./run.sh

# Or use individual commands:
npm run dev      # Start Vite frontend (port 3000)
npm run serve    # Start Jaclang backend (port 8000)
npm run full-dev # Start both concurrently
```

#### 4. Build for Production
```bash
# Build frontend and backend
npm run full-build

# Or step by step:
npm run build    # Build frontend with Vite
jac build ./app.jac  # Compile Jaclang application
jac serve app.jir    # Start production server
```

## 🌟 Architecture Overview

### Frontend (Vite + Jac-Client)
- **Framework**: Vite + React plugin for JSX compilation
- **Jac-Client**: `@jac-client/utils` for backend communication
- **Build Process**: Vite compiles the `cl {}` block from `app.jac`
- **Development**: Hot reload with Vite dev server

### Backend (Pure Jaclang)
- **Language**: Pure Jaclang 0.9.3
- **Architecture**: Object-Spatial Programming
- **APIs**: REST endpoints via walkers
- **Session**: Built-in session management

## 🔧 File Structure
```
Jeseci-Smart-Learning-Academy/
├── app.jac                    # Main Jaclang application
├── src/
│   └── client_runtime.js      # Vite entry point
├── dist/                      # Vite build output
├── vite.config.js             # Vite configuration
├── package.json               # Dependencies and scripts
├── run.sh                     # Development script
└── .venv/                     # Python virtual environment
```

## 🌐 Access Points

### Development Environment
- **Frontend**: http://localhost:3000 (Vite dev server)
- **Backend**: http://localhost:8000 (Jaclang API server)
- **Integrated**: http://localhost:3000 (proxied to backend)

### Production Environment
- **Single Server**: http://localhost:8000 (Jaclang server with Vite)
- **Static Files**: Served from `/dist/` directory
- **API Routes**: `/walker/*` and `/function/*`

## 🚀 Deployment

### Local Production
```bash
npm run full-build
jac serve app.jir  # Single server on port 8000
```

### Docker Deployment
```dockerfile
FROM node:18-alpine

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .
RUN npm run build && jac build ./app.jac

# Expose and run
EXPOSE 8000
CMD ["jac", "serve", "app.jir"]
```

## 🔍 Troubleshooting

### Common Issues

1. **Permission Denied (Vite)**
   - Ensure Node.js and npm are properly installed
   - Check file permissions: `chmod +x run.sh`

2. **Jaclang Build Errors**
   - Verify Python virtual environment is activated
   - Check Jaclang installation: `pip install --upgrade jaclang`

3. **Port Conflicts**
   - Frontend: Change port in `vite.config.js`
   - Backend: Change port in `run.sh`

4. **Jac-Client Import Errors**
   - Verify `@jac-client/utils` is installed: `npm list @jac-client/utils`
   - Check Node.js version compatibility

## 📝 Development Notes

### Frontend Development
- Use pure Jaclang `cl {}` blocks for UI components
- Leverage `@jac-client/utils` for backend communication
- Vite provides hot reload for rapid development

### Backend Development
- Define walkers for API endpoints
- Use nodes for data structures
- Leverage Jaclang's built-in session management

### Integration
- Frontend communicates with backend via `@jac-client/utils`
- Vite proxies API calls to Jaclang server
- Session state managed by Jaclang runtime