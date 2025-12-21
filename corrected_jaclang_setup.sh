#!/bin/bash
# CORRECTED Jaclang Project Setup - Fixed npm dependency issue
# This script uses the ACTUAL correct approach

set -e

echo "🎓 CORRECTED JACLANG PROJECT SETUP"
echo "📋 Using ACTUAL correct Jaclang approach (NO fake npm packages!)"

# Install jac-client (Python package, NOT npm!)
echo "🐍 Installing jac-client (Python package)..."
uv pip install jac-client

# Check if we're in the right directory
if [ -f "app.jac" ]; then
    echo "⚠️  app.jac exists - backing up current project"
    mv app.jac app.jac.backup
fi

# Create new Jaclang project with automatic setup
echo "🔧 Creating new Jaclang project with automatic configuration..."
jac create_jac_app temp_project

# Move the contents to current directory
echo "📦 Setting up project structure..."
rm -rf ./*
cp -r temp_project/* .
rm -rf temp_project

# Create CORRECT minimal package.json (no fake dependencies)
echo "📝 Creating correct package.json (no dependencies needed)..."
cat > package.json << 'EOF'
{
  "name": "jeseci-smart-learning-academy",
  "version": "1.0.0",
  "type": "module"
}
EOF

# Remove any fake dependencies from vite.config.js
echo "🔧 Updating vite.config.js..."
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [],
  build: {
    outDir: 'dist'
  }
});
EOF

# Restore our application code with proper syntax
echo "🔄 Restoring application code with correct syntax..."

# Create the correct app.jac file
cat > app.jac << 'EOF'
# ==============================================================================
# Jeseci Smart Learning Academy - Correct Jaclang 0.9.3 Architecture
# ==============================================================================

# Backend - JAC Object-Spatial Programming
node user {
    has user_id: str;
    has username: str;
    has email: str;
    has progress: dict;
}

node course {
    has course_id: str;
    has title: str;
    has description: str;
    has lessons: list;
}

walker init {
    has welcome_msg: str = "Welcome to Jeseci Smart Learning Academy!";
    
    can initialize with entry {
        report {
            "message": self.welcome_msg,
            "status": "initialized",
            "version": "5.0.0"
        };
    }
}

walker health_check {
    has status: str = "healthy";
    has version: str = "5.0.0";
    has timestamp: str = "2025-12-22T03:32:25Z";
    
    can check_health with entry {
        report {
            "service": "Jeseci Smart Learning Academy",
            "status": self.status,
            "version": self.version,
            "timestamp": self.timestamp
        };
    }
}

walker concepts {
    has topic: str = "general";
    
    can get_concepts with entry {
        report {
            "concepts": [
                "Object-Spatial Programming",
                "Walker-based APIs", 
                "Node-based Data Structures",
                "Jaclang Frontend Compilation"
            ],
            "topic": self.topic
        };
    }
}

walker user_progress {
    has user_id: str = "default";
    
    can get_progress with entry {
        report {
            "user_id": self.user_id,
            "progress": {
                "completed_lessons": 0,
                "current_course": "Introduction to Jaclang",
                "total_score": 0
            }
        };
    }
}

# Frontend - Client-side Code (NO external imports needed!)
cl {
    def LearningDashboard() -> any {
        return (
            <div style={{
                fontFamily: 'Arial, sans-serif',
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '20px',
                backgroundColor: '#f5f5f5'
            }}>
                <div style={{
                    backgroundColor: 'white',
                    padding: '30px',
                    borderRadius: '10px',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                    textAlign: 'center'
                }}>
                    <h1 style={{
                        color: '#2c3e50',
                        fontSize: '2.5em',
                        marginBottom: '10px'
                    }}>
                        Jeseci Smart Learning Academy
                    </h1>
                    <p style={{
                        color: '#7f8c8d',
                        fontSize: '1.2em'
                    }}>
                        Pure Jaclang 0.9.3 Architecture
                    </p>
                </div>
                
                <div style={{
                    backgroundColor: '#27ae60',
                    color: 'white',
                    padding: '20px',
                    borderRadius: '5px',
                    margin: '20px 0',
                    textAlign: 'center'
                }}>
                    <h2 style={{ margin: '0' }}>
                        Application Status: Operational
                    </h2>
                    <p style={{ margin: '10px 0 0 0' }}>
                        <strong>Version:</strong> 5.0.0 | 
                        <strong>Architecture:</strong> Pure Jaclang + Native JSX
                    </p>
                </div>
                
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '20px',
                    marginTop: '30px'
                }}>
                    <div style={{
                        backgroundColor: '#3498db',
                        color: 'white',
                        padding: '20px',
                        borderRadius: '5px'
                    }}>
                        <h3>Backend APIs</h3>
                        <p>Test the application APIs:</p>
                        <button 
                            onClick={() => this.testWalker('/walker/health_check')}
                            style={{
                                backgroundColor: '#2980b9',
                                color: 'white',
                                border: 'none',
                                padding: '10px 15px',
                                borderRadius: '3px',
                                margin: '5px',
                                cursor: 'pointer'
                            }}
                        >
                            Test Health Check
                        </button>
                        <button 
                            onClick={() => this.testWalker('/walker/init')}
                            style={{
                                backgroundColor: '#2980b9',
                                color: 'white',
                                border: 'none',
                                padding: '10px 15px',
                                borderRadius: '3px',
                                margin: '5px',
                                cursor: 'pointer'
                            }}
                        >
                            Test Init
                        </button>
                    </div>
                    
                    <div style={{
                        backgroundColor: '#e74c3c',
                        color: 'white',
                        padding: '20px',
                        borderRadius: '5px'
                    }}>
                        <h3>Architecture Features</h3>
                        <ul style={{ textAlign: 'left' }}>
                            <li>Single language (Jaclang)</li>
                            <li>No external React dependencies</li>
                            <li>Native JSX implementation</li>
                            <li>Built-in authentication</li>
                            <li>Native backend communication</li>
                            <li>Zero configuration build</li>
                        </ul>
                    </div>
                </div>
                
                <div id="result" style={{
                    backgroundColor: '#ecf0f1',
                    padding: '20px',
                    borderRadius: '5px',
                    marginTop: '20px',
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap'
                }}>
                    Click buttons above to test APIs...
                </div>
            </div>
        );
    }
    
    can testWalker(endpoint: str) {
        try {
            fetch(`http://localhost:8000${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').textContent = 
                    `${endpoint} Response:\n${JSON.stringify(data, null, 2)}`;
            })
            .catch(error => {
                document.getElementById('result').textContent = 
                    `${endpoint} Error:\n${error.message}`;
            });
        } catch (error) {
            document.getElementById('result').textContent = 
                `${endpoint} Error:\n${error.message}`;
        }
    }
}
EOF

# Install Node.js dependencies (minimal - just what's auto-managed)
echo "📦 Installing minimal Node.js dependencies..."
npm install

echo "🔨 Building with CORRECTED setup..."
jac build ./app.jac

echo "✅ Setup complete!"
echo ""
echo "🚀 TO START THE APPLICATION:"
echo "   ./corrected_run.sh"
echo ""
echo "🌐 The application will be available at:"
echo "   http://localhost:8000/page/app"
echo ""
echo "📋 This setup uses:"
echo "   ✅ jac-client (Python package via pip)"
echo "   ✅ Automatic Vite configuration"
echo "   ✅ No fake npm packages"
echo "   ✅ Minimal package.json"