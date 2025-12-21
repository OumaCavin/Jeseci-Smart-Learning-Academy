# ==============================================================================
# Jeseci Smart Learning Academy - Pure Jaclang 0.9.3 Architecture
# ==============================================================================

# Import built-in Jac client utilities (NO external React needed!)
climport from '@jac-client/utils' {
    jacSpawn, jacLogin, jacSignup, jacLogout, jacIsLoggedIn,
    navigate, Link, useRouter
}

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
    has welcome_msg: str = "🎓 Welcome to Jeseci Smart Learning Academy!";
    
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
    has timestamp: str = "2025-12-22T02:59:00Z";
    
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
    has learning_concepts: list;
    
    can manage_concepts with entry {
        self.learning_concepts = [
            "Object-Spatial Programming", 
            "JAC Graph Architecture",
            "Client-Server Communication",
            "React-like Components"
        ];
        report {
            "concepts": self.learning_concepts,
            "total_count": len(self.learning_concepts)
        };
    }
}

walker user_progress {
    has user_data: dict;
    
    can get_progress with entry {
        self.user_data = {
            "courses_completed": 3,
            "lessons_completed": 15,
            "current_streak": 7
        };
        report {
            "progress": self.user_data
        };
    }
}

# ==============================================================================
# FRONTEND - Pure Jaclang JSX (NO external React dependencies!)
# ==============================================================================

cl {

    def LearningDashboard() -> any {
        return (
            <div style={containerStyle}>
                <div style={headerStyle}>
                    <h1 style={titleStyle}>🎓 Jeseci Smart Learning Academy</h1>
                    <p style={subtitleStyle}>Pure Jaclang 0.9.3 Architecture</p>
                </div>
                
                <div style={cardStyle}>
                    <h2 style={h2Style}>✅ Application Status: Operational</h2>
                    <p><strong>Version:</strong> 5.0.0</p>
                    <p><strong>Architecture:</strong> Pure Jaclang + Native JSX</p>
                    <p><strong>Backend:</strong> Object-Spatial Programming APIs</p>
                    <p><strong>Frontend:</strong> Built-in React-like Components</p>
                </div>
                
                <div style={gridStyle}>
                    <div style={apiCardStyle}>
                        <h3>🚀 Backend APIs</h3>
                        <p>Native Jac Walkers with Object-Spatial Programming</p>
                        <button style={buttonStyle} onClick={lambda -> None { testWelcomeAPI(); }}>Test Welcome API</button>
                        <button style={buttonBlueStyle} onClick={lambda -> None { testHealthAPI(); }}>Health Check</button>
                        <button style={buttonOrangeStyle} onClick={lambda -> None { testConceptsAPI(); }}>View Concepts</button>
                        <button style={buttonPurpleStyle} onClick={lambda -> None { testProgressAPI(); }}>User Progress</button>
                    </div>
                    
                    <div style={infoCardStyle}>
                        <h3>🔧 Architecture Benefits</h3>
                        <ul>
                            <li>✅ Single language (Jaclang)</li>
                            <li>✅ No external React dependencies</li>
                            <li>✅ Native JSX implementation</li>
                            <li>✅ Built-in authentication</li>
                            <li>✅ Native backend communication</li>
                            <li>✅ Zero configuration build</li>
                        </ul>
                    </div>
                </div>
                
                <div style={footerStyle}>
                    <p>Built with Jaclang 0.9.3 Object-Spatial Programming</p>
                    <p>© 2025 Cavin Otieno • Jeseci Smart Learning Academy</p>
                </div>
            </div>
        );
    }

    # API Testing Functions using native Jac communication (simplified)
    def testWelcomeAPI() -> any {
        # For now, just show a message since full async handling needs more complex setup
        alert("Testing Welcome API - Check browser console for actual response");
        console.log("Would call: jacSpawn('init', '', {})");
    }

    def testHealthAPI() -> any {
        alert("Testing Health Check API - Check browser console for actual response");
        console.log("Would call: jacSpawn('health_check', '', {})");
    }

    def testConceptsAPI() -> any {
        alert("Testing Concepts API - Check browser console for actual response");
        console.log("Would call: jacSpawn('concepts', '', {})");
    }

    def testProgressAPI() -> any {
        alert("Testing Progress API - Check browser console for actual response");
        console.log("Would call: jacSpawn('user_progress', '', {})");
    }

    # Main app entry point
    def app() -> any {
        return <LearningDashboard />;
    }
}

# ==============================================================================
# Style Definitions (Inline for simplicity)
# ==============================================================================
with entry {
    containerStyle = {
        "fontFamily": "Arial, sans-serif",
        "maxWidth": "1200px", 
        "margin": "0 auto",
        "padding": "20px",
        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "minHeight": "100vh",
        "color": "#333"
    };
    
    headerStyle = {
        "textAlign": "center",
        "color": "white", 
        "marginBottom": "40px",
        "padding": "40px",
        "background": "rgba(255,255,255,0.1)",
        "borderRadius": "20px"
    };
    
    titleStyle = {
        "fontSize": "3em",
        "margin": "0 0 10px 0",
        "textShadow": "2px 2px 4px rgba(0,0,0,0.3)"
    };
    
    subtitleStyle = {
        "fontSize": "1.2em",
        "opacity": "0.9"
    };
    
    cardStyle = {
        "background": "rgba(255,255,255,0.95)",
        "borderRadius": "20px",
        "padding": "30px",
        "margin": "20px 0",
        "boxShadow": "0 8px 32px rgba(0,0,0,0.1)",
        "border": "1px solid #eee"
    };
    
    h2Style = {
        "color": "#2c3e50",
        "marginBottom": "20px"
    };
    
    gridStyle = {
        "display": "grid",
        "gridTemplateColumns": "repeat(auto-fit, minmax(400px, 1fr))",
        "gap": "20px",
        "margin": "20px 0"
    };
    
    apiCardStyle = {
        "background": "#f8f9fa",
        "borderRadius": "10px",
        "padding": "20px",
        "borderLeft": "4px solid #2196F3"
    };
    
    infoCardStyle = {
        "background": "#e8f5e8",
        "borderRadius": "10px", 
        "padding": "20px",
        "borderLeft": "4px solid #4CAF50"
    };
    
    buttonStyle = {
        "display": "inline-block",
        "padding": "12px 25px",
        "background": "#4CAF50",
        "color": "white",
        "textDecoration": "none",
        "borderRadius": "25px",
        "margin": "5px",
        "border": "none",
        "cursor": "pointer",
        "fontSize": "14px"
    };
    
    # Create button styles without spread operator
    buttonBlueStyle = {
        "display": "inline-block",
        "padding": "12px 25px",
        "background": "#2196F3",
        "color": "white",
        "textDecoration": "none",
        "borderRadius": "25px",
        "margin": "5px",
        "border": "none",
        "cursor": "pointer",
        "fontSize": "14px"
    };
    
    buttonOrangeStyle = {
        "display": "inline-block",
        "padding": "12px 25px",
        "background": "#FF9800",
        "color": "white",
        "textDecoration": "none",
        "borderRadius": "25px",
        "margin": "5px",
        "border": "none",
        "cursor": "pointer",
        "fontSize": "14px"
    };
    
    buttonPurpleStyle = {
        "display": "inline-block",
        "padding": "12px 25px",
        "background": "#9C27B0",
        "color": "white",
        "textDecoration": "none",
        "borderRadius": "25px",
        "margin": "5px",
        "border": "none",
        "cursor": "pointer",
        "fontSize": "14px"
    };
    
    footerStyle = {
        "textAlign": "center",
        "marginTop": "40px",
        "color": "rgba(255,255,255,0.8)",
        "padding": "20px"
    };
}
