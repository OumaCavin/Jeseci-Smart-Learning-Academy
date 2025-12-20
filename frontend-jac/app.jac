"""
Jeseci Smart Learning Companion - JAC Frontend
AI-Powered Learning Platform with JAC Runtime Integration
"""

# Import components and services
import "./components" as components;
import "./services" as services;
import "./pages" as pages;

# Main application object
obj LearningCompanionApp {
    # Application state
    has user_state: dict = {};
    has current_page: str = "dashboard";
    has concepts: list = [];
    has learning_paths: list = [];
    has dashboard_stats: dict = {};  # NEW: Dashboard statistics
    has is_authenticated: bool = False;
    
    # API Configuration
    has api_base_url: str = "http://127.0.0.1:8000/api/v1";
    has auth_token: str = "";

    # Entry point for the application
    can init_app with entry {
        print("🚀 Initializing Jeseci Smart Learning Companion...");
        
        # Initialize authentication state
        self.check_auth_status();
        
        # Load initial data
        self.load_initial_data();
        
        # Start the application
        self.render_app();
    }

    # Check authentication status
    can check_auth_status with entry {
        # Check if user has valid session
        local_storage_token = self.get_local_storage("auth_token");
        
        if (local_storage_token) {
            self.auth_token = local_storage_token;
            self.is_authenticated = True;
            print("✅ User authenticated");
        } else {
            print("🔐 User not authenticated");
            self.is_authenticated = False;
        }
    }

    # Load initial data from FastAPI backend
    can load_initial_data with entry {
        if (self.is_authenticated) {
            # Create FastAPI service instance
            api_service = services.FastAPIService();
            api_service.set_auth_token(self.auth_token);
            
            try {
                # 1. Load Dashboard Stats (New!)
                print("📊 Loading dashboard statistics...");
                progress_data = api_service.get_user_progress();
                self.dashboard_stats = progress_data;
                print(f"✅ Loaded dashboard stats: {len(progress_data)} data points");

                # Load concepts
                print("📚 Loading concepts...");
                concepts_data = api_service.get_concepts();
                self.concepts = concepts_data;
                print(f"✅ Loaded {len(concepts_data)} concepts");
                
                # Load learning paths
                print("🛤️ Loading learning paths...");
                paths_data = api_service.get_learning_paths();
                self.learning_paths = paths_data;
                print(f"✅ Loaded {len(paths_data)} learning paths");
                
            } catch (error) {
                print(f"❌ Failed to load initial data: {error}");
                # Show error to user or retry mechanism
                self.show_data_loading_error(error);
            }
        }
    }
    
    # Handle data loading errors
    can show_data_loading_error with entry (error: str) {
        print(f"🚨 Data loading error: {error}");
        # In production, you'd show a toast notification or retry button
    }

    # Render the main application
    can render_app with entry {
        <div className="learning-companion-app">
            {self.render_header()}
            {self.render_main_content()}
            {self.render_footer()}
        </div>
    }

    # Render application header
    can render_header with entry {
        <header className="app-header">
            <div className="header-content">
                <h1 className="app-title">
                    🎓 Jeseci Smart Learning Companion
                </h1>
                {self.render_navigation()}
            </div>
        </header>
    }

    # Render navigation menu
    can render_navigation with entry {
        <nav className="main-nav">
            <ul className="nav-list">
                <li className="nav-item">
                    <button 
                        className={`nav-link ${self.current_page == 'dashboard' ? 'active' : ''}`}
                        onClick={() => self.navigate_to_page("dashboard")}
                    >
                        📊 Dashboard
                    </button>
                </li>
                <li className="nav-item">
                    <button 
                        className={`nav-link ${self.current_page == 'concepts' ? 'active' : ''}`}
                        onClick={() => self.navigate_to_page("concepts")}
                    >
                        📚 Concepts
                    </button>
                </li>
                <li className="nav-item">
                    <button 
                        className={`nav-link ${self.current_page == 'learning-paths' ? 'active' : ''}`}
                        onClick={() => self.navigate_to_page("learning-paths")}
                    >
                        🛤️ Learning Paths
                    </button>
                </li>
                <li className="nav-item">
                    <button 
                        className={`nav-link ${self.current_page == 'progress' ? 'active' : ''}`}
                        onClick={() => self.navigate_to_page("progress")}
                    >
                        📈 Progress
                    </button>
                </li>
                {self.render_auth_buttons()}
            </ul>
        </nav>
    }

    # Render authentication buttons
    can render_auth_buttons with entry {
        if (self.is_authenticated) {
            <div className="auth-section">
                <span className="user-greeting">Welcome, {self.get_user_name()}</span>
                <button 
                    className="logout-btn"
                    onClick={() => self.logout()}
                >
                    🚪 Logout
                </button>
            </div>
        } else {
            <div className="auth-section">
                <button 
                    className="login-btn"
                    onClick={() => self.show_login_modal()}
                >
                    🔐 Login
                </button>
                <button 
                    className="register-btn"
                    onClick={() => self.show_register_modal()}
                >
                    📝 Register
                </button>
            </div>
        }
    }

    # Render main content area
    can render_main_content with entry {
        <main className="main-content">
            {self.render_current_page()}
        </main>
    }

    # Render current page content
    can render_current_page with entry {
        if (!self.is_authenticated) {
            return self.render_welcome_page();
        }
        
        match (self.current_page) {
            # Pass the fetched stats to the page!
            case "dashboard": return pages.DashboardPage.render(self.dashboard_stats); 
            case "concepts": return pages.ConceptsPage.render(self.concepts);
            case "learning-paths": return pages.LearningPathsPage.render(self.learning_paths);
            case "progress": return pages.ProgressPage.render(self.dashboard_stats);
            default: return pages.DashboardPage.render(self.dashboard_stats);
        }
    }

    # Render welcome page for unauthenticated users
    can render_welcome_page with entry {
        <div className="welcome-page">
            <div className="welcome-content">
                <h2>Welcome to Jeseci Smart Learning Companion</h2>
                <p>An AI-powered personalized learning platform</p>
                <div className="features-grid">
                    <div className="feature-card">
                        <h3>🎯 Adaptive Learning</h3>
                        <p>Personalized learning paths based on your progress and goals</p>
                    </div>
                    <div className="feature-card">
                        <h3>📊 Progress Tracking</h3>
                        <p>Monitor your learning journey with detailed analytics</p>
                    </div>
                    <div className="feature-card">
                        <h3>🧠 AI-Powered</h3>
                        <p>Smart recommendations and adaptive content delivery</p>
                    </div>
                    <div className="feature-card">
                        <h3>🌐 Knowledge Graph</h3>
                        <p>Explore concepts with intelligent relationship mapping</p>
                    </div>
                </div>
                <div className="cta-buttons">
                    <button className="cta-btn primary" onClick={() => self.show_login_modal()}>
                        Get Started - Login
                    </button>
                    <button className="cta-btn secondary" onClick={() => self.show_register_modal()}>
                        Create Account
                    </button>
                </div>
            </div>
        </div>
    }

    # Render application footer
    can render_footer with entry {
        <footer className="app-footer">
            <div className="footer-content">
                <p>&copy; 2025 Jeseci Smart Learning Companion | Powered by JAC Runtime</p>
                <div className="footer-links">
                    <a href="#about">About</a>
                    <a href="#help">Help</a>
                    <a href="#contact">Contact</a>
                </div>
            </div>
        </footer>
    }

    # Navigation methods
    can navigate_to_page with entry (page_name: str) {
        self.current_page = page_name;
        self.render_app();  # Re-render the application
    }

    # Authentication methods
    can show_login_modal with entry {
        # Pass the app instance to the modal for callback
        components.LoginModal.show(self);
    }

    can show_register_modal with entry {
        # Pass the app instance to the modal for callback
        components.RegisterModal.show(self);
    }
    
    # Show password reset modal (for when users click reset link in email)
    can show_password_reset_modal with entry (reset_token: str = "") {
        components.PasswordResetModal.show(self, reset_token);
    }
    
    # Handle login from modal
    can handle_modal_login with entry (login_input: str, password: str, remember_me: bool) {
        self.login(login_input, password);
    }
    
    # Handle register from modal
    can handle_modal_register with entry (user_data: dict) {
        self.register(user_data);
    }
    
    # Handle forgot password from modal
    can handle_modal_forgot_password with entry (email: str) {
        self.send_password_reset(email);
    }
    
    # Handle password reset from modal
    can handle_modal_password_reset with entry (new_password: str, reset_token: str) {
        self.reset_password(new_password, reset_token);
    }

    can login with entry (login_input: str, password: str) {
        try {
            # Create FastAPI service instance
            api_service = services.FastAPIService();
            
            # Call FastAPI login endpoint
            login_response = api_service.login(login_input, password);
            
            if (login_response["success"]) {
                self.auth_token = login_response["token"];
                
                # Store user info if returned by login endpoint
                if ("user" in login_response) {
                    self.user_state = login_response["user"];
                }
                
                self.is_authenticated = True;
                self.save_to_local_storage("auth_token", self.auth_token);
                self.load_initial_data();
                self.render_app();
                print("✅ Login successful");
            } else {
                print(f"❌ Login failed: {login_response.get('error', 'Unknown error')}");
            }
        } catch (error) {
            print(f"❌ Login error: {error}");
        }
    }

    can register with entry (user_data: dict) {
        try {
            # Create FastAPI service instance
            api_service = services.FastAPIService();
            
            # Call FastAPI register endpoint
            register_response = api_service.register(user_data);
            
            if (register_response["success"]) {
                print("✅ Registration successful");
                self.show_login_modal();
            } else {
                print(f"❌ Registration failed: {register_response.get('error', 'Unknown error')}");
            }
        } catch (error) {
            print(f"❌ Registration error: {error}");
        }
    }

    can logout with entry {
        self.auth_token = "";
        self.is_authenticated = False;
        self.clear_local_storage("auth_token");
        self.render_app();
        print("👋 Logged out successfully");
    }

    # Password reset methods
    can send_password_reset with entry (email: str) {
        try {
            # Create FastAPI service instance
            api_service = services.FastAPIService();
            
            # Call FastAPI forgot password endpoint
            forgot_response = api_service.forgot_password(email);
            
            if (forgot_response["success"]) {
                print("✅ Password reset email sent successfully");
                # Show success message to user (you could add a toast notification here)
                self.show_password_reset_success();
            } else {
                print(f"❌ Failed to send password reset email: {forgot_response.get('error', 'Unknown error')}");
                # Show error message to user
                self.show_password_reset_error(forgot_response.get('error', 'Failed to send reset email'));
            }
        } catch (error) {
            print(f"❌ Password reset error: {error}");
            self.show_password_reset_error("Connection error. Please try again.");
        }
    }

    can reset_password with entry (new_password: str, reset_token: str) {
        try {
            # Create FastAPI service instance
            api_service = services.FastAPIService();
            
            # Call FastAPI reset password endpoint
            reset_response = api_service.reset_password(reset_token, new_password);
            
            if (reset_response["success"]) {
                print("✅ Password reset successfully");
                # Show success message and redirect to login
                self.show_password_reset_success();
                # Auto-redirect to login after success
                self.show_login_modal();
            } else {
                print(f"❌ Failed to reset password: {reset_response.get('error', 'Unknown error')}");
                # Show error message to user
                self.show_password_reset_error(reset_response.get('error', 'Failed to reset password'));
            }
        } catch (error) {
            print(f"❌ Password reset error: {error}");
            self.show_password_reset_error("Connection error. Please try again.");
        }
    }

    # Show password reset success/error messages
    can show_password_reset_success with entry {
        print("✅ Password reset email sent! Check your inbox.");
        # You could add a toast notification or success modal here
    }

    can show_password_reset_error with entry (error_message: str) {
        print(f"❌ Password reset error: {error_message}");
        # You could add a toast notification or error modal here
    }

    # Utility methods
    can get_user_name with entry {
        # Extract user name from user state or JWT token
        if (self.user_state and "username" in self.user_state) {
            return self.user_state["username"];
        } elif (self.user_state and "email" in self.user_state) {
            # Extract username from email (before @)
            email = self.user_state["email"];
            return email.split("@")[0];
        }
        return "Learner";  # Fallback
    }
    
    # Update user state after successful login
    can update_user_state with entry (login_response: dict) {
        if (login_response["success"] and "user" in login_response) {
            self.user_state = login_response["user"];
        }
    }

    # Local storage helpers
    can save_to_local_storage with entry (key: str, value: str) {
        # Browser localStorage integration
        print(f"Saving to localStorage: {key} = {value}");
    }

    can get_local_storage with entry (key: str) -> str {
        # Browser localStorage integration
        print(f"Getting from localStorage: {key}");
        return "";  # Placeholder
    }

    can clear_local_storage with entry (key: str) {
        # Browser localStorage integration
        print(f"Clearing from localStorage: {key}");
    }
}

# Main application entry
walker main {
    can init with entry {
        # Initialize the learning companion app
        app = LearningCompanionApp();
        app.init_app();
    }
}