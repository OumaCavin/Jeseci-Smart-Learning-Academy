# Jeseci Smart Learning Academy - Full Stack Application
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
    
    # Node ability to provide concept information
    can get_info with entry {
        report {
            "id": self.concept_id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty_level,
            "duration": self.estimated_duration,
            "type": self.content_type,
            "mastery": self.mastery_score,
            "locked": self.is_locked,
            "completion_date": self.completion_date,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "tags": self.tags,
            "learning_objectives": self.learning_objectives,
            "prerequisites": self.prerequisites
        };
    }
    
    # Node ability to record access
    can record_access with entry {
        self.last_accessed = "2025-12-21T03:02:42Z";
        self.access_count += 1;
    }
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
    has created_at: str = "2025-12-21T03:02:42Z";
    has last_active: str = "2025-12-21T03:02:42Z";
    
    # Node ability to get progress summary
    can get_progress_summary with entry {
        report {
            "user_id": self.user_id,
            "username": self.username,
            "current_concept": self.current_concept,
            "overall_mastery": self.overall_mastery,
            "streak": self.learning_streak,
            "completed": self.total_concepts_completed,
            "time_spent": self.total_time_spent,
            "achievements": self.achievements,
            "preferences": self.learning_preferences,
            "preferred_difficulty": self.preferred_difficulty,
            "goals": self.learning_goals,
            "created_at": self.created_at,
            "last_active": self.last_active
        };
    }
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
            "timestamp": "2025-12-21T03:02:42Z",
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
            "timestamp": "2025-12-21T03:02:42Z"
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
        
        # Create concept nodes
        created_concepts = [];
        for concept_data in filtered_concepts {
            concept = LearningConcept(
                concept_id=concept_data["concept_id"],
                title=concept_data["title"],
                description=concept_data["description"],
                difficulty_level=concept_data["difficulty_level"],
                estimated_duration=concept_data["estimated_duration"],
                content_type=concept_data["content_type"],
                tags=concept_data["tags"],
                learning_objectives=concept_data["learning_objectives"],
                prerequisites=concept_data["prerequisites"]
            );
            
            root ++> concept;
            created_concepts.append(concept);
        }
        
        # Convert to response format
        concepts_response = [];
        for concept in created_concepts {
            concepts_response.append({
                "id": concept.concept_id,
                "title": concept.title,
                "description": concept.description,
                "difficulty": concept.difficulty_level,
                "duration": concept.estimated_duration,
                "type": concept.content_type,
                "mastery": concept.mastery_score,
                "locked": concept.is_locked,
                "tags": concept.tags,
                "learning_objectives": concept.learning_objectives,
                "prerequisites": concept.prerequisites,
                "access_count": concept.access_count,
                "progress_percentage": concept.mastery_score * 100,
                "estimated_completion": concept.estimated_duration if concept.mastery_score == 0.0 else concept.estimated_duration * (1 - concept.mastery_score)
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
        # Create enhanced user progress for full-stack UI
        user_progress = UserProgress(
            user_id="fullstack_user_001",
            username=self.username,
            current_concept="jac_syntax_mastery",
            overall_mastery=0.45,
            learning_streak=7,
            total_concepts_completed=2,
            total_time_spent=240,  # 4 hours
            achievements=["Syntax Master", "7-Day Streak", "Full Stack Explorer"],
            learning_preferences={
                "preferred_learning_style": "interactive",
                "session_length": 45,
                "notifications": True,
                "difficulty_preference": "challenging",
                "theme": "dark"
            },
            preferred_difficulty=3,
            learning_goals=["Master JAC full-stack development", "Build production applications", "Create learning content"]
        );
        
        root ++> user_progress;
        
        report {
            "action": "get_user_progress_ui",
            "progress": {
                "user_id": user_progress.user_id,
                "username": user_progress.username,
                "current_concept": user_progress.current_concept,
                "overall_mastery": user_progress.overall_mastery,
                "streak": user_progress.learning_streak,
                "completed": user_progress.total_concepts_completed,
                "time_spent": user_progress.total_time_spent,
                "achievements": user_progress.achievements,
                "preferences": user_progress.learning_preferences,
                "preferred_difficulty": user_progress.preferred_difficulty,
                "goals": user_progress.learning_goals,
                "created_at": user_progress.created_at,
                "last_active": user_progress.last_active,
                "progress_percentage": user_progress.overall_mastery * 100,
                "level": "Intermediate Learner" if user_progress.overall_mastery < 0.8 else "Advanced Learner"
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
                "total_estimated_time": 690,  # minutes
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

# React hooks import for frontend components
cl import from react { useState, useEffect, useRef, createContext, useContext } cl {}

# Learning Dashboard Context
LearningContext = create_context({});

# Main Learning Dashboard Component
def LearningDashboard() -> any {
    return (
        <div className="min-h-screen bg-gray-50">
            <HeaderComponent />
            <MainContent />
            <FooterComponent />
        </div>
    );
}

# Header Component with Navigation
def HeaderComponent() -> any {
    return (
        <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center">
                        <h1 className="text-2xl font-bold text-blue-600">
                            🎓 Jeseci Smart Learning Academy
                        </h1>
                        <span className="ml-3 px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                            Full Stack JAC
                        </span>
                    </div>
                    <NavigationMenu />
                </div>
            </div>
        </header>
    );
}

# Navigation Menu Component
def NavigationMenu() -> any {
    return (
        <nav className="flex space-x-4">
            <button className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-100">
                Dashboard
            </button>
            <button className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-100">
                Concepts
            </button>
            <button className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-100">
                Progress
            </button>
            <button className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-100">
                Analytics
            </button>
        </nav>
    );
}

# Main Content Area
def MainContent() -> any {
    return (
        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <WelcomeSection />
            <DashboardStats />
            <ConceptGrid />
            <ProgressSection />
        </main>
    );
}

# Welcome Section Component
def WelcomeSection() -> any {
    return (
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-6 mb-8 text-white">
            <h2 className="text-3xl font-bold mb-2">Welcome to Your Learning Journey!</h2>
            <p className="text-lg opacity-90">
                Master JAC programming with our interactive full-stack learning platform
            </p>
            <div className="mt-4 flex space-x-4">
                <button className="bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                    Continue Learning
                </button>
                <button className="border border-white text-white px-4 py-2 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
                    Browse Concepts
                </button>
            </div>
        </div>
    );
}

# Dashboard Statistics Component
def DashboardStats() -> any {
    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg">
                        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                        </svg>
                    </div>
                    <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Concepts Completed</p>
                        <p className="text-2xl font-semibold text-gray-900">2/5</p>
                    </div>
                </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                    <div className="p-2 bg-green-100 rounded-lg">
                        <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                    </div>
                    <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Learning Streak</p>
                        <p className="text-2xl font-semibold text-gray-900">7 days</p>
                    </div>
                </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                    <div className="p-2 bg-purple-100 rounded-lg">
                        <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                    </div>
                    <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Overall Progress</p>
                        <p className="text-2xl font-semibold text-gray-900">45%</p>
                    </div>
                </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                    <div className="p-2 bg-yellow-100 rounded-lg">
                        <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">Study Time</p>
                        <p className="text-2xl font-semibold text-gray-900">4h 30m</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

# Learning Concepts Grid Component
def ConceptGrid() -> any {
    return (
        <div className="mb-8">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-gray-900">Learning Path</h3>
                <div className="flex space-x-2">
                    <select className="px-3 py-2 border border-gray-300 rounded-md text-sm">
                        <option>All Difficulties</option>
                        <option>Beginner</option>
                        <option>Intermediate</option>
                        <option>Advanced</option>
                    </select>
                    <button className="px-3 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700">
                        Search
                    </button>
                </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <ConceptCard 
                    id="jac_syntax_mastery"
                    title="JAC Syntax Mastery"
                    description="Master the essential syntax of JAC programming language with hands-on examples"
                    difficulty={1}
                    duration="60 min"
                    progress={100}
                    status="completed"
                />
                <ConceptCard 
                    id="osp_fundamentals"
                    title="Object-Spatial Programming Fundamentals"
                    description="Deep dive into OSP concepts including nodes, edges, walkers, and spatial relationships"
                    difficulty={2}
                    duration="90 min"
                    progress={75}
                    status="in_progress"
                />
                <ConceptCard 
                    id="advanced_walkers"
                    title="Advanced Walker Patterns and Events"
                    description="Master complex walker behaviors, event handling, and advanced traversal patterns"
                    difficulty={3}
                    duration="120 min"
                    progress={0}
                    status="locked"
                />
                <ConceptCard 
                    id="fullstack_jac"
                    title="Full Stack JAC Development"
                    description="Build complete full-stack applications using JAC backend and client components"
                    difficulty={4}
                    duration="180 min"
                    progress={0}
                    status="locked"
                />
                <ConceptCard 
                    id="production_deployment"
                    title="Production JAC Deployment"
                    description="Deploy and scale JAC applications in production environments"
                    difficulty={5}
                    duration="240 min"
                    progress={0}
                    status="locked"
                />
            </div>
        </div>
    );
}

# Individual Concept Card Component
def ConceptCard(id: str, title: str, description: str, difficulty: int, duration: str, progress: int, status: str) -> any {
    difficulty_colors = {
        1: "bg-green-100 text-green-800",
        2: "bg-blue-100 text-blue-800", 
        3: "bg-yellow-100 text-yellow-800",
        4: "bg-orange-100 text-orange-800",
        5: "bg-red-100 text-red-800"
    };
    
    status_colors = {
        "completed": "bg-green-500",
        "in_progress": "bg-blue-500",
        "locked": "bg-gray-400"
    };
    
    difficulty_text = {
        1: "Beginner",
        2: "Intermediate", 
        3: "Advanced",
        4: "Expert",
        5: "Master"
    };
    
    return (
        <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
            <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${difficulty_colors[difficulty]}`}>
                        {difficulty_text[difficulty]}
                    </span>
                    <div className={`w-3 h-3 rounded-full ${status_colors[status]}`}></div>
                </div>
                
                <h4 className="text-lg font-semibold text-gray-900 mb-2">{title}</h4>
                <p className="text-gray-600 text-sm mb-4">{description}</p>
                
                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <span>⏱️ {duration}</span>
                    <span>📊 {difficulty}/5</span>
                </div>
                
                {progress > 0 and (
                    <div className="mb-4">
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                            <span>Progress</span>
                            <span>{progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                                className="bg-blue-600 h-2 rounded-full transition-all" 
                                style={{width: f"{progress}%"}}
                            ></div>
                        </div>
                    </div>
                )}
                
                <button 
                    className={`w-full py-2 px-4 rounded-md font-medium transition-colors ${
                        status == "locked" 
                        ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                        : status == "completed"
                        ? "bg-green-600 text-white hover:bg-green-700"
                        : "bg-blue-600 text-white hover:bg-blue-700"
                    }`}
                    disabled={status == "locked"}
                >
                    {status == "completed" ? "Review" : status == "in_progress" ? "Continue" : status == "locked" ? "Locked" : "Start"}
                </button>
            </div>
        </div>
    );
}

# Progress Section Component
def ProgressSection() -> any {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Progress</h3>
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Overall Completion</span>
                        <span className="text-sm font-medium">45%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{width: "45%"}}></div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Current Level</span>
                        <span className="text-sm font-medium text-blue-600">Intermediate Learner</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Next Milestone</span>
                        <span className="text-sm font-medium">Complete 3 Concepts</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{width: "67%"}}></div>
                    </div>
                </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Achievements</h3>
                <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                            🏆
                        </div>
                        <div>
                            <p className="text-sm font-medium">Syntax Master</p>
                            <p className="text-xs text-gray-500">Completed JAC Syntax course</p>
                        </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            🔥
                        </div>
                        <div>
                            <p className="text-sm font-medium">7-Day Streak</p>
                            <p className="text-xs text-gray-500">Learned for 7 consecutive days</p>
                        </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                            🚀
                        </div>
                        <div>
                            <p className="text-sm font-medium">Full Stack Explorer</p>
                            <p className="text-xs text-gray-500">Started full-stack development</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

# Footer Component
def FooterComponent() -> any {
    return (
        <footer className="bg-white border-t mt-12">
            <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center">
                    <p className="text-sm text-gray-500">
                        © 2025 Jeseci Smart Learning Academy. Built with Full Stack JAC.
                    </p>
                    <div className="flex space-x-6">
                        <a href="#" className="text-sm text-gray-500 hover:text-gray-900">About</a>
                        <a href="#" className="text-sm text-gray-500 hover:text-gray-900">Privacy</a>
                        <a href="#" className="text-sm text-gray-500 hover:text-gray-900">Terms</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}

# API Integration Helper Component
def APITester() -> any {
    return (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">API Testing Panel</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <button 
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                    onclick={lambda: testAPIEndpoint("welcome")}
                >
                    Test Welcome API
                </button>
                <button 
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
                    onclick={lambda: testAPIEndpoint("health")}
                >
                    Test Health Check
                </button>
                <button 
                    className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 text-sm"
                    onclick={lambda: testAPIEndpoint("concepts")}
                >
                    Test Concepts API
                </button>
            </div>
            <div id="api-results" className="mt-4 p-4 bg-gray-50 rounded-md">
                <p className="text-sm text-gray-600">Click a button to test the API endpoints...</p>
            </div>
        </div>
    );
}

# JavaScript helper functions for API testing
def testAPIEndpoint(endpoint: str) -> any {
    # This would integrate with the JAC backend APIs
    # For demonstration, showing the integration pattern
    pass

with entry {
    # Full-stack system initialization
    print("🎓 Jeseci Smart Learning Academy - Full Stack Edition");
    print("📚 Complete JAC with Backend APIs and Frontend UI");
    print("🚀 Use 'jac serve learning_portal_fullstack.jir' to start the full-stack server");
    print("✨ Features: Interactive dashboard, real-time APIs, responsive UI");
    print("🔧 Built with pure JAC backend and JAC client frontend components");
}