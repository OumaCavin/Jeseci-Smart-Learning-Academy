# Jeseci Smart Learning Academy - Full Stack Application (Corrected)
# Complete JAC implementation with backend API and frontend UI

# =============================================================================
# BACKEND: OBJECT-SPATIAL PROGRAMMING INFRASTRUCTURE
# =============================================================================

# Enhanced Learning Concept Node
node LearningConcept {
    has concept_id: str;
    has title: str;
    has description: str;
    has difficulty_level: int = 1;
    has estimated_duration: int = 30;
    has content_type: str = "lesson";
    has mastery_score: float = 0.0;
    has is_locked: bool = True;
    has completion_date: str = "";
    has last_accessed: str = "";
    has access_count: int = 0;
    has tags: list = [];
    has learning_objectives: list = [];
    has prerequisites: list = [];
}

# Enhanced User Progress Node
node UserProgress {
    has user_id: str;
    has username: str;
    has current_concept: str = "";
    has overall_mastery: float = 0.0;
    has learning_streak: int = 0;
    has total_concepts_completed: int = 0;
    has total_time_spent: int = 0;
    has achievements: list = [];
    has learning_preferences: dict = {};
    has preferred_difficulty: int = 2;
    has learning_goals: list = [];
    has created_at: str = "2025-12-21T03:06:01Z";
    has last_active: str = "2025-12-21T03:06:01Z";
}

# Progress Tracking Edge
edge Progress {
    has mastery_score: float = 0.0;
    has completion_date: str = "";
    has time_spent: int = 0;
    has attempt_count: int = 0;
}

# =============================================================================
# BACKEND: API WALKERS
# =============================================================================

# System Welcome and Initialization
walker fullstack_welcome {
    can initialize_fullstack with `root entry {
        report {
            "message": "Welcome to Jeseci Smart Learning Academy - Full Stack!",
            "status": "initialized",
            "architecture": "Full Stack JAC with Client UI",
            "timestamp": "2025-12-21T03:06:01Z",
            "version": "4.0.0",
            "features": [
                "Full stack JAC application",
                "Interactive frontend with JAC client",
                "Backend API with Object-Spatial Programming",
                "Real-time learning progress tracking",
                "Responsive user interface",
                "Modern learning dashboard"
            ]
        };
    }
}

# Health Check with Frontend Status
walker fullstack_health_check {
    can check_fullstack_health with `root entry {
        report {
            "service": "Jeseci Smart Learning Academy - Full Stack",
            "status": "healthy",
            "version": "4.0.0",
            "architecture": "Full Stack JAC with Client UI",
            "features": [
                "Full stack JAC application with UI",
                "Interactive learning dashboard",
                "Real-time progress tracking",
                "Modern responsive design",
                "Complete learning management system"
            ],
            "system_metrics": {
                "backend_api": "operational",
                "frontend_ui": "loaded",
                "database": "connected",
                "user_sessions": "active"
            },
            "timestamp": "2025-12-21T03:06:01Z"
        };
    }
}

# Enhanced Learning Concepts Management
walker fullstack_concept_management {
    has action: str = "list";
    has concept_id: str = "";
    has difficulty_filter: int = 0;
    has content_type_filter: str = "";
    has search_query: str = "";
    
    can list_concepts_ui with `root entry {
        # Enhanced learning concepts for full-stack app
        concepts_data = [
            {
                "concept_id": "jac_syntax_mastery",
                "title": "JAC Syntax Mastery",
                "description": "Master the essential syntax of JAC programming language with hands-on examples",
                "difficulty_level": 1,
                "estimated_duration": 60,
                "content_type": "lesson",
                "tags": ["syntax", "basics", "variables", "functions"],
                "learning_objectives": [
                    "Understand JAC syntax rules and conventions",
                    "Declare and use variables effectively",
                    "Write basic functions and control structures",
                    "Apply proper code formatting and style"
                ],
                "prerequisites": []
            },
            {
                "concept_id": "osp_fundamentals",
                "title": "Object-Spatial Programming Fundamentals",
                "description": "Deep dive into OSP concepts including nodes, edges, walkers, and spatial relationships",
                "difficulty_level": 2,
                "estimated_duration": 90,
                "content_type": "lesson",
                "tags": ["OSP", "nodes", "edges", "walkers", "graph"],
                "learning_objectives": [
                    "Design and implement node architectures",
                    "Create meaningful edge relationships",
                    "Build efficient walker traversal patterns",
                    "Optimize graph-based data structures"
                ],
                "prerequisites": ["jac_syntax_mastery"]
            },
            {
                "concept_id": "advanced_walkers",
                "title": "Advanced Walker Patterns and Events",
                "description": "Master complex walker behaviors, event handling, and advanced traversal patterns",
                "difficulty_level": 3,
                "estimated_duration": 120,
                "content_type": "lesson",
                "tags": ["walkers", "abilities", "events", "traversal"],
                "learning_objectives": [
                    "Implement sophisticated walker abilities",
                    "Handle complex event scenarios",
                    "Create efficient graph traversal algorithms",
                    "Optimize walker performance and memory usage"
                ],
                "prerequisites": ["osp_fundamentals"]
            },
            {
                "concept_id": "fullstack_jac",
                "title": "Full Stack JAC Development",
                "description": "Build complete full-stack applications using JAC backend and client components",
                "difficulty_level": 4,
                "estimated_duration": 180,
                "content_type": "project",
                "tags": ["fullstack", "client", "UI", "backend", "integration"],
                "learning_objectives": [
                    "Integrate JAC client components with backend APIs",
                    "Build responsive user interfaces",
                    "Implement real-time data binding",
                    "Create complete full-stack applications"
                ],
                "prerequisites": ["advanced_walkers"]
            },
            {
                "concept_id": "production_deployment",
                "title": "Production JAC Deployment",
                "description": "Deploy and scale JAC applications in production environments",
                "difficulty_level": 5,
                "estimated_duration": 240,
                "content_type": "advanced",
                "tags": ["production", "deployment", "scaling", "performance"],
                "learning_objectives": [
                    "Deploy JAC applications to production",
                    "Implement monitoring and logging",
                    "Optimize performance for scale",
                    "Handle production edge cases"
                ],
                "prerequisites": ["fullstack_jac"]
            }
        ];
        
        # Apply filters
        filtered_concepts = [];
        for concept_data in concepts_data {
            include_concept = True;
            
            # Apply difficulty filter
            if self.difficulty_filter > 0 and concept_data["difficulty_level"] != self.difficulty_filter {
                include_concept = False;
            }
            
            # Apply content type filter
            if self.content_type_filter != "" and concept_data["content_type"] != self.content_type_filter {
                include_concept = False;
            }
            
            # Apply search query filter
            if self.search_query != "" {
                search_text = (concept_data["title"] + " " + concept_data["description"]).lower();
                if self.search_query.lower() not in search_text {
                    include_concept = False;
                }
            }
            
            if include_concept {
                filtered_concepts.append(concept_data);
            }
        }
        
        # Convert to response format
        concepts_response = [];
        for concept_data in filtered_concepts {
            concepts_response.append({
                "id": concept_data["concept_id"],
                "title": concept_data["title"],
                "description": concept_data["description"],
                "difficulty": concept_data["difficulty_level"],
                "duration": concept_data["estimated_duration"],
                "type": concept_data["content_type"],
                "mastery": 0.0,
                "locked": concept_data["difficulty_level"] > 2,
                "tags": concept_data["tags"],
                "learning_objectives": concept_data["learning_objectives"],
                "prerequisites": concept_data["prerequisites"],
                "access_count": 0,
                "progress_percentage": 0,
                "estimated_completion": concept_data["estimated_duration"]
            });
        }
        
        report {
            "action": "list_concepts_ui",
            "concepts": concepts_response,
            "total_count": len(concepts_response),
            "filters_applied": {
                "difficulty": self.difficulty_filter,
                "content_type": self.content_type_filter,
                "search_query": self.search_query
            },
            "ui_features": {
                "interactive_cards": True,
                "progress_indicators": True,
                "filter_controls": True,
                "search_functionality": True
            },
            "status": "success"
        };
    }
    
    can get_concept_details_ui with `root entry {
        if self.concept_id == "" {
            report {
                "error": "concept_id parameter required",
                "status": "error"
            };
        }
        
        # Enhanced concept details for UI
        concept_details = {
            "jac_syntax_mastery": {
                "id": "jac_syntax_mastery",
                "title": "JAC Syntax Mastery",
                "description": "Master the essential syntax of JAC programming language with hands-on examples",
                "difficulty": 1,
                "duration": 60,
                "type": "lesson",
                "prerequisites": [],
                "learning_objectives": [
                    "Understand JAC syntax rules and conventions",
                    "Declare and use variables effectively",
                    "Write basic functions and control structures",
                    "Apply proper code formatting and style"
                ],
                "key_topics": [
                    "Variable declaration and typing",
                    "Function definitions with abilities",
                    "Control flow with brackets",
                    "Collection types and operations",
                    "Error handling patterns"
                ],
                "interactive_elements": {
                    "code_editor": True,
                    "syntax_highlighting": True,
                    "live_examples": True,
                    "practice_exercises": True
                },
                "estimated_completion": "1-2 hours",
                "difficulty_progression": "Beginner to Intermediate"
            },
            "fullstack_jac": {
                "id": "fullstack_jac",
                "title": "Full Stack JAC Development",
                "description": "Build complete full-stack applications using JAC backend and client components",
                "difficulty": 4,
                "duration": 180,
                "type": "project",
                "prerequisites": ["advanced_walkers"],
                "learning_objectives": [
                    "Integrate JAC client components with backend APIs",
                    "Build responsive user interfaces",
                    "Implement real-time data binding",
                    "Create complete full-stack applications"
                ],
                "key_topics": [
                    "JAC client component architecture",
                    "Backend API integration",
                    "State management patterns",
                    "Responsive design principles"
                ],
                "interactive_elements": {
                    "live_demo": True,
                    "component_library": True,
                    "api_tester": True,
                    "full_project_build": True
                },
                "estimated_completion": "4-6 hours",
                "difficulty_progression": "Advanced to Expert"
            }
        };
        
        details = concept_details.get(self.concept_id);
        if details {
            report {
                "concept": details,
                "ui_data": {
                    "interactive_preview": True,
                    "progress_tracking": True,
                    "completion_badge": True,
                    "next_steps": True
                },
                "status": "success"
            };
        } else {
            report {
                "error": f"Concept '{self.concept_id}' not found",
                "status": "error"
            };
        }
    }
}

# User Progress Management
walker fullstack_user_progress {
    has action: str = "get_progress";
    has username: str = "demo_user";
    has concept_id: str = "";
    has mastery_score: float = 0.0;
    has time_spent: int = 0;
    
    can get_user_progress_ui with `root entry {
        report {
            "action": "get_user_progress_ui",
            "progress": {
                "user_id": "fullstack_user_001",
                "username": self.username,
                "current_concept": "jac_syntax_mastery",
                "overall_mastery": 0.45,
                "streak": 7,
                "completed": 2,
                "time_spent": 240,
                "achievements": ["Syntax Master", "7-Day Streak", "Full Stack Explorer"],
                "preferences": {
                    "preferred_learning_style": "interactive",
                    "session_length": 45,
                    "notifications": True,
                    "difficulty_preference": "challenging",
                    "theme": "dark"
                },
                "preferred_difficulty": 3,
                "goals": ["Master JAC full-stack development", "Build production applications", "Create learning content"],
                "created_at": "2025-12-21T03:06:01Z",
                "last_active": "2025-12-21T03:06:01Z",
                "progress_percentage": 45,
                "level": "Intermediate Learner"
            },
            "ui_components": {
                "progress_chart": True,
                "achievement_badges": True,
                "streak_counter": True,
                "learning_goals": True,
                "preferences_panel": True
            },
            "recommendations": [
                {
                    "type": "next_concept",
                    "title": "Object-Spatial Programming Fundamentals",
                    "reason": "You're ready to progress to OSP concepts",
                    "difficulty": 2,
                    "estimated_time": 90,
                    "confidence": 0.88
                },
                {
                    "type": "achievement",
                    "title": "Complete 3 Concepts",
                    "reason": "You're close to unlocking the 'JAC Explorer' badge",
                    "progress": 67,
                    "target": 3
                }
            ],
            "status": "success"
        };
    }
}

# System Analytics for UI
walker fullstack_analytics {
    can get_ui_analytics with `root entry {
        analytics = {
            "action": "ui_analytics",
            "system_metrics": {
                "total_concepts": 5,
                "difficulty_levels": 5,
                "total_estimated_time": 690,
                "user_count": 1,
                "active_users": 1,
                "concepts_completed": 2,
                "average_mastery": 0.45,
                "learning_streak_record": 7,
                "total_learning_time": 240
            },
            "ui_analytics": {
                "page_views": 156,
                "concept_browses": 89,
                "search_queries": 23,
                "completion_rate": 0.75,
                "user_engagement": 0.87,
                "average_session_time": 45
            },
            "performance_metrics": {
                "api_response_time": "45ms",
                "ui_render_time": "12ms",
                "cache_hit_ratio": "94%",
                "user_satisfaction": 4.8
            },
            "learning_insights": {
                "most_popular_concept": "JAC Syntax Mastery",
                "average_completion_time": 120,
                "preferred_difficulty": 3,
                "peak_learning_hours": "19:00-21:00"
            },
            "status": "success"
        };
        
        report analytics;
    }
}

# =============================================================================
# FRONTEND: JAC CLIENT COMPONENTS
# =============================================================================

cl import from react { useState, useEffect, useRef, createContext, useContext } cl {
    # Main App Component - Entry Point
    def app() -> any {
        # Create context inside the function
        LearningContext = create_context({});
        return <LearningDashboard />;
    }
    
    # Main Learning Dashboard Component
    def LearningDashboard() -> any {
        [concepts, setConcepts] = useState([]);
        [userProgress, setUserProgress] = useState({});
        [analytics, setAnalytics] = useState({});
        [selectedTab, setSelectedTab] = useState("dashboard");
        [loading, setLoading] = useState(True);
        [error, setError] = useState("");
        
        # Load initial data
        useEffect(lambda -> None {
            loadDashboardData();
        }, []);
        
        def loadDashboardData() -> None {
            setLoading(True);
            setError("");
            
            # Simulate API calls - in real implementation, these would call JAC walkers
            # For now, we'll use mock data
            setTimeout(lambda -> None {
                setConcepts([
                    {
                        "id": "jac_syntax_mastery",
                        "title": "JAC Syntax Mastery",
                        "description": "Master the essential syntax of JAC programming language",
                        "difficulty": 1,
                        "duration": "60 min",
                        "progress": 100,
                        "status": "completed",
                        "tags": ["syntax", "basics"]
                    },
                    {
                        "id": "osp_fundamentals",
                        "title": "Object-Spatial Programming Fundamentals",
                        "description": "Deep dive into OSP concepts including nodes, edges, walkers",
                        "difficulty": 2,
                        "duration": "90 min",
                        "progress": 75,
                        "status": "in_progress",
                        "tags": ["OSP", "nodes", "edges"]
                    },
                    {
                        "id": "advanced_walkers",
                        "title": "Advanced Walker Patterns and Events",
                        "description": "Master complex walker behaviors and traversal patterns",
                        "difficulty": 3,
                        "duration": "120 min",
                        "progress": 0,
                        "status": "locked",
                        "tags": ["walkers", "abilities"]
                    },
                    {
                        "id": "fullstack_jac",
                        "title": "Full Stack JAC Development",
                        "description": "Build complete full-stack applications using JAC",
                        "difficulty": 4,
                        "duration": "180 min",
                        "progress": 0,
                        "status": "locked",
                        "tags": ["fullstack", "client", "UI"]
                    },
                    {
                        "id": "production_deployment",
                        "title": "Production JAC Deployment",
                        "description": "Deploy and scale JAC applications in production",
                        "difficulty": 5,
                        "duration": "240 min",
                        "progress": 0,
                        "status": "locked",
                        "tags": ["production", "deployment"]
                    }
                ]);
                
                setUserProgress({
                    "username": "demo_user",
                    "overall_mastery": 45,
                    "streak": 7,
                    "completed": 2,
                    "time_spent": "4h 30m",
                    "level": "Intermediate Learner",
                    "achievements": ["Syntax Master", "7-Day Streak", "Full Stack Explorer"]
                });
                
                setAnalytics({
                    "total_concepts": 5,
                    "completion_rate": 75,
                    "user_engagement": 87,
                    "satisfaction_score": 4.8
                });
                
                setLoading(False);
            }, 1000);
        }
        
        if loading {
            return <div style={{"textAlign": "center", "padding": "50px"}}><h2>Loading Dashboard...</h2></div>;
        }
        
        if error {
            return <div style={{"textAlign": "center", "padding": "50px", "color": "red"}}><h2>Error: {error}</h2></div>;
        }
        
        return (
            <div style={{"minHeight": "100vh", "backgroundColor": "#f9fafb", "fontFamily": "Arial, sans-serif"}}>
                <HeaderComponent />
                <NavigationMenu selectedTab={selectedTab} setSelectedTab={setSelectedTab} />
                <MainContent 
                    concepts={concepts}
                    userProgress={userProgress}
                    analytics={analytics}
                    selectedTab={selectedTab}
                    onRefresh={loadDashboardData}
                />
                <FooterComponent />
            </div>
        );
    }
    
    # Header Component with Navigation
    def HeaderComponent() -> any {
        return (
            <header style={{"backgroundColor": "white", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "borderBottom": "1px solid #e5e7eb"}}>
                <div style={{"maxWidth": "1200px", "margin": "0 auto", "padding": "0 20px"}}>
                    <div style={{"display": "flex", "justifyContent": "space-between", "alignItems": "center", "height": "64px"}}>
                        <div style={{"display": "flex", "alignItems": "center"}}>
                            <h1 style={{"fontSize": "24px", "fontWeight": "bold", "color": "#2563eb", "margin": "0"}}>
                                🎓 Jeseci Smart Learning Academy
                            </h1>
                            <span style={{"marginLeft": "12px", "padding": "4px 8px", "backgroundColor": "#dcfce7", "color": "#166534", "fontSize": "12px", "fontWeight": "500", "borderRadius": "9999px"}}>
                                Full Stack JAC
                            </span>
                        </div>
                    </div>
                </div>
            </header>
        );
    }
    
    # Navigation Menu Component
    def NavigationMenu(selectedTab: str, setSelectedTab: any) -> any {
        return (
            <nav style={{"backgroundColor": "white", "borderBottom": "1px solid #e5e7eb"}}>
                <div style={{"maxWidth": "1200px", "margin": "0 auto", "padding": "0 20px"}}>
                    <div style={{"display": "flex", "spaceX": "16px"}}>
                        {[
                            {"id": "dashboard", "label": "Dashboard"},
                            {"id": "concepts", "label": "Concepts"},
                            {"id": "progress", "label": "Progress"},
                            {"id": "analytics", "label": "Analytics"}
                        ].map(lambda tab: any {
                            <button
                                key={tab["id"]}
                                style={{
                                    "padding": "12px 16px",
                                    "borderRadius": "6px",
                                    "fontSize": "14px",
                                    "fontWeight": "500",
                                    "border": "none",
                                    "backgroundColor": selectedTab == tab["id"] ? "#3b82f6" : "transparent",
                                    "color": selectedTab == tab["id"] ? "white" : "#374151",
                                    "cursor": "pointer"
                                }}
                                onClick={lambda -> None { setSelectedTab(tab["id"]); }}
                            >
                                {tab["label"]}
                            </button>
                        })}
                    </div>
                </div>
            </nav>
        );
    }
    
    # Main Content Area
    def MainContent(concepts: list, userProgress: dict, analytics: dict, selectedTab: str, onRefresh: any) -> any {
        return (
            <main style={{"maxWidth": "1200px", "margin": "0 auto", "padding": "24px 20px"}}>
                {selectedTab == "dashboard" and <DashboardView concepts={concepts} userProgress={userProgress} analytics={analytics} />}
                {selectedTab == "concepts" and <ConceptsView concepts={concepts} />}
                {selectedTab == "progress" and <ProgressView userProgress={userProgress} />}
                {selectedTab == "analytics" and <AnalyticsView analytics={analytics} />}
                <APITester onRefresh={onRefresh} />
            </main>
        );
    }
    
    # Dashboard View Component
    def DashboardView(concepts: list, userProgress: dict, analytics: dict) -> any {
        return (
            <div>
                <WelcomeSection />
                <DashboardStats userProgress={userProgress} analytics={analytics} />
                <ConceptGrid concepts={concepts} />
            </div>
        );
    }
    
    # Welcome Section Component
    def WelcomeSection() -> any {
        return (
            <div style={{
                "background": "linear-gradient(to right, #3b82f6, #8b5cf6)",
                "borderRadius": "8px",
                "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                "padding": "24px",
                "marginBottom": "32px",
                "color": "white"
            }}>
                <h2 style={{"fontSize": "30px", "fontWeight": "bold", "marginBottom": "8px"}}>
                    Welcome to Your Learning Journey!
                </h2>
                <p style={{"fontSize": "18px", "opacity": "0.9", "marginBottom": "16px"}}>
                    Master JAC programming with our interactive full-stack learning platform
                </p>
                <div style={{"display": "flex", "spaceX": "16px"}}>
                    <button style={{
                        "backgroundColor": "white",
                        "color": "#3b82f6",
                        "padding": "8px 16px",
                        "borderRadius": "8px",
                        "fontWeight": "600",
                        "border": "none",
                        "cursor": "pointer"
                    }}>
                        Continue Learning
                    </button>
                    <button style={{
                        "border": "1px solid white",
                        "color": "white",
                        "padding": "8px 16px",
                        "borderRadius": "8px",
                        "fontWeight": "600",
                        "backgroundColor": "transparent",
                        "cursor": "pointer"
                    }}>
                        Browse Concepts
                    </button>
                </div>
            </div>
        );
    }
    
    # Dashboard Statistics Component
    def DashboardStats(userProgress: dict, analytics: dict) -> any {
        stats = [
            {"label": "Concepts Completed", "value": f"{userProgress.get("completed", 0)}/5", "icon": "📚", "color": "#3b82f6"},
            {"label": "Learning Streak", "value": f"{userProgress.get("streak", 0)} days", "icon": "⚡", "color": "#10b981"},
            {"label": "Overall Progress", "value": f"{userProgress.get("overall_mastery", 0)}%", "icon": "📊", "color": "#8b5cf6"},
            {"label": "Study Time", "value": userProgress.get("time_spent", "0h 0m"), "icon": "⏱️", "color": "#f59e0b"}
        ];
        
        return (
            <div style={{"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))", "gap": "24px", "marginBottom": "32px"}}>
                {stats.map(lambda stat: any {
                    <div key={stat["label"]} style={{"backgroundColor": "white", "borderRadius": "8px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "padding": "24px"}}>
                        <div style={{"display": "flex", "alignItems": "center"}}>
                            <div style={{"padding": "8px", "borderRadius": "8px", "backgroundColor": stat["color"] + "20", "marginRight": "16px"}}>
                                <span style={{"fontSize": "24px"}}>{stat["icon"]}</span>
                            </div>
                            <div>
                                <p style={{"fontSize": "14px", "fontWeight": "500", "color": "#6b7280", "margin": "0"}}>{stat["label"]}</p>
                                <p style={{"fontSize": "24px", "fontWeight": "600", "color": "#111827", "margin": "0"}}>{stat["value"]}</p>
                            </div>
                        </div>
                    </div>
                })}
            </div>
        );
    }
    
    # Learning Concepts Grid Component
    def ConceptGrid(concepts: list) -> any {
        return (
            <div style={{"marginBottom": "32px"}}>
                <div style={{"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "24px"}}>
                    <h3 style={{"fontSize": "20px", "fontWeight": "600", "color": "#111827", "margin": "0"}}>Learning Path</h3>
                    <div style={{"display": "flex", "spaceX": "8px"}}>
                        <select style={{
                            "padding": "8px 12px",
                            "border": "1px solid #d1d5db",
                            "borderRadius": "6px",
                            "fontSize": "14px"
                        }}>
                            <option>All Difficulties</option>
                            <option>Beginner</option>
                            <option>Intermediate</option>
                            <option>Advanced</option>
                        </select>
                        <button style={{
                            "padding": "8px 16px",
                            "backgroundColor": "#3b82f6",
                            "color": "white",
                            "borderRadius": "6px",
                            "fontSize": "14px",
                            "border": "none",
                            "cursor": "pointer"
                        }}>
                            Search
                        </button>
                    </div>
                </div>
                
                <div style={{"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "24px"}}>
                    {concepts.map(lambda concept: any {
                        <ConceptCard key={concept["id"]} concept={concept} />
                    })}
                </div>
            </div>
        );
    }
    
    # Individual Concept Card Component
    def ConceptCard(concept: dict) -> any {
        difficulty_colors = {
            1: {"bg": "#dcfce7", "text": "#166534"},
            2: {"bg": "#dbeafe", "text": "#1d4ed8"}, 
            3: {"bg": "#fef3c7", "text": "#d97706"},
            4: {"bg": "#fed7aa", "text": "#ea580c"},
            5: {"bg": "#fecaca", "text": "#dc2626"}
        };
        
        status_colors = {
            "completed": "#10b981",
            "in_progress": "#3b82f6",
            "locked": "#9ca3af"
        };
        
        difficulty_text = {
            1: "Beginner",
            2: "Intermediate", 
            3: "Advanced",
            4: "Expert",
            5: "Master"
        };
        
        colors = difficulty_colors.get(concept["difficulty"], difficulty_colors[1]);
        
        return (
            <div style={{
                "backgroundColor": "white",
                "borderRadius": "8px",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                "overflow": "hidden",
                "transition": "box-shadow 0.2s"
            }}>
                <div style={{"padding": "24px"}}>
                    <div style={{"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "16px"}}>
                        <span style={{
                            "padding": "4px 8px",
                            "fontSize": "12px",
                            "fontWeight": "600",
                            "borderRadius": "9999px",
                            "backgroundColor": colors["bg"],
                            "color": colors["text"]
                        }}>
                            {difficulty_text.get(concept["difficulty"], "Beginner")}
                        </span>
                        <div style={{
                            "width": "12px",
                            "height": "12px",
                            "borderRadius": "50%",
                            "backgroundColor": status_colors.get(concept["status"], "#9ca3af")
                        }}></div>
                    </div>
                    
                    <h4 style={{"fontSize": "18px", "fontWeight": "600", "color": "#111827", "marginBottom": "8px"}}>
                        {concept["title"]}
                    </h4>
                    <p style={{"color": "#6b7280", "fontSize": "14px", "marginBottom": "16px"}}>
                        {concept["description"]}
                    </p>
                    
                    <div style={{"display": "flex", "justifyContent": "space-between", "fontSize": "14px", "color": "#6b7280", "marginBottom": "16px"}}>
                        <span>⏱️ {concept["duration"]}</span>
                        <span>📊 {concept["difficulty"]}/5</span>
                    </div>
                    
                    {concept["progress"] > 0 and (
                        <div style={{"marginBottom": "16px"}}>
                            <div style={{"display": "flex", "justifyContent": "space-between", "fontSize": "14px", "color": "#6b7280", "marginBottom": "4px"}}>
                                <span>Progress</span>
                                <span>{concept["progress"]}%</span>
                            </div>
                            <div style={{"width": "100%", "backgroundColor": "#e5e7eb", "borderRadius": "9999px", "height": "8px"}}>
                                <div style={{
                                    "backgroundColor": "#3b82f6",
                                    "height": "8px",
                                    "borderRadius": "9999px",
                                    "width": f"{concept["progress"]}%",
                                    "transition": "width 0.3s"
                                }}></div>
                            </div>
                        </div>
                    )}
                    
                    <button style={{
                        "width": "100%",
                        "padding": "8px 16px",
                        "borderRadius": "6px",
                        "fontWeight": "500",
                        "border": "none",
                        "cursor": "pointer",
                        "backgroundColor": concept["status"] == "locked" ? "#d1d5db" : concept["status"] == "completed" ? "#10b981" : "#3b82f6",
                        "color": concept["status"] == "locked" ? "#9ca3af" : "white",
                        "transition": "background-color 0.2s"
                    }}>
                        {concept["status"] == "completed" ? "Review" : concept["status"] == "in_progress" ? "Continue" : concept["status"] == "locked" ? "Locked" : "Start"}
                    </button>
                </div>
            </div>
        );
    }
    
    # Additional view components for tabs
    def ConceptsView(concepts: list) -> any {
        return <div><h2>Concepts View</h2><ConceptGrid concepts={concepts} /></div>;
    }
    
    def ProgressView(userProgress: dict) -> any {
        return <div><h2>Progress View</h2><p>User Progress: {userProgress}</p></div>;
    }
    
    def AnalyticsView(analytics: dict) -> any {
        return <div><h2>Analytics View</h2><p>Analytics: {analytics}</p></div>;
    }
    
    # Footer Component
    def FooterComponent() -> any {
        return (
            <footer style={{"backgroundColor": "white", "borderTop": "1px solid #e5e7eb", "marginTop": "48px"}}>
                <div style={{"maxWidth": "1200px", "margin": "0 auto", "padding": "24px 20px"}}>
                    <div style={{"display": "flex", "justifyContent": "space-between", "alignItems": "center"}}>
                        <p style={{"fontSize": "14px", "color": "#6b7280", "margin": "0"}}>
                            © 2025 Jeseci Smart Learning Academy. Built with Full Stack JAC.
                        </p>
                        <div style={{"display": "flex", "spaceX": "24px"}}>
                            <a href="#" style={{"fontSize": "14px", "color": "#6b7280", "textDecoration": "none"}}>About</a>
                            <a href="#" style={{"fontSize": "14px", "color": "#6b7280", "textDecoration": "none"}}>Privacy</a>
                            <a href="#" style={{"fontSize": "14px", "color": "#6b7280", "textDecoration": "none"}}>Terms</a>
                        </div>
                    </div>
                </div>
            </footer>
        );
    }
    
    # API Integration Helper Component
    def APITester(onRefresh: any) -> any {
        return (
            <div style={{"backgroundColor": "white", "borderRadius": "8px", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)", "padding": "24px", "marginBottom": "32px"}}>
                <h3 style={{"fontSize": "18px", "fontWeight": "600", "color": "#111827", "marginBottom": "16px"}}>API Testing Panel</h3>
                <div style={{"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "16px"}}>
                    <button style={{
                        "padding": "8px 16px",
                        "backgroundColor": "#3b82f6",
                        "color": "white",
                        "borderRadius": "6px",
                        "fontSize": "14px",
                        "border": "none",
                        "cursor": "pointer"
                    }}>
                        Test Welcome API
                    </button>
                    <button style={{
                        "padding": "8px 16px",
                        "backgroundColor": "#10b981",
                        "color": "white",
                        "borderRadius": "6px",
                        "fontSize": "14px",
                        "border": "none",
                        "cursor": "pointer"
                    }}>
                        Test Health Check
                    </button>
                    <button style={{
                        "padding": "8px 16px",
                        "backgroundColor": "#8b5cf6",
                        "color": "white",
                        "borderRadius": "6px",
                        "fontSize": "14px",
                        "border": "none",
                        "cursor": "pointer"
                    }}>
                        Test Concepts API
                    </button>
                </div>
                <div style={{"marginTop": "16px", "padding": "16px", "backgroundColor": "#f9fafb", "borderRadius": "6px"}}>
                    <p style={{"fontSize": "14px", "color": "#6b7280"}}>Click a button to test the API endpoints...</p>
                </div>
            </div>
        );
    }
}
}

# =============================================================================
# SYSTEM INITIALIZATION
# =============================================================================

with entry {
    # Full-stack system initialization
    print("🎓 Jeseci Smart Learning Academy - Full Stack Edition");
    print("📚 Complete JAC with Backend APIs and Frontend UI");
    print("🚀 Use 'jac serve learning_portal_fullstack_corrected.jir' to start the full-stack server");
    print("✨ Features: Interactive dashboard, real-time APIs, responsive UI");
    print("🔧 Built with pure JAC backend and JAC client frontend components");
    print("🌐 Access the app at: http://localhost:8000/page/app");
}