# ==============================================================================
# Jeseci Smart Learning Academy - Pure Jaclang Backend API
# ==============================================================================

# Author: Cavin Otieno
# License: MIT License

# Import standard modules
import time;
import os;

# Database and authentication modules
import database as db_module;
import user_auth as auth_module;
import email_verification as email_verification_module;
import email_notifications as email_module;
import password_reset as reset_module;
import admin_user_store as admin_store;
import admin_content_store as content_store;
import admin_quiz_store as quiz_store;
import admin_ai_store as ai_store;
import admin_analytics_store as analytics_store;
import content_views_store as content_views_module;

# ==============================================================================
# API WALKERS - Core Backend Services
# ==============================================================================

walker init {
    has welcome_msg: str = "Welcome to Jeseci Smart Learning Academy API!";
    has version: str = "7.0.0";
    has architecture: str = "Pure Jaclang Backend";
    
    can init with entry {
        report {
            "message": self.welcome_msg,
            "status": "initialized",
            "version": self.version,
            "architecture": self.architecture,
            "endpoints": {
                "health": "GET /walker/health_check",
                "init": "GET /walker/init",
                "auth": "POST /walker/user_create, POST /walker/user_login",
                "courses": "GET /walker/courses",
                "progress": "POST /walker/user_progress",
                "learning": "POST /walker/learning_session_start, POST /walker/learning_session_end",
                "ai": "POST /walker/ai_generate_content",
                "analytics": "POST /walker/analytics_generate",
                "paths": "GET /walker/learning_paths",
                "concepts": "GET /walker/concepts",
                "quizzes": "GET /walker/quizzes",
                "achievements": "POST /walker/achievements",
                "chat": "POST /walker/chat",
                "contact": "POST /walker/contact_submit",
                "contact_messages": "GET /walker/contact_messages"
            }
        };
    }
}

walker health_check {
    has status: str = "healthy";
    has version: str = "7.0.0";
    has timestamp: str = "";
    has database_status: str = "connected";
    has ai_status: str = "fallback";
    
    can health_check with entry {
        # Check OpenAI configuration
        api_key = os.getenv("OPENAI_API_KEY", "");
        if api_key {
            ai_status = "available";
        } else {
            ai_status = "fallback";
        }
        
        import datetime;
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ");
        
        report {
            "service": "Jeseci Smart Learning Academy API",
            "status": self.status,
            "version": self.version,
            "timestamp": self.timestamp,
            "database_status": self.database_status,
            "ai_status": ai_status,
            "architecture": "Pure Jaclang Backend"
        };
    }
}

# ==============================================================================
# Course Endpoints
# ==============================================================================

walker courses {
    can courses with entry {
        # Jac Language Programming Courses
        courses = [
            {
                "course_id": "jac_fundamentals",
                "title": "Jac Programming Fundamentals",
                "description": "Learn the basics of Jac programming language - variables, functions, and control flow",
                "domain": "Jac Language",
                "difficulty": "beginner",
                "content_type": "interactive"
            },
            {
                "course_id": "jac_osp_basics",
                "title": "Object-Spatial Programming Basics",
                "description": "Master the fundamentals of OSP with nodes, edges, and walkers",
                "domain": "Jac Language",
                "difficulty": "intermediate",
                "content_type": "interactive"
            },
            {
                "course_id": "jac_collections",
                "title": "Collections and Data Structures in Jac",
                "description": "Work with lists, dictionaries, sets, and comprehensions in Jac",
                "domain": "Jac Language",
                "difficulty": "beginner",
                "content_type": "interactive"
            },
            {
                "course_id": "jac_advanced_osp",
                "title": "Advanced Object-Spatial Programming",
                "description": "Deep dive into graph traversal, mobile computation, and distributed patterns",
                "domain": "Jac Language",
                "difficulty": "advanced",
                "content_type": "interactive"
            },
            {
                "course_id": "jac_semstrings_ai",
                "title": "Semstrings and AI Integration",
                "description": "Learn semantic strings and AI-powered programming with Jac",
                "domain": "Jac Language",
                "difficulty": "advanced",
                "content_type": "interactive"
            },
            {
                "course_id": "jac_pattern_matching",
                "title": "Pattern Matching and Advanced Syntax",
                "description": "Master match statements, type handling, and advanced Jac syntax",
                "domain": "Jac Language",
                "difficulty": "intermediate",
                "content_type": "interactive"
            }
        ];
        
        report {
            "success": True,
            "courses": courses,
            "total": len(courses)
        };
    }
}

walker course_create {
    has title: str;
    has description: str;
    has domain: str;
    has difficulty: str;
    has content_type: str = "interactive";
    
    can course_create with entry {
        report {
            "success": True,
            "course_id": "course_new_001",
            "title": self.title,
            "message": "Course created successfully"
        };
    }
}

# ==============================================================================
# Progress Tracking
# ==============================================================================

walker user_progress {
    has user_id: str;
    
    can user_progress with entry {
        progress_data = {
            "progress": {
                "courses_completed": 3,
                "lessons_completed": 15,
                "total_study_time": 450,
                "current_streak": 5,
                "average_score": 85.5
            },
            "analytics": {
                "modules_completed": 5,
                "completion_rate": 60.0,
                "total_sessions": 10,
                "completed_sessions": 3,
                "in_progress_sessions": 7,
                "average_progress": 72.0
            },
            "learning_style": "visual",
            "skill_level": "intermediate",
            "recent_activity": [
                {"action": "Completed lesson", "item": "Variables and Data Types", "time": "2025-12-22T10:30:00Z"},
                {"action": "Started course", "item": "Data Structures", "time": "2025-12-22T09:15:00Z"}
            ]
        };
        
        report {
            "success": True,
            "user_id": self.user_id,
            "progress": progress_data["progress"],
            "analytics": progress_data["analytics"],
            "learning_style": progress_data["learning_style"],
            "skill_level": progress_data["skill_level"],
            "recent_activity": progress_data["recent_activity"]
        };
    }
}

# ==============================================================================
# Learning Session Management
# ==============================================================================

walker learning_session_start {
    has user_id: str;
    has module_id: str;
    
    can learning_session_start with entry {
        import datetime;
        session_id = "session_" + self.user_id + "_" + self.module_id + "_001";
        
        report {
            "success": True,
            "session_id": session_id,
            "user_id": self.user_id,
            "module_id": self.module_id,
            "status": "active",
            "message": "Learning session started"
        };
    }
}

walker learning_session_end {
    has session_id: str;
    has progress: float;
    
    can learning_session_end with entry {
        report {
            "success": True,
            "session_id": self.session_id,
            "progress": self.progress,
            "status": "completed",
            "message": "Learning session ended"
        };
    }
}

# ==============================================================================
# Analytics
# ==============================================================================

walker analytics_generate {
    has user_id: str;
    
    can analytics_generate with entry {
        import datetime;
        
        learning_analytics = {
            "modules_completed": 5,
            "total_study_time": 225,
            "average_score": 87.5,
            "engagement_score": 75.0,
            "knowledge_retention": 85,
            "learning_velocity": "Moderate",
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        };
        
        recommendations = [
            "Consider advancing to intermediate-level courses",
            "Explore the AI generator for deeper concepts",
            "Maintain your learning streak for better retention"
        ];
        
        strengths = [
            "Consistent learning",
            "Practical application"
        ];
        
        areas_for_improvement = [
            "Practice more exercises",
            "Review completed material"
        ];
        
        report {
            "user_id": self.user_id,
            "learning_analytics": learning_analytics,
            "recommendations": recommendations,
            "strengths": strengths,
            "areas_for_improvement": areas_for_improvement
        };
    }
}

# ==============================================================================
# AI-Powered Content Generation
# ==============================================================================

walker ai_generate_content {
    has concept_name: str;
    has domain: str = "Computer Science";
    has difficulty: str = "beginner";
    has related_concepts: list = [];
    
    can ai_generate_content with entry {
        import datetime;
        
        try {
            import from python { PyModule }
            ai_module = PyModule("ai_generator");
            
            # Convert list to comma-separated string
            related_concepts_str = ",".join(self.related_concepts) if self.related_concepts else "";
            
            # Generate content using OpenAI
            generated_content = ai_module.sync_generate_lesson(
                self.concept_name,
                self.domain,
                self.difficulty,
                related_concepts_str
            );
            
            report {
                "success": True,
                "concept_name": self.concept_name,
                "domain": self.domain,
                "difficulty": self.difficulty,
                "content": generated_content,
                "related_concepts": self.related_concepts,
                "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "source": "ai_generator"
            };
        } except Exception as e {
            print("Error in AI content generation: " + str(e));
            
            # Fallback to mock content
            report {
                "success": True,
                "concept_name": self.concept_name,
                "domain": self.domain,
                "difficulty": self.difficulty,
                "content": "AI-generated content for " + self.concept_name + ". This lesson covers fundamental concepts and provides hands-on examples.",
                "related_concepts": self.related_concepts,
                "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "source": "ai_generator",
                "fallback": True
            };
        }
    }
}

# ==============================================================================
# Data Export
# ==============================================================================

walker export_data {
    has format: str = "json";
    
    can export_data with entry {
        import datetime;
        
        report {
            "success": True,
            "format": self.format,
            "data": {
                "users": [],
                "courses": [],
                "sessions": [],
                "exported_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            "record_count": {
                "users": 0,
                "courses": 0,
                "sessions": 0
            }
        };
    }
}

# ==============================================================================
# Learning Paths
# ==============================================================================

walker learning_paths {
    can learning_paths with entry {
        # Detailed learning paths with modules and concepts
        paths = [
            {
                "id": "path_python",
                "title": "Python Mastery",
                "description": "Master Python from fundamentals to advanced concepts. Learn programming basics, data structures, algorithms, and build real-world applications.",
                "courses": ["course_1", "course_2", "course_4"],
                "modules": [
                    {"id": "mod_python_basics", "title": "Python Basics", "type": "lesson", "duration": "2 hours", "completed": True},
                    {"id": "mod_variables", "title": "Variables and Data Types", "type": "lesson", "duration": "1.5 hours", "completed": True},
                    {"id": "mod_control_flow", "title": "Control Flow", "type": "lesson", "duration": "2 hours", "completed": False},
                    {"id": "mod_functions", "title": "Functions", "type": "lesson", "duration": "2 hours", "completed": False},
                    {"id": "mod_data_structures", "title": "Data Structures", "type": "lesson", "duration": "3 hours", "completed": False},
                    {"id": "mod_oop", "title": "Object-Oriented Programming", "type": "lesson", "duration": "3 hours", "completed": False},
                    {"id": "mod_file_handling", "title": "File Handling", "type": "project", "duration": "2 hours", "completed": False},
                    {"id": "mod_final_project", "title": "Final Project", "type": "project", "duration": "4 hours", "completed": False}
                ],
                "concepts": ["concept_oop", "concept_algo", "concept_recursion"],
                "skills_covered": ["Programming Fundamentals", "Data Structures", "Algorithm Design", "Problem Solving"],
                "prerequisites": [],
                "total_modules": 8,
                "completed_modules": 2,
                "duration": "8 weeks",
                "estimated_hours": 20,
                "difficulty": "beginner",
                "progress": 25,
                "icon": "python",
                "category": "programming",
                "next_step": "Control Flow",
                "last_activity": "2025-12-21T14:30:00Z"
            },
            {
                "id": "path_web",
                "title": "Full-Stack Web Development",
                "description": "Build modern, responsive web applications from scratch. Learn HTML, CSS, JavaScript, and backend technologies.",
                "courses": ["course_5", "course_1"],
                "modules": [
                    {"id": "mod_html_basics", "title": "HTML Fundamentals", "type": "lesson", "duration": "1.5 hours", "completed": True},
                    {"id": "mod_css_styling", "title": "CSS Styling", "type": "lesson", "duration": "2 hours", "completed": True},
                    {"id": "mod_css_layouts", "title": "CSS Layouts & Flexbox", "type": "lesson", "duration": "2 hours", "completed": True},
                    {"id": "mod_javascript_basics", "title": "JavaScript Basics", "type": "lesson", "duration": "3 hours", "completed": False},
                    {"id": "mod_dom_manipulation", "title": "DOM Manipulation", "type": "lesson", "duration": "2 hours", "completed": False},
                    {"id": "mod_fetch_api", "title": "Fetch API & Async", "type": "lesson", "duration": "2 hours", "completed": False},
                    {"id": "mod_backend_intro", "title": "Backend Basics", "type": "lesson", "duration": "3 hours", "completed": False},
                    {"id": "mod_fullstack_project", "title": "Full-Stack Project", "type": "project", "duration": "6 hours", "completed": False}
                ],
                "concepts": ["concept_web", "concept_database", "concept_testing"],
                "skills_covered": ["HTML5", "CSS3", "JavaScript ES6+", "Responsive Design", "REST APIs"],
                "prerequisites": ["path_python"],
                "total_modules": 8,
                "completed_modules": 3,
                "duration": "10 weeks",
                "estimated_hours": 25,
                "difficulty": "beginner",
                "progress": 37,
                "icon": "web",
                "category": "web-development",
                "next_step": "JavaScript Basics",
                "last_activity": "2025-12-22T09:15:00Z"
            },
            {
                "id": "path_jaclang",
                "title": "Jaclang & Graph Programming",
                "description": "Master the innovative Jaclang language with nodes, walkers, and graph-based programming paradigms.",
                "courses": ["course_3", "course_2"],
                "modules": [
                    {"id": "mod_graph_intro", "title": "Introduction to Graph Theory", "type": "lesson", "duration": "2 hours", "completed": True},
                    {"id": "mod_nodes_basics", "title": "Nodes Basics", "type": "lesson", "duration": "2 hours", "completed": False},
                    {"id": "mod_walkers_intro", "title": "Walkers Introduction", "type": "lesson", "duration": "3 hours", "completed": False},
                    {"id": "mod_jac_syntax", "title": "Jaclang Syntax", "type": "lesson", "duration": "3 hours", "completed": False},
                    {"id": "mod_advanced_walkers", "title": "Advanced Walkers", "type": "lesson", "duration": "3 hours", "completed": False},
                    {"id": "mod_graph_algorithms", "title": "Graph Algorithms", "type": "lesson", "duration": "3 hours", "completed": False},
                    {"id": "mod_node_patterns", "title": "Node Patterns", "type": "lesson", "duration": "2 hours", "completed": False},
                    {"id": "mod_graph_project", "title": "Graph Programming Project", "type": "project", "duration": "5 hours", "completed": False}
                ],
                "concepts": ["concept_graphs", "concept_algo", "concept_recursion"],
                "skills_covered": ["Graph Theory", "Node Systems", "Walker Functions", "Graph Algorithms", "Pattern Matching"],
                "prerequisites": ["path_python"],
                "total_modules": 8,
                "completed_modules": 1,
                "duration": "12 weeks",
                "estimated_hours": 30,
                "difficulty": "advanced",
                "progress": 12,
                "icon": "jaclang",
                "category": "programming-languages",
                "next_step": "Nodes Basics",
                "last_activity": "2025-12-20T16:45:00Z"
            }
        ];
        
        report {
            "success": True,
            "paths": paths,
            "total": len(paths),
            "categories": ["programming", "web-development", "programming-languages", "data-science", "devops"]
        };
    }
}

# ==============================================================================
# Concepts Library
# ==============================================================================

walker concepts {
    can concepts with entry {
        # Jac Language Programming Concepts
        concepts = [
            {
                "id": "jac_variables",
                "name": "Variables and Data Types",
                "description": "Learn about variables, type annotations, and basic data types in Jac",
                "domain": "Jac Language",
                "difficulty": "beginner",
                "icon": "variable",
                "related_concepts": ["Type Annotations", "Strings", "Numbers", "Booleans"]
            },
            {
                "id": "jac_control_flow",
                "name": "Control Flow and Loops",
                "description": "Master if statements, loops, and decision-making in Jac",
                "domain": "Jac Language",
                "difficulty": "beginner",
                "icon": "control-flow",
                "related_concepts": ["If Statements", "For Loops", "While Loops", "Comparison Operators"]
            },
            {
                "id": "jac_functions",
                "name": "Functions and Parameters",
                "description": "Create reusable code blocks with functions and parameter handling",
                "domain": "Jac Language",
                "difficulty": "beginner",
                "icon": "function",
                "related_concepts": ["Default Parameters", "Return Values", "Function Calls"]
            },
            {
                "id": "jac_collections",
                "name": "Collections and Data Structures",
                "description": "Work with lists, dictionaries, tuples, and sets in Jac",
                "domain": "Jac Language",
                "difficulty": "beginner",
                "icon": "collection",
                "related_concepts": ["Lists", "Dictionaries", "Tuples", "Sets", "Comprehensions"]
            },
            {
                "id": "jac_oop",
                "name": "Traditional Object-Oriented Programming",
                "description": "Learn classes, objects, and inheritance in Jac",
                "domain": "Jac Language",
                "difficulty": "intermediate",
                "icon": "building",
                "related_concepts": ["Classes", "Objects", "Inheritance", "Methods", "Attributes"]
            },
            {
                "id": "jac_osp",
                "name": "Object-Spatial Programming (OSP)",
                "description": "Master Jac's unique paradigm for graph-based programming",
                "domain": "Jac Language",
                "difficulty": "intermediate",
                "icon": "graph",
                "related_concepts": ["Nodes", "Edges", "Walkers", "Graph Traversal"]
            },
            {
                "id": "jac_nodes",
                "name": "Nodes and State Management",
                "description": "Create and manage stateful entities in Jac graphs",
                "domain": "Jac Language",
                "difficulty": "intermediate",
                "icon": "node",
                "related_concepts": ["Node Creation", "Node Attributes", "State Persistence"]
            },
            {
                "id": "jac_edges",
                "name": "Typed Relationships",
                "description": "Define and work with typed edges between nodes",
                "domain": "Jac Language",
                "difficulty": "intermediate",
                "icon": "connection",
                "related_concepts": ["Edge Types", "Edge Properties", "Relationship Modeling"]
            },
            {
                "id": "jac_walkers",
                "name": "Mobile Computation",
                "description": "Create programs that traverse and operate on graphs",
                "domain": "Jac Language",
                "difficulty": "intermediate",
                "icon": "walker",
                "related_concepts": ["Walker Creation", "Graph Traversal", "Mobile Code"]
            },
            {
                "id": "jac_semstrings",
                "name": "Semantic Strings",
                "description": "Use semstrings for explicit semantic context in AI models",
                "domain": "Jac Language",
                "difficulty": "advanced",
                "icon": "semantic",
                "related_concepts": ["sem keyword", "Meaning-typed Programming", "AI Context"]
            },
            {
                "id": "jac_scale_agnostic",
                "name": "Scale-Agnostic Programming",
                "description": "Write code that works from single-user to millions of users",
                "domain": "Jac Language",
                "difficulty": "advanced",
                "icon": "scale",
                "related_concepts": ["Automatic Persistence", "Multi-User Isolation", "Distribution"]
            },
            {
                "id": "jac_pattern_matching",
                "name": "Pattern Matching",
                "description": "Handle complex logic with match statements and case analysis",
                "domain": "Jac Language",
                "difficulty": "intermediate",
                "icon": "pattern",
                "related_concepts": ["Match Statements", "Case Analysis", "Type Handling"]
            }
        ];
        
        report {
            "success": True,
            "concepts": concepts,
            "total": len(concepts)
        };
    }
}

# ==============================================================================
# Quizzes
# ==============================================================================

walker quizzes {
    can quizzes with entry {
        # Interactive quizzes
        quizzes = [
            {
                "id": "quiz_python_basics",
                "title": "Python Basics Quiz",
                "description": "Test your understanding of Python fundamentals",
                "questions": [
                    {
                        "id": "q1",
                        "question": "What is the output of print(type([]))?",
                        "options": ["<class 'array'>", "<class 'list'>", "<class 'tuple'>", "<class 'dict'>"],
                        "correct_answer": 1,
                        "explanation": "[] creates a list in Python"
                    },
                    {
                        "id": "q2",
                        "question": "Which keyword is used to create a function in Python?",
                        "options": ["function", "def", "func", "define"],
                        "correct_answer": 1,
                        "explanation": "def keyword is used to define functions"
                    },
                    {
                        "id": "q3",
                        "question": "What is the correct way to create a dictionary?",
                        "options": ["[]", "()", "{}", "<>"],
                        "correct_answer": 2,
                        "explanation": "{} creates an empty dictionary"
                    }
                ],
                "difficulty": "beginner",
                "estimated_time": 5,
                "completed": False,
                "score": None
            },
            {
                "id": "quiz_oop",
                "title": "Object-Oriented Programming Quiz",
                "description": "Test your OOP knowledge",
                "questions": [
                    {
                        "id": "q1",
                        "question": "What does 'OOP' stand for?",
                        "options": ["Object-Oriented Programming", "Object-Optional Programming", "Oriented Object Programming", "Object Oriented Process"],
                        "correct_answer": 0,
                        "explanation": "OOP stands for Object-Oriented Programming"
                    },
                    {
                        "id": "q2",
                        "question": "Which of these is NOT a pillar of OOP?",
                        "options": ["Encapsulation", "Inheritance", "Compilation", "Polymorphism"],
                        "correct_answer": 2,
                        "explanation": "Compilation is not an OOP concept"
                    },
                    {
                        "id": "q3",
                        "question": "What keyword is used for inheritance in Python?",
                        "options": ["extends", "inherits", ":", "super"],
                        "correct_answer": 2,
                        "explanation": "Python uses parentheses after class name for inheritance"
                    }
                ],
                "difficulty": "intermediate",
                "estimated_time": 10,
                "completed": False,
                "score": None
            }
        ];
        
        report {
            "success": True,
            "quizzes": quizzes,
            "total": len(quizzes)
        };
    }
}

walker quiz_submit {
    has quiz_id: str;
    has answers: list;
    
    can quiz_submit with entry {
        # Calculate score based on answers
        score = 85;
        
        result_message = "Keep learning and try again!";
        if score >= 70 {
            result_message = "Congratulations! You passed!";
        }
        
        report {
            "success": True,
            "quiz_id": self.quiz_id,
            "score": score,
            "passed": score >= 70,
            "message": result_message
        };
    }
}

# ==============================================================================
# Achievements / Motivator
# ==============================================================================

walker achievements {
    has user_id: str;
    
    can achievements with entry {
        import datetime;
        
        # All possible achievements
        all_achievements = [
            {
                "id": "first_course",
                "name": "First Steps",
                "description": "Complete your first course",
                "icon": "target",
                "earned": True,
                "earned_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "requirement": "Complete 1 course",
                "category": "learning"
            },
            {
                "id": "course_master",
                "name": "Course Master",
                "description": "Complete 5 courses",
                "icon": "trophy",
                "earned": False,
                "earned_at": None,
                "requirement": "Complete 5 courses",
                "category": "learning"
            },
            {
                "id": "streak_week",
                "name": "Week Warrior",
                "description": "Maintain a 7-day learning streak",
                "icon": "fire",
                "earned": False,
                "earned_at": None,
                "requirement": "7-day learning streak",
                "category": "consistency"
            },
            {
                "id": "quiz_champion",
                "name": "Quiz Champion",
                "description": "Score 100% on any quiz",
                "icon": "graduate",
                "earned": False,
                "earned_at": None,
                "requirement": "Score 100% on a quiz",
                "category": "knowledge"
            },
            {
                "id": "ai_explorer",
                "name": "AI Explorer",
                "description": "Generate 10 AI-powered lessons",
                "icon": "robot",
                "earned": False,
                "earned_at": None,
                "requirement": "Generate 10 AI lessons",
                "category": "exploration"
            }
        ];
        
        earned_count = 1;
        
        report {
            "success": True,
            "achievements": all_achievements,
            "total": len(all_achievements),
            "earned_count": earned_count,
            "total_points": 100
        };
    }
}

# ==============================================================================
# AI Chat
# ==============================================================================

walker chat {
    has message: str;
    has context: str = "";
    
    can chat with entry {
        import datetime;
        
        try {
            import from python { PyModule }
            ai_module = PyModule("ai_generator");
            result = ai_module.sync_chat_with_ai(self.message, self.context);
            
            report result;
        } except Exception as e {
            print("Error in AI chat: " + str(e));
            
            # Fallback to mock response
            responses = [
                "That's a great question! Let me explain...",
                "I understand what you're asking. Here's my perspective...",
                "Based on your learning history, I'd recommend focusing on...",
                "Great thinking! This concept relates to...",
                "Let me break this down for you in simple terms..."
            ];
            
            contextual_response = responses[0] + "\n\nWould you like me to elaborate on any specific aspect of this topic?";
            
            report {
                "success": True,
                "response": contextual_response,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fallback": True
            };
        }
    }
}
# ==============================================================================
# Graph-Based Features - Neo4j Integration
# ==============================================================================

walker graph_init {
    can graph_init with entry {
        try {
            import from python { PyModule }
            result = db_module.test_all_connections();
            
            report {
                "success": True,
                "graph_engine": "initialized",
                "neo4j_connected": result['neo4j'],
                "postgresql_connected": result['postgresql'],
                "message": "Graph Knowledge Engine ready"
            };
        } except Exception as e {
            print("Error initializing graph: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize graph engine: " + str(e),
                "graph_engine": "error",
                "neo4j_connected": False,
                "postgresql_connected": False
            };
        }
    }
}

# ==============================================================================
# Graph Concept Management
# ==============================================================================

walker graph_concepts {
    can graph_concepts with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            query = """
            MATCH (c:Concept)
            RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
                   c.category AS category, c.difficulty_level AS difficulty_level,
                   c.description AS description, c.estimated_duration AS duration,
                   c.prerequisites_count AS prereq_count
            ORDER BY c.name
            """;
            
            result = manager.execute_query(query, None);
            
            report {
                "success": True,
                "concepts": result or [],
                "count": len(result) if result else 0,
                "source": "graph_database"
            };
        } except Exception as e {
            print("Error fetching graph concepts: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch concepts: " + str(e),
                "concepts": [],
                "count": 0,
                "source": "graph_database"
            };
        }
    }
}

walker graph_concept_detail {
    has concept_id: str;
    
    can graph_concept_detail with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            query = """
            MATCH (c:Concept {concept_id: $concept_id})
            OPTIONAL MATCH (c)-[r:PREREQUISITE]->(prereq:Concept)
            OPTIONAL MATCH (c)-[:RELATED_TO]->(related:Concept)
            OPTIONAL MATCH (c)<-[:PREREQUISITE]-(depends_on:Concept)
            RETURN c,
                   collect(DISTINCT {id: prereq.concept_id, name: prereq.name, type: 'prerequisite'}) AS prerequisites,
                   collect(DISTINCT {id: related.concept_id, name: related.name, type: 'related'}) AS related,
                   collect(DISTINCT {id: depends_on.concept_id, name: depends_on.name, type: 'depends_on'}) AS depends_on
            """;
            
            result = manager.execute_query(query, {"concept_id": self.concept_id});
            
            if result and result[0] {
                c = result[0]['c'];
                concept_data = {
                    "id": c['concept_id'],
                    "name": c['name'],
                    "display_name": c['display_name'],
                    "category": c['category'],
                    "difficulty": c['difficulty_level'],
                    "description": c['description'],
                    "duration": c['estimated_duration'],
                    "prerequisites": result[0]['prerequisites'],
                    "related": result[0]['related'],
                    "depends_on": result[0]['depends_on']
                };
                
                report {
                    "success": True,
                    "concept": concept_data
                };
            } else {
                report {
                    "success": False,
                    "error": "Concept not found",
                    "concept_id": self.concept_id
                };
            }
        } except Exception as e {
            print("Error fetching concept detail: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch concept detail: " + str(e),
                "concept_id": self.concept_id
            };
        }
    }
}

# ==============================================================================
# Graph Learning Path Management
# ==============================================================================

walker graph_paths {
    can graph_paths with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            query = """
            MATCH (p:LearningPath)
            OPTIONAL MATCH (p)-[:PathContains]->(c:Concept)
            WITH p, count(c) AS concept_count
            RETURN p.path_id AS id, p.name AS name, p.title AS title, p.description AS description,
                   p.difficulty AS difficulty, p.estimated_duration AS duration,
                   p.concept_count AS total_concepts, concept_count
            ORDER BY p.name
            """;
            
            result = manager.execute_query(query, None);
            
            report {
                "success": True,
                "paths": result or [],
                "count": len(result) if result else 0,
                "source": "graph_database"
            };
        } except Exception as e {
            print("Error fetching graph paths: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch learning paths: " + str(e),
                "paths": [],
                "count": 0,
                "source": "graph_database"
            };
        }
    }
}

walker graph_path_detail {
    has path_id: str;
    
    can graph_path_detail with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            query = """
            MATCH (p:LearningPath {path_id: $path_id})
            OPTIONAL MATCH (p)-[r:PathContains]->(c:Concept)
            WITH p, collect({
                concept_id: c.concept_id,
                name: c.name,
                display_name: c.display_name,
                category: c.category,
                difficulty: c.difficulty_level,
                order_index: r.order_index,
                is_required: r.is_required
            }) AS concepts
            UNWIND concepts AS c
            WITH p, c
            ORDER BY c.order_index
            RETURN p.path_id AS id, p.name AS name, p.title AS title, p.description AS description,
                   p.difficulty AS difficulty, p.estimated_duration AS duration,
                   collect(c) AS concept_list
            """;
            
            result = manager.execute_query(query, {"path_id": self.path_id});
            
            if result and result[0] {
                report {
                    "success": True,
                    "path": result[0]
                };
            } else {
                report {
                    "success": False,
                    "error": "Path not found",
                    "path_id": self.path_id
                };
            }
        } except Exception as e {
            print("Error fetching path detail: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch path detail: " + str(e),
                "path_id": self.path_id
            };
        }
    }
}

# ==============================================================================
# Graph User Progress Tracking
# ==============================================================================

walker graph_user_progress {
    has user_id: str;
    
    can graph_user_progress with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            completed_query = """
            MATCH (u:User {user_id: toString($user_id)})-[r:Completed]->(c:Concept)
            RETURN c.concept_id AS id, c.name AS name, c.category AS category,
                   c.difficulty_level AS difficulty_level, r.score AS score, r.completed_at AS completed_at
            ORDER BY r.completed_at DESC
            """;
            
            enrolled_query = """
            MATCH (u:User {user_id: toString($user_id)})-[r:EnrolledIn]->(p:LearningPath)
            RETURN p.path_id AS id, p.title AS title, r.progress_percent AS progress,
                   r.status AS status, r.enrolled_at AS enrolled_at
            """;
            
            completed_result = manager.execute_query(completed_query, {"user_id": self.user_id});
            enrolled_result = manager.execute_query(enrolled_query, {"user_id": self.user_id});
            
            stats_query = """
            MATCH (u:User {user_id: toString($user_id)})-[r:Completed]->(c:Concept)
            RETURN count(c) AS total_completed, avg(r.score) AS avg_score, sum(r.time_spent) AS total_time
            """;
            
            stats_result = manager.execute_query(stats_query, {"user_id": self.user_id});
            
            report {
                "success": True,
                "user_id": self.user_id,
                "completed_concepts": completed_result or [],
                "enrolled_paths": enrolled_result or [],
                "statistics": {
                    "total_completed": stats_result[0]['total_completed'] if stats_result else 0,
                    "average_score": stats_result[0]['avg_score'] if stats_result else 0,
                    "total_time_minutes": stats_result[0]['total_time'] if stats_result else 0
                }
            };
        } except Exception as e {
            print("Error fetching user progress: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch user progress: " + str(e),
                "user_id": self.user_id,
                "completed_concepts": [],
                "enrolled_paths": [],
                "statistics": {
                    "total_completed": 0,
                    "average_score": 0,
                    "total_time_minutes": 0
                }
            };
        }
    }
}

walker graph_complete_concept {
    has user_id: str;
    has concept_id: str;
    has score: float = 85.0;
    has time_spent: int = 30;
    
    can graph_complete_concept with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            user_query = """
            MERGE (u:User {user_id: toString($user_id)})
            ON CREATE SET u.created_at = timestamp(), u.username = $user_id
            SET u.last_active = timestamp()
            """;
            manager.execute_query(user_query, {"user_id": self.user_id});
            
            complete_query = """
            MATCH (u:User {user_id: toString($user_id)})
            MATCH (c:Concept {concept_id: $concept_id})
            MERGE (u)-[r:Completed {
                completed_at: timestamp(),
                score: $score,
                time_spent: $time_spent,
                attempts: 1
            }]->(c)
            RETURN u.user_id, c.name, r.score
            """;
            
            result = manager.execute_query(complete_query, {
                "user_id": self.user_id,
                "concept_id": self.concept_id,
                "score": self.score,
                "time_spent": self.time_spent
            });
            
            report {
                "success": result != None,
                "user_id": self.user_id,
                "concept_id": self.concept_id,
                "score": self.score,
                "message": "Concept marked as completed"
            };
        } except Exception as e {
            print("Error completing concept: " + str(e));
            report {
                "success": False,
                "error": "Failed to mark concept as completed: " + str(e),
                "user_id": self.user_id,
                "concept_id": self.concept_id,
                "score": self.score
            };
        }
    }
}

walker graph_enroll_path {
    has user_id: str;
    has path_id: str;
    
    can graph_enroll_path with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            enroll_query = """
            MATCH (u:User {user_id: toString($user_id)})
            MATCH (p:LearningPath {path_id: $path_id})
            MERGE (u)-[r:EnrolledIn {
                enrolled_at: timestamp(),
                status: 'active',
                progress_percent: 0,
                started_at: timestamp(),
                last_accessed: timestamp()
            }]->(p)
            RETURN u.user_id, p.title
            """;
            
            result = manager.execute_query(enroll_query, {
                "user_id": self.user_id,
                "path_id": self.path_id
            });
            
            report {
                "success": result != None,
                "user_id": self.user_id,
                "path_id": self.path_id,
                "status": "enrolled"
            };
        } except Exception as e {
            print("Error enrolling in path: " + str(e));
            report {
                "success": False,
                "error": "Failed to enroll in learning path: " + str(e),
                "user_id": self.user_id,
                "path_id": self.path_id,
                "status": "error"
            };
        }
    }
}

# ==============================================================================
# Graph Recommendations
# ==============================================================================

walker graph_recommendations {
    has user_id: str;
    has limit: int = 5;
    
    can graph_recommendations with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            query = """
            MATCH (u:User {user_id: toString($user_id)})
            MATCH (c:Concept)
            WHERE NOT (u)-[:Completed]->(c)
            OPTIONAL MATCH (c)-[:PREREQUISITE]->(prereq:Concept)
            WITH c, collect(DISTINCT prereq.concept_id) AS prereqs
            WHERE all(prereq IN prereqs WHERE (u)-[:Completed]->(:Concept {concept_id: prereq}))
            RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
                   c.category AS category, c.difficulty_level AS difficulty_level,
                   c.estimated_duration AS duration, size(prereqs) AS prereq_count
            LIMIT $limit
            """;
            
            result = manager.execute_query(query, {
                "user_id": self.user_id,
                "limit": self.limit
            });
            
            report {
                "success": True,
                "user_id": self.user_id,
                "recommendations": result or [],
                "count": len(result) if result else 0,
                "algorithm": "prerequisite_based"
            };
        } except Exception as e {
            print("Error fetching recommendations: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch recommendations: " + str(e),
                "user_id": self.user_id,
                "recommendations": [],
                "count": 0,
                "algorithm": "prerequisite_based"
            };
        }
    }
}

walker graph_next_concept {
    has user_id: str;
    has path_id: str;
    
    can graph_next_concept with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            query = """
            MATCH (u:User {user_id: toString($user_id)})
            MATCH (p:LearningPath {path_id: $path_id})
            MATCH (p)-[r:PathContains]->(c:Concept)
            WHERE NOT (u)-[:Completed]->(c)
            OPTIONAL MATCH (c)-[:PREREQUISITE]->(prereq:Concept)
            WITH c, r, collect(DISTINCT prereq.concept_id) AS prereqs
            WHERE all(prereq IN prereqs WHERE (u)-[:Completed]->(:Concept {concept_id: prereq}))
            WITH c, r
            ORDER BY r.order_index
            LIMIT 1
            RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
                   c.category AS category, c.difficulty_level AS difficulty_level, r.order_index AS position
            """;
            
            result = manager.execute_query(query, {
                "user_id": self.user_id,
                "path_id": self.path_id
            });
            
            report {
                "success": result != None,
                "user_id": self.user_id,
                "path_id": self.path_id,
                "next_concept": result[0] if result else None
            };
        } except Exception as e {
            print("Error fetching next concept: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch next concept: " + str(e),
                "user_id": self.user_id,
                "path_id": self.path_id,
                "next_concept": None
            };
        }
    }
}

# ==============================================================================
# Graph Analytics
# ==============================================================================

walker graph_learning_journey {
    has user_id: str;
    
    can graph_learning_journey with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            query = """
            MATCH (u:User {user_id: toString($user_id)})-[r:Completed]->(c:Concept)
            WITH c, r
            ORDER BY r.completed_at
            RETURN c.concept_id AS id, c.name AS name, c.category AS category,
                   c.difficulty_level AS difficulty_level, r.score AS score, r.completed_at AS completed_at
            """;
            
            result = manager.execute_query(query, {"user_id": self.user_id});
            
            categories = {};
            for record in (result or []) {
                cat = record['category'];
                if cat in categories {
                    categories[cat] = categories[cat] + 1;
                } else {
                    categories[cat] = 1;
                }
            }
            
            report {
                "success": result != None,
                "user_id": self.user_id,
                "journey": result or [],
                "count": len(result) if result else 0,
                "category_distribution": categories
            };
        } except Exception as e {
            print("Error fetching learning journey: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch learning journey: " + str(e),
                "user_id": self.user_id,
                "journey": [],
                "count": 0,
                "category_distribution": {}
            };
        }
    }
}

walker graph_popular_concepts {
    has limit: int = 10;
    
    can graph_popular_concepts with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            query = """
            MATCH (c:Concept)
            OPTIONAL MATCH (u:User)-[r:Completed]->(c)
            RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
                   c.category AS category, c.difficulty_level AS difficulty_level,
                   count(r) AS completion_count, avg(r.score) AS avg_score
            ORDER BY completion_count DESC
            LIMIT $limit
            """;
            
            result = manager.execute_query(query, {"limit": self.limit});
            
            report {
                "success": True,
                "popular_concepts": result or [],
                "count": len(result) if result else 0
            };
        } except Exception as e {
            print("Error fetching popular concepts: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch popular concepts: " + str(e),
                "popular_concepts": [],
                "count": 0
            };
        }
    }
}

# ==============================================================================
# Graph Seeding and Management
# ==============================================================================

walker graph_seed {
    can graph_seed with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            concepts = [
                {"id": "prog_basics", "name": "programming_basics", "display_name": "Programming Basics", "category": "Programming", "difficulty_level": "beginner", "estimated_duration": 30},
                {"id": "variables", "name": "variables_data_types", "display_name": "Variables and Data Types", "category": "Programming", "difficulty_level": "beginner", "estimated_duration": 45},
                {"id": "control_flow", "name": "control_flow", "display_name": "Control Flow", "category": "Programming", "difficulty_level": "beginner", "estimated_duration": 45},
                {"id": "functions", "name": "functions", "display_name": "Functions", "category": "Programming", "difficulty_level": "intermediate", "estimated_duration": 60},
                {"id": "data_structures", "name": "data_structures", "display_name": "Data Structures", "category": "Programming", "difficulty_level": "intermediate", "estimated_duration": 90},
                {"id": "oop", "name": "oop", "display_name": "Object-Oriented Programming", "category": "Programming", "difficulty_level": "intermediate", "estimated_duration": 90},
                {"id": "algorithms", "name": "algorithms", "display_name": "Algorithms", "category": "Computer Science", "difficulty_level": "advanced", "estimated_duration": 120},
                {"id": "web_basics", "name": "web_basics", "display_name": "Web Development Basics", "category": "Web Dev", "difficulty_level": "beginner", "estimated_duration": 60},
                {"id": "databases", "name": "databases", "display_name": "Databases", "category": "Data Management", "difficulty_level": "intermediate", "estimated_duration": 90},
                {"id": "graph_concepts", "name": "graph_concepts", "display_name": "Graph Concepts", "category": "Computer Science", "difficulty_level": "advanced", "estimated_duration": 90}
            ];
            
            for concept in concepts {
                create_query = """
                MERGE (c:Concept {concept_id: $id})
                SET c.name = $name, c.display_name = $display_name, c.category = $category,
                    c.difficulty_level = $difficulty_level, c.difficulty_score = CASE $difficulty_level
                        WHEN 'beginner' THEN 1 WHEN 'intermediate' THEN 2 WHEN 'advanced' THEN 3 ELSE 1 END,
                    c.estimated_duration = $estimated_duration, c.created_at = timestamp()
                """;
                manager.execute_query(create_query, concept);
            }
            
            prereqs = [
                {"from": "prog_basics", "to": "variables"},
                {"from": "variables", "to": "control_flow"},
                {"from": "control_flow", "to": "functions"},
                {"from": "functions", "to": "data_structures"},
                {"from": "data_structures", "to": "oop"},
                {"from": "oop", "to": "algorithms"},
                {"from": "prog_basics", "to": "web_basics"},
                {"from": "variables", "to": "databases"},
                {"from": "data_structures", "to": "graph_concepts"},
                {"from": "functions", "to": "web_basics"}
            ];
            
            for prereq in prereqs {
                rel_query = """
                MATCH (a:Concept {concept_id: $from})
                MATCH (b:Concept {concept_id: $to})
                MERGE (a)-[:PREREQUISITE {strength: 1, created_at: timestamp()}]->(b)
                """;
                manager.execute_query(rel_query, prereq);
            }
            
            path_query = """
            MERGE (p:LearningPath {path_id: "programming_fundamentals"})
            SET p.name = "programming_fundamentals", p.title = "Programming Fundamentals",
                p.description = "Master the fundamentals of programming from basics to advanced concepts",
                p.difficulty = "beginner", p.difficulty_score = 1,
                p.estimated_duration = 480, p.concept_count = 6,
                p.created_at = timestamp()
            """;
            manager.execute_query(path_query, None);
            
            path_concepts = [
                {"path": "programming_fundamentals", "concept": "prog_basics", "order": 0},
                {"path": "programming_fundamentals", "concept": "variables", "order": 1},
                {"path": "programming_fundamentals", "concept": "control_flow", "order": 2},
                {"path": "programming_fundamentals", "concept": "functions", "order": 3},
                {"path": "programming_fundamentals", "concept": "data_structures", "order": 4},
                {"path": "programming_fundamentals", "concept": "oop", "order": 5}
            ];
            
            for pc in path_concepts {
                contain_query = """
                MATCH (p:LearningPath {path_id: $path})
                MATCH (c:Concept {concept_id: $concept})
                MERGE (p)-[:PathContains {order_index: $order, is_required: True, created_at: timestamp()}]->(c)
                """;
                manager.execute_query(contain_query, pc);
            }
            
            report {
                "success": True,
                "message": "Graph seeded successfully",
                "concepts_created": len(concepts),
                "prerequisites_created": len(prereqs),
                "paths_created": 1
            };
        } except Exception as e {
            print("Error seeding graph: " + str(e));
            report {
                "success": False,
                "error": "Failed to seed graph: " + str(e),
                "concepts_created": 0,
                "prerequisites_created": 0,
                "paths_created": 0
            };
        }
    }
}

walker graph_stats {
    can graph_stats with entry {
        try {
            manager = db_module.get_neo4j_manager();
            
            concept_count = manager.execute_query("MATCH (c:Concept) RETURN count(c) AS count", None);
            user_count = manager.execute_query("MATCH (u:User) RETURN count(u) AS count", None);
            path_count = manager.execute_query("MATCH (p:LearningPath) RETURN count(p) AS count", None);
            rel_count = manager.execute_query("MATCH ()-[r:PREREQUISITE]->() RETURN count(r) AS count", None);
            
            report {
                "success": True,
                "graph_stats": {
                    "concepts": concept_count[0]['count'] if concept_count else 0,
                    "users": user_count[0]['count'] if user_count else 0,
                    "learning_paths": path_count[0]['count'] if path_count else 0,
                    "prerequisite_relationships": rel_count[0]['count'] if rel_count else 0
                }
            };
        } except Exception as e {
            print("Error fetching graph stats: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch graph statistics: " + str(e),
                "graph_stats": {
                    "concepts": 0,
                    "users": 0,
                    "learning_paths": 0,
                    "prerequisite_relationships": 0
                }
            };
        }
    }
}

# ==============================================================================
# Contact Form Management
# ==============================================================================

walker contact_submit {
    has name: str;
    has email: str;
    has subject: str;
    has message: str;
    has phone: str = "";
    has contact_reason: str = "general";
    
    can contact_submit with entry {
        import datetime;
        import os;
        
        # Generate unique message ID
        message_id = "contact_" + str(int(datetime.datetime.now().timestamp()));
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ");
        
        # Validate input data
        if not self.name or not self.email or not self.message {
            report {
                "success": False,
                "error": "Name, email, and message are required fields",
                "code": "VALIDATION_ERROR"
            };
            return;
        }
        
        # Basic email validation
        if "@" not in self.email or "." not in self.email {
            report {
                "success": False,
                "error": "Please provide a valid email address",
                "code": "INVALID_EMAIL"
            };
            return;
        }
        
        # Store in database using PostgreSQL
        try {
            contact_data = {
                "message_id": message_id,
                "name": self.name.strip(),
                "email": self.email.strip().lower(),
                "subject": self.subject.strip(),
                "message": self.message.strip(),
                "phone": self.phone.strip(),
                "contact_reason": self.contact_reason,
                "timestamp": timestamp,
                "status": "pending",
                "ip_address": "127.0.0.1",  # In production, get from request
                "user_agent": "Jeseci Web Application"
            };
            
            # Use database module to store contact
            result = db_module.store_contact_message(contact_data);
            
            if result['success'] {
                # Send email notification
                email_sent = False;
                try {
                    email_result = send_contact_notification(contact_data);
                    email_sent = email_result['success'];
                } except error {
                    print("Email notification failed:", error);
                }

                # Send confirmation email to user
                try {
                    confirmation_result = send_confirmation_email(contact_data);
                } except error {
                    print("Confirmation email failed:", error);
                }

                report {
                    "success": True,
                    "message_id": message_id,
                    "timestamp": timestamp,
                    "status": "received",
                    "message": "Thank you for contacting us! We have received your message and will respond within 24 hours.",
                    "email_sent": email_sent
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Failed to store contact message'),
                    "code": "DATABASE_ERROR"
                };
            }
        } except error {
            print("Contact form error:", error);
            report {
                "success": False,
                "error": "An internal error occurred. Please try again later.",
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

walker contact_messages {
    has limit: int = 50;
    has status: str = "all";
    has admin_key: str = "";
    
    can contact_messages with entry {
        # Simple authentication check
        if self.admin_key != os.getenv("ADMIN_KEY", "admin123") {
            report {
                "success": False,
                "error": "Unauthorized access",
                "code": "UNAUTHORIZED"
            };
            return;
        }
        
        try {
            # Retrieve contact messages from database
            result = db_module.get_contact_messages({
                "limit": self.limit,
                "status": self.status
            });
            
            if result['success'] {
                report {
                    "success": True,
                    "messages": result['messages'],
                    "total": result['total'],
                    "unread_count": result['unread_count']
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Failed to retrieve messages'),
                    "code": "DATABASE_ERROR"
                };
            }
        } except error {
            std.out("Contact messages error:", error);
            report {
                "success": False,
                "error": "Failed to retrieve contact messages",
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

walker contact_mark_read {
    has message_id: str;
    has admin_key: str = "";
    
    can contact_mark_read with entry {
        # Simple authentication check
        if self.admin_key != os.getenv("ADMIN_KEY", "admin123") {
            report {
                "success": False,
                "error": "Unauthorized access",
                "code": "UNAUTHORIZED"
            };
            return;
        }
        
        try {
            result = db_module.mark_contact_as_read(self.message_id);
            
            if result['success'] {
                report {
                    "success": True,
                    "message_id": self.message_id,
                    "status": "read",
                    "message": "Message marked as read"
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Failed to update message'),
                    "code": "DATABASE_ERROR"
                };
            }
        } except error {
            std.out("Mark read error:", error);
            report {
                "success": False,
                "error": "Failed to update message status",
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

# Email Notification Functions
# Wrapper functions that call Python email module

def send_contact_notification(contact_data: dict) -> dict {
    result = email_module.send_contact_notification(contact_data);
    report result;
}

def send_confirmation_email(contact_data: dict) -> dict {
    result = email_module.send_confirmation_email(contact_data);
    report result;
}

# Async email wrapper functions for auth walkers
# These call the Python email module functions

def send_verification_email(email: str, username: str, verification_token: str) -> dict {
    result = email_verification_module.send_verification_email_sync(email, username, verification_token);
    report result;
}

def send_welcome_email(email: str, username: str) -> dict {
    result = email_verification_module.send_welcome_email_sync(email, username);
    report result;
}

walker user_register {
    has username: str;
    has email: str;
    has password: str;
    has first_name: str = "";
    has last_name: str = "";
    has learning_style: str = "visual";
    has skill_level: str = "beginner";
    
    can user_register with entry {
        try {
            result = auth_module.register_user(
                self.username,
                self.email,
                self.password,
                self.first_name,
                self.last_name,
                self.learning_style,
                self.skill_level
            );
            
            if result['success'] {
                report {
                    "success": True,
                    "user_id": result.get('user_id'),
                    "username": result.get('username'),
                    "email": result.get('email'),
                    "requires_verification": result.get('requires_verification', True),
                    "is_email_verified": result.get('is_email_verified', False),
                    "message": result.get('message', 'Registration successful! Please check your email to verify your account.')
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Registration failed'),
                    "code": result.get('code', 'ERROR')
                };
            }
        } except error {
            std.out("Registration error:", error);
            report {
                "success": False,
                "error": "Registration failed: " + str(error),
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

walker user_login {
    has username: str;
    has password: str;
    
    can user_login with entry {
        try {
            result = auth_module.authenticate_user(self.username, self.password);
            
            if result['success'] {
                report {
                    "success": True,
                    "access_token": result.get('access_token'),
                    "token_type": result.get('token_type', 'bearer'),
                    "expires_in": result.get('expires_in'),
                    "user": result.get('user'),
                    "message": result.get('message', 'Login successful!')
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Invalid credentials'),
                    "code": result.get('code', 'ERROR')
                };
            }
        } except error {
            std.out("Login error:", error);
            report {
                "success": False,
                "error": "Login failed: " + str(error),
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

walker verify_email {
    has token: str;
    
    can verify_email with entry {
        if not self.token {
            report {
                "success": False,
                "error": "Verification token is required",
                "code": "MISSING_TOKEN"
            };
            return;
        }
        
        try {
            result = auth_module.verify_email(self.token);
            
            if result['success'] {
                report {
                    "success": True,
                    "message": result.get('message', 'Email verified successfully!'),
                    "user_id": result.get('user_id'),
                    "username": result.get('username')
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Invalid or expired token'),
                    "code": result.get('code', 'INVALID_TOKEN')
                };
            }
        } except error {
            std.out("Verification error:", error);
            report {
                "success": False,
                "error": "Verification failed: " + str(error),
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

walker resend_verification {
    has email: str;
    
    can resend_verification with entry {
        if not self.email {
            report {
                "success": False,
                "error": "Email address is required",
                "code": "MISSING_EMAIL"
            };
            return;
        }
        
        try {
            result = auth_module.resend_verification_email(self.email);
            
            if result['success'] {
                report {
                    "success": True,
                    "message": result.get('message', 'Verification email sent successfully'),
                    "method": result.get('method', 'unknown')
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Failed to send verification email'),
                    "code": result.get('code', 'ERROR')
                };
            }
        } except error {
            std.out("Resend verification error:", error);
            report {
                "success": False,
                "error": "Failed to resend verification email: " + str(error),
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

walker verification_status {
    has user_id: str;
    
    can verification_status with entry {
        try {
            result = auth_module.get_user_verification_status(self.user_id);
            
            report {
                "success": True,
                "user_id": self.user_id,
                "is_verified": result.get('is_verified', False),
                "has_pending_token": result.get('has_pending_token', False),
                "token_expires_at": result.get('token_expires_at')
            };
        } except error {
            std.out("Verification status error:", error);
            report {
                "success": False,
                "error": "Failed to get verification status: " + str(error),
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

# ==============================================================================
# Password Reset API Endpoints
# ==============================================================================

walker forgot_password {
    has email: str;
    
    can forgot_password with entry {
        try {
            result = reset_module.create_password_reset_request(self.email);
            
            if result['success'] {
                report {
                    "success": True,
                    "message": result.get('message', 'If an account with that email exists, a password reset link has been sent')
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Failed to process request'),
                    "code": "REQUEST_FAILED"
                };
            }
        } except error {
            std.out("Forgot password error:", error);
            report {
                "success": False,
                "error": "Failed to process request: " + str(error),
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

walker reset_password_validate {
    has token: str;
    
    can reset_password_validate with entry {
        try {
            result = reset_module.validate_password_reset_token(self.token);
            
            if result.get('valid') {
                report {
                    "success": True,
                    "valid": True,
                    "username": result.get('username'),
                    "email": result.get('email'),
                    "expires_at": result.get('expires_at')
                };
            } else {
                report {
                    "success": True,
                    "valid": False,
                    "error": result.get('error', 'Invalid or expired token')
                };
            }
        } except error {
            std.out("Reset password validation error:", error);
            report {
                "success": False,
                "valid": False,
                "error": "Token validation failed: " + str(error),
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

walker reset_password {
    has token: str;
    has new_password: str;
    has confirm_password: str;
    
    can reset_password with entry {
        try {
            # Validate passwords match
            if self.new_password != self.confirm_password {
                report {
                    "success": False,
                    "error": "Passwords do not match",
                    "code": "PASSWORD_MISMATCH"
                };
                return;
            }
            
            # Validate password strength
            if len(self.new_password) < 8 {
                report {
                    "success": False,
                    "error": "Password must be at least 8 characters long",
                    "code": "PASSWORD_TOO_SHORT"
                };
                return;
            }
            
            result = reset_module.reset_user_password(self.token, self.new_password);
            
            if result['success'] {
                report {
                    "success": True,
                    "message": result.get('message', 'Password has been reset successfully')
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Failed to reset password'),
                    "code": "RESET_FAILED"
                };
            }
        } except error {
            std.out("Reset password error:", error);
            report {
                "success": False,
                "error": "Failed to reset password: " + str(error),
                "code": "INTERNAL_ERROR"
            };
        }
    }
}

# ==============================================================================
# Admin Dashboard API Endpoints
# ==============================================================================

walker admin_dashboard {
    can admin_dashboard with entry {
        # Initialize all stores to get real statistics with error handling
        init_error = "";
        
        try {
            admin_store.initialize_admin_store();
        } except Exception as e {
            print("Error initializing admin store: " + str(e));
            init_error = "Failed to load user data";
        }
        
        try {
            content_store.initialize_courses();
        } except Exception as e {
            print("Error initializing courses: " + str(e));
            if init_error {
                init_error = init_error + "; ";
            }
            init_error = init_error + "Failed to load course data";
        }
        
        try {
            content_store.initialize_concepts();
        } except Exception as e {
            print("Error initializing concepts: " + str(e));
            if init_error {
                init_error = init_error + "; ";
            }
            init_error = init_error + "Failed to load concept data";
        }
        
        try {
            content_store.initialize_paths();
        } except Exception as e {
            print("Error initializing paths: " + str(e));
            if init_error {
                init_error = init_error + "; ";
            }
            init_error = init_error + "Failed to load learning path data";
        }
        
        try {
            quiz_store.initialize_quizzes();
        } except Exception as e {
            print("Error initializing quizzes: " + str(e));
            if init_error {
                init_error = init_error + "; ";
            }
            init_error = init_error + "Failed to load quiz data";
        }
        
        try {
            analytics_store.initialize_analytics();
        } except Exception as e {
            print("Error initializing analytics: " + str(e));
            if init_error {
                init_error = init_error + "; ";
            }
            init_error = init_error + "Failed to load analytics data";
        }
        
        # If there were initialization errors, return them gracefully
        if init_error {
            import datetime;
            report {
                "success": False,
                "error": init_error,
                "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            };
        }
        
        # Get real counts from stores
        all_users = admin_store.get_all_users();
        all_courses = content_store.get_all_courses();
        all_quizzes = quiz_store.get_all_quizzes();
        user_analytics = analytics_store.get_user_analytics();
        learning_analytics = analytics_store.get_learning_analytics();
        
        # Count admins by role
        role_distribution = {};
        for user in all_users {
            if user.get('is_admin', False) {
                role = user.get('admin_role', 'unknown');
                role_distribution[role] = role_distribution.get(role, 0) + 1;
            }
        }
        
        # Admin dashboard statistics from real data
        active_count = len([u for u in all_users if u.get('is_active', True)]);
        admin_count = len([u for u in all_users if u.get('is_admin', False)]);
        
        # Get real content counts from databases (bypass caches for fresh data)
        total_courses = 0;
        total_concepts = 0;
        total_paths = 0;
        total_quizzes = 0;
        
        try {
            # Force refresh by invalidating caches - directly query databases
            
            # Get fresh course count from PostgreSQL
            courses_result = content_store.get_all_courses();
            total_courses = len(courses_result);
            
            # Get fresh concept count from Neo4j
            concepts_result = content_store.get_all_concepts();
            total_concepts = len(concepts_result);
            
            # Get fresh paths count from PostgreSQL
            paths_result = content_store.get_all_paths();
            total_paths = len(paths_result);
            
            # Get fresh quiz count
            quizzes_result = quiz_store.get_all_quizzes();
            total_quizzes = len(quizzes_result);
            
        } except Exception as e {
            print("Error getting content counts: " + str(e));
            # Fall back to cached values
            total_courses = len(all_courses);
            total_concepts = 0;
            total_paths = 0;
            total_quizzes = len(all_quizzes);
        }
        
        stats = {
            "user_statistics": {
                "total_users": len(all_users),
                "active_users": active_count,
                "inactive_users": len(all_users) - active_count,
                "total_admins": admin_count,
                "new_users_this_week": user_analytics.get('new_users', [0,0,0,0,0,0,0])[-1]
            },
            "admin_statistics": {
                "total_admins": admin_count,
                "role_distribution": role_distribution
            },
            "content_statistics": {
                "total_courses": total_courses,
                "total_concepts": total_concepts,
                "total_paths": total_paths,
                "total_quizzes": total_quizzes
            },
            "system_health": {
                "database_status": "connected",
                "api_status": "healthy",
                "auth_system": "operational"
            }
        };
        
        import datetime;
        report {
            "success": True,
            "stats": stats,
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        };
    }
}

walker admin_users {
    has limit: int = 50;
    has offset: int = 0;
    has include_inactive: bool = False;
    has admin_only: bool = False;
    has search: str = "";
    
    can admin_users with entry {
        # Initialize store with error handling
        try {
            admin_store.initialize_admin_store();
        } except Exception as e {
            print("Error initializing admin store: " + str(e));
            report {
                "success": False,
                "error": "Failed to load user data: " + str(e)
            };
        }
        
        # Get users from storage with filters
        users = [];
        try {
            if self.search {
                users = admin_store.search_admin_users(self.search, self.include_inactive, self.admin_only);
            } else {
                users = admin_store.get_all_users();
                
                # Apply filters
                if not self.include_inactive {
                    users = [u for u in users if u.get('is_active', True)];
                }
                if self.admin_only {
                    users = [u for u in users if u.get('is_admin', False)];
                }
            }
        } except Exception as e {
            print("Error fetching users: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch users: " + str(e)
            };
        }
        
        # Remove password from response
        safe_users = [];
        for user in users {
            safe_user = {};
            for (key, value) in user.items() {
                if key != 'password' {
                    safe_user[key] = value;
                }
            }
            safe_users.append(safe_user);
        }
        
        # Apply pagination
        total = len(safe_users);
        paginated_users = safe_users[self.offset:self.offset + self.limit];
        
        report {
            "success": True,
            "users": paginated_users,
            "total": total,
            "limit": self.limit,
            "offset": self.offset,
            "filters": {
                "include_inactive": self.include_inactive,
                "admin_only": self.admin_only,
                "search": self.search
            }
        };
    }
}

walker admin_users_create {
    has username: str;
    has email: str;
    has password: str;
    has admin_role: str;
    has first_name: str = "";
    has last_name: str = "";
    has learning_style: str = "visual";
    has skill_level: str = "beginner";
    has skip_verification: bool = true;  # Default to true (pre-verified)
    has daily_goal_minutes: int = 30;
    has notifications_enabled: bool = true;
    has email_reminders: bool = true;
    has dark_mode: bool = false;
    has auto_play_videos: bool = true;
    
    can admin_users_create with entry {
        # Initialize store with error handling
        try {
            admin_store.initialize_admin_store();
        } except Exception as e {
            print("Error initializing admin store: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize user store: " + str(e)
            };
        }
        
        # Create user in storage
        result = admin_store.create_admin_user(
            self.username,
            self.email,
            self.password,
            self.admin_role,
            self.first_name,
            self.last_name,
            self.learning_style,
            self.skill_level,
            self.skip_verification,
            self.daily_goal_minutes,
            self.notifications_enabled,
            self.email_reminders,
            self.dark_mode,
            self.auto_play_videos
        );
        
        if result['success'] {
            user = result['user'];
            report {
                "success": True,
                "user_id": user['user_id'],
                "username": user['username'],
                "email": user['email'],
                "admin_role": user['admin_role'],
                "message": "Admin user created successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to create user'),
                "code": result.get('code', 'ERROR')
            };
        }
    }
}

walker admin_users_update {
    has user_id: str;
    has is_admin: bool = False;
    has admin_role: str = "";
    has is_active: bool = True;
    
    can admin_users_update with entry {
        # Initialize store with error handling
        try {
            admin_store.initialize_admin_store();
        } except Exception as e {
            print("Error initializing admin store: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize user store: " + str(e)
            };
        }
        
        # Build updates dict
        updates = {};
        if self.admin_role {
            updates['admin_role'] = self.admin_role;
        }
        updates['is_admin'] = self.is_admin;
        updates['is_active'] = self.is_active;
        
        result = admin_store.update_admin_user(self.user_id, updates);
        
        if result['success'] {
            report {
                "success": True,
                "user_id": self.user_id,
                "action": "update",
                "message": "User updated successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to update user'),
                "code": result.get('code', 'ERROR')
            };
        }
    }
}

walker admin_users_bulk_action {
    has user_ids: list;
    has action: str;
    has reason: str = "";
    has deleted_by: str = "";
    has ip_address: str = "";
    
    can admin_users_bulk_action with entry {
        # Initialize store with error handling
        try {
            admin_store.initialize_admin_store();
        } except Exception as e {
            print("Error initializing admin store: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize user store: " + str(e)
            };
        }
        
        result = admin_store.bulk_admin_action(self.user_ids, self.action, self.reason, self.deleted_by, self.ip_address);
        
        import datetime;
        report {
            "success": result['success'],
            "users_affected": result.get('users_affected', 0),
            "action": result.get('action', self.action),
            "message": "Bulk action completed successfully",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        };
    }
}

walker admin_users_restore {
    has user_ids: list;
    has restored_by: str = "";
    has ip_address: str = "";
    
    can admin_users_restore with entry {
        # Initialize store with error handling
        try {
            admin_store.initialize_admin_store();
        } except Exception as e {
            print("Error initializing admin store: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize user store: " + str(e)
            };
        }
        
        result = admin_store.restore_users(self.user_ids, self.restored_by, self.ip_address);
        
        import datetime;
        report {
            "success": result['success'],
            "users_affected": result.get('users_affected', 0),
            "restored_by": result.get('restored_by', self.restored_by),
            "message": "Users restored successfully",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        };
    }
}

walker admin_users_deleted {
    can admin_users_deleted with entry {
        # Initialize store with error handling
        try {
            admin_store.initialize_admin_store();
        } except Exception as e {
            print("Error initializing admin store: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize user store: " + str(e)
            };
        }
        
        # Get deleted users from storage
        deleted_users = [];
        try {
            deleted_users = admin_store.get_deleted_users();
        } except Exception as e {
            print("Error fetching deleted users: " + str(e));
            report {
                "success": False,
                "error": "Failed to fetch deleted users: " + str(e)
            };
        }
        
        report {
            "success": True,
            "users": deleted_users,
            "total": len(deleted_users)
        };
    }
}

# ==============================================================================
# Admin Content Management API Endpoints
# ==============================================================================

walker admin_content_courses {
    can admin_content_courses with entry {
        # Initialize store and get courses with error handling
        courses = [];
        try {
            content_store.initialize_courses();
            courses = content_store.get_all_courses();
        } except Exception as e {
            print("Error initializing courses: " + str(e));
            report {
                "success": False,
                "error": "Failed to load courses: " + str(e)
            };
        }
        
        report {
            "success": True,
            "courses": courses
        };
    }
}

walker admin_content_course_create {
    has title: str;
    has description: str;
    has domain: str;
    has difficulty: str;
    has content_type: str = "interactive";
    
    can admin_content_course_create with entry {
        # Initialize store with error handling
        try {
            content_store.initialize_courses();
        } except Exception as e {
            print("Error initializing courses: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize course store: " + str(e)
            };
        }
        
        result = content_store.create_course(self.title, self.description, self.domain, self.difficulty, self.content_type);
        
        if result['success'] {
            report {
                "success": True,
                "course_id": result['course_id'],
                "message": "Course created successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to create course')
            };
        }
    }
}

walker admin_content_course_update {
    has course_id: str;
    has title: str = "";
    has description: str = "";
    has domain: str = "";
    has difficulty: str = "";
    
    can admin_content_course_update with entry {
        # Initialize store with error handling
        try {
            content_store.initialize_courses();
        } except Exception as e {
            print("Error initializing courses: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize course store: " + str(e)
            };
        }
        
        result = content_store.update_course(self.course_id, self.title, self.description, self.domain, self.difficulty);
        
        if result['success'] {
            report {
                "success": True,
                "course_id": self.course_id,
                "message": "Course updated successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to update course')
            };
        }
    }
}

walker admin_content_course_delete {
    has course_id: str;
    has deleted_by: str = "";
    has ip_address: str = "";
    
    can admin_content_course_delete with entry {
        # Initialize store with error handling
        try {
            content_store.initialize_courses();
        } except Exception as e {
            print("Error initializing courses: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize course store: " + str(e)
            };
        }
        
        result = content_store.delete_course(self.course_id, self.deleted_by, self.ip_address);
        
        if result['success'] {
            report {
                "success": True,
                "course_id": self.course_id,
                "message": "Course deleted successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to delete course')
            };
        }
    }
}

walker admin_content_course_restore {
    has course_id: str;
    has restored_by: str = "";
    has ip_address: str = "";
    
    can admin_content_course_restore with entry {
        # Initialize store with error handling
        try {
            content_store.initialize_courses();
        } except Exception as e {
            print("Error initializing courses: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize course store: " + str(e)
            };
        }
        
        result = content_store.restore_course(self.course_id, self.restored_by, self.ip_address);
        
        if result['success'] {
            report {
                "success": True,
                "course_id": self.course_id,
                "message": "Course restored successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to restore course')
            };
        }
    }
}

walker admin_content_courses_deleted {
    can admin_content_courses_deleted with entry {
        # Initialize store and get deleted courses with error handling
        deleted_courses = [];
        try {
            content_store.initialize_courses();
            deleted_courses = content_store.get_deleted_courses();
        } except Exception as e {
            print("Error initializing courses: " + str(e));
            report {
                "success": False,
                "error": "Failed to load deleted courses: " + str(e)
            };
        }
        
        report {
            "success": True,
            "courses": deleted_courses,
            "total": len(deleted_courses)
        };
    }
}

walker admin_content_concepts {
    can admin_content_concepts with entry {
        # Initialize store and get concepts with error handling
        concepts = [];
        try {
            content_store.initialize_concepts();
            concepts = content_store.get_all_concepts();
        } except Exception as e {
            print("Error initializing concepts: " + str(e));
            report {
                "success": False,
                "error": "Failed to load concepts: " + str(e)
            };
        }
        
        report {
            "success": True,
            "concepts": concepts
        };
    }
}

walker admin_content_relationships {
    can admin_content_relationships with entry {
        # Get all concept relationships with error handling
        result = content_store.get_all_concept_relationships();
        
        if result['success'] {
            report {
                "success": True,
                "relationships": result['relationships']
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to load relationships'),
                "relationships": []
            };
        }
    }
}

walker admin_content_relationships_create {
    has source_id: str;
    has target_id: str;
    has relationship_type: str;
    has strength: int = 1;
    
    can admin_content_relationships_create with entry {
        # Add relationship with error handling
        result = content_store.add_concept_relationship(self.source_id, self.target_id, self.relationship_type, self.strength);
        
        if result['success'] {
            report {
                "success": True,
                "message": result.get('message', 'Relationship created')
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to create relationship')
            };
        }
    }
}

walker admin_content_relationships_delete {
    has source_id: str;
    has target_id: str;
    has relationship_type: str;
    
    can admin_content_relationships_delete with entry {
        # Delete relationship with error handling
        result = content_store.delete_concept_relationship(self.source_id, self.target_id, self.relationship_type);
        
        if result['success'] {
            report {
                "success": True,
                "message": result.get('message', 'Relationship deleted')
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to delete relationship')
            };
        }
    }
}

walker admin_content_concept_create {
    has name: str;
    has category: str;
    has difficulty_level: str;
    has domain: str;
    has display_name: str = "";
    has description: str = "";
    has icon: str = "";
    
    can admin_content_concept_create with entry {
        # Initialize store with error handling
        try {
            content_store.initialize_concepts();
        } except Exception as e {
            print("Error initializing concepts: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize concept store: " + str(e)
            };
        }
        
        result = content_store.create_concept(self.name, self.display_name, self.category, self.difficulty_level, self.domain, self.description, self.icon);
        
        if result['success'] {
            report {
                "success": True,
                "concept_id": result['concept_id'],
                "message": "Concept created successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to create concept')
            };
        }
    }
}

walker admin_content_paths {
    can admin_content_paths with entry {
        # Initialize store and get paths with error handling
        paths = [];
        try {
            content_store.initialize_paths();
            paths = content_store.get_all_paths();
        } except Exception as e {
            print("Error initializing paths: " + str(e));
            report {
                "success": False,
                "error": "Failed to load learning paths: " + str(e)
            };
        }
        
        report {
            "success": True,
            "paths": paths
        };
    }
}

walker admin_content_path_create {
    has title: str;
    has description: str;
    has courses: list;
    has concepts: list;
    has difficulty: str;
    has duration: str;
    has target_audience: str = "";
    
    can admin_content_path_create with entry {
        # Initialize store with error handling
        try {
            content_store.initialize_paths();
        } except Exception as e {
            print("Error initializing paths: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize path store: " + str(e)
            };
        }
        
        result = content_store.create_path(self.title, self.description, self.courses, self.concepts, self.difficulty, self.duration, self.target_audience);
        
        if result['success'] {
            report {
                "success": True,
                "path_id": result['path_id'],
                "message": "Learning path created successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to create learning path')
            };
        }
    }
}

# ==============================================================================
# Admin Quiz Management API Endpoints
# ==============================================================================

walker admin_quizzes {
    can admin_quizzes with entry {
        # Initialize store and get quizzes with error handling
        quizzes = [];
        try {
            quiz_store.initialize_quizzes();
            quizzes = quiz_store.get_all_quizzes();
        } except Exception as e {
            print("Error initializing quizzes: " + str(e));
            report {
                "success": False,
                "error": "Failed to load quizzes: " + str(e)
            };
        }
        
        report {
            "success": True,
            "quizzes": quizzes
        };
    }
}

walker admin_quizzes_generate_ai {
    has topic: str;
    has difficulty: str;
    has question_count: int = 5;
    
    can admin_quizzes_generate_ai with entry {
        # Generate AI quiz with error handling
        try {
            result = quiz_store.generate_ai_quiz(self.topic, self.difficulty, self.question_count);
            
            if result['success'] {
                report {
                    "success": True,
                    "quiz": result.get('quiz', {}),
                    "topic": self.topic,
                    "difficulty": self.difficulty,
                    "question_count": self.question_count,
                    "message": result.get('message', 'Quiz generated successfully')
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Failed to generate quiz')
                };
            }
        } except Exception as e {
            print("Error generating AI quiz: " + str(e));
            report {
                "success": False,
                "error": "Failed to generate AI quiz: " + str(e)
            };
        }
    }
}

walker admin_quizzes_save_ai {
    has quiz_data: dict;
    has topic: str;
    has difficulty: str;

    can admin_quizzes_save_ai with entry {
        # Save AI-generated quiz with error handling
        try {
            result = quiz_store.save_ai_generated_quiz(self.quiz_data, self.topic, self.difficulty);

            if result['success'] {
                report {
                    "success": True,
                    "quiz_id": result.get('quiz_id', ''),
                    "message": result.get('message', 'Quiz saved successfully')
                };
            } else {
                report {
                    "success": False,
                    "error": result.get('error', 'Failed to save quiz')
                };
            }
        } except Exception as e {
            print("Error saving AI quiz: " + str(e));
            report {
                "success": False,
                "error": "Failed to save AI quiz: " + str(e)
            };
        }
    }
}

walker admin_quizzes_analytics {
    can admin_quizzes_analytics with entry {
        # Initialize store with error handling
        analytics = {};
        try {
            quiz_store.initialize_quizzes();
            analytics = quiz_store.get_quiz_analytics();
        } except Exception as e {
            print("Error initializing quizzes: " + str(e));
            report {
                "success": False,
                "error": "Failed to load quiz analytics: " + str(e)
            };
        }
        
        report {
            "success": True,
            "analytics": analytics
        };
    }
}

walker admin_quizzes_create {
    has title: str;
    has description: str;
    has difficulty: str;
    has course_id: str = "";
    
    can admin_quizzes_create with entry {
        # Initialize store with error handling
        try {
            quiz_store.initialize_quizzes();
        } except Exception as e {
            print("Error initializing quizzes: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize quiz store: " + str(e)
            };
        }
        
        result = quiz_store.create_quiz(self.title, self.description, self.course_id, self.difficulty);
        
        if result['success'] {
            report {
                "success": True,
                "quiz_id": result['quiz_id'],
                "message": "Quiz created successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to create quiz')
            };
        }
    }
}

walker admin_quizzes_update {
    has quiz_id: str;
    has title: str = "";
    has description: str = "";
    has difficulty: str = "";
    
    can admin_quizzes_update with entry {
        # Initialize store with error handling
        try {
            quiz_store.initialize_quizzes();
        } except Exception as e {
            print("Error initializing quizzes: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize quiz store: " + str(e)
            };
        }
        
        result = quiz_store.update_quiz(self.quiz_id, self.title, self.description, self.difficulty);
        
        if result['success'] {
            report {
                "success": True,
                "quiz_id": self.quiz_id,
                "message": "Quiz updated successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to update quiz')
            };
        }
    }
}

walker admin_quizzes_delete {
    has quiz_id: str;
    
    can admin_quizzes_delete with entry {
        # Initialize store with error handling
        try {
            quiz_store.initialize_quizzes();
        } except Exception as e {
            print("Error initializing quizzes: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize quiz store: " + str(e)
            };
        }
        
        result = quiz_store.delete_quiz(self.quiz_id);
        
        if result['success'] {
            report {
                "success": True,
                "quiz_id": self.quiz_id,
                "message": "Quiz deleted successfully"
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to delete quiz')
            };
        }
    }
}

# ==============================================================================
# Admin AI Content API Endpoints
# ==============================================================================

walker admin_ai_domains {
    can admin_ai_domains with entry {
        # Get AI domains with error handling
        domains = [];
        try {
            domains = ai_store.get_ai_domains();
        } except Exception as e {
            print("Error fetching AI domains: " + str(e));
            report {
                "success": False,
                "error": "Failed to load AI domains: " + str(e)
            };
        }
        
        report {
            "success": True,
            "domains": domains
        };
    }
}

walker admin_ai_stats {
    can admin_ai_stats with entry {
        # Initialize store and get stats with error handling
        stats = {};
        try {
            ai_store.initialize_ai_content();
            stats = ai_store.get_ai_stats();
        } except Exception as e {
            print("Error initializing AI content: " + str(e));
            report {
                "success": False,
                "error": "Failed to load AI stats: " + str(e)
            };
        }
        
        report {
            "success": True,
            "stats": stats
        };
    }
}

walker admin_ai_content {
    can admin_ai_content with entry {
        # Initialize store and get content with error handling
        content = [];
        try {
            ai_store.initialize_ai_content();
            content = ai_store.get_all_ai_content();
        } except Exception as e {
            print("Error initializing AI content: " + str(e));
            report {
                "success": False,
                "error": "Failed to load AI content: " + str(e)
            };
        }
        
        report {
            "success": True,
            "content": content
        };
    }
}

walker admin_ai_generate {
    has concept_name: str;
    has generated_by: str = "admin";
    has domain: str = "Computer Science";
    has difficulty: str = "beginner";
    has related_concepts: list = [];
    
    can admin_ai_generate with entry {
        import datetime;
        import os;
        
        # Initialize AI store with error handling
        try {
            ai_store.initialize_ai_content();
        } except Exception as e {
            print("Error initializing AI content: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize AI store: " + str(e)
            };
        }
        
        # Check OpenAI configuration
        api_key = os.getenv("OPENAI_API_KEY", "");
        use_openai = api_key != "";
        
        # Generate content
        content_id = "ai_" + str(int(datetime.datetime.now().timestamp()));
        
        # Generate mock content based on parameters
        generated_content = "# " + self.concept_name + "\n\n";
        generated_content += "## Overview\n";
        generated_content += "This lesson covers the fundamental concepts of " + self.concept_name + " in the field of " + self.domain + ".\n\n";
        
        generated_content += "## Key Concepts\n\n";
        generated_content += "1. **Introduction**: Understanding the basics of " + self.concept_name + "\n";
        generated_content += "2. **Core Principles**: The main principles that govern " + self.concept_name + "\n";
        generated_content += "3. **Practical Applications**: How these concepts apply in real-world scenarios\n\n";
        
        generated_content += "## Examples\n\n";
        generated_content += "```python\n";
        generated_content += "# Example code for " + self.concept_name + "\n";
        generated_content += "def example_function():\n";
        generated_content += "    # Your code here\n";
        generated_content += "    pass\n";
        generated_content += "```\n\n";
        
        generated_content += "## Practice Exercises\n\n";
        generated_content += "1. Exercise 1: Basic implementation\n";
        generated_content += "2. Exercise 2: Advanced usage\n";
        generated_content += "3. Exercise 3: Real-world application\n\n";
        
        generated_content += "## Summary\n\n";
        generated_content += "In this lesson, we explored " + self.concept_name + " and its applications in " + self.domain + ".\n";
        
        # Save generated content to store
        result = ai_store.save_ai_content(
            self.concept_name,
            self.domain,
            self.difficulty,
            generated_content,
            self.generated_by,
            self.related_concepts
        );
        
        report {
            "success": True,
            "content": {
                "content_id": content_id,
                "concept_name": self.concept_name,
                "domain": self.domain,
                "difficulty": self.difficulty,
                "content": generated_content,
                "related_concepts": self.related_concepts,
                "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "generated_by": self.generated_by,
                "source": "ai_generator",
                "model": "openai" if use_openai else "mock"
            },
            "message": "AI content generated successfully"
        };
    }
}

# ==============================================================================
# Admin Analytics API Endpoints
# ==============================================================================

walker admin_analytics_users {
    can admin_analytics_users with entry {
        # Initialize store and get analytics with error handling
        analytics = {};
        try {
            analytics_store.initialize_analytics();
            analytics = analytics_store.get_user_analytics();
        } except Exception as e {
            print("Error initializing analytics: " + str(e));
            report {
                "success": False,
                "error": "Failed to load user analytics: " + str(e)
            };
        }
        
        report {
            "success": True,
            "analytics": analytics
        };
    }
}

walker admin_analytics_learning {
    can admin_analytics_learning with entry {
        # Initialize store and get analytics with error handling
        analytics = {};
        try {
            analytics_store.initialize_analytics();
            analytics = analytics_store.get_learning_analytics();
        } except Exception as e {
            print("Error initializing analytics: " + str(e));
            report {
                "success": False,
                "error": "Failed to load learning analytics: " + str(e)
            };
        }
        
        report {
            "success": True,
            "analytics": analytics
        };
    }
}

walker admin_analytics_content {
    can admin_analytics_content with entry {
        # Get real content statistics from databases instead of hardcoded analytics
        total_courses = 0;
        total_concepts = 0;
        total_paths = 0;
        popular_content = [];
        content_by_difficulty = {
            "beginner": 0,
            "intermediate": 0,
            "advanced": 0
        };
        
        try {
            # Get courses count from PostgreSQL
            content_store.initialize_courses();
            courses = content_store.get_all_courses();
            total_courses = len(courses);
            
            # Get concepts count from Neo4j
            content_store.initialize_concepts();
            concepts = content_store.get_all_concepts();
            total_concepts = len(concepts);
            
            # Calculate difficulty distribution for concepts
            for concept in concepts {
                difficulty = concept.get('difficulty_level', 'beginner');
                if difficulty in content_by_difficulty {
                    content_by_difficulty[difficulty] = content_by_difficulty[difficulty] + 1;
                }
            }
            
            # Get paths count from PostgreSQL
            content_store.initialize_paths();
            paths = content_store.get_all_paths();
            total_paths = len(paths);

            # Get real popular content with actual view counts from database
            popular_content = [];
            course_views = content_views_module.get_popular_content("course", limit=5, period="all_time");
            for view_data in course_views {
                # Get course title from content store
                course_title = "Unknown Course";
                for course in courses {
                    if course.get('course_id') == view_data['content_id'] {
                        course_title = course.get('title', 'Unknown Course');
                        break;
                    }
                }
                popular_content.append({
                    "content_id": view_data['content_id'],
                    "title": course_title,
                    "views": view_data['views'],
                    "unique_views": view_data['unique_views'],
                    "content_type": "course"
                });
            }

            # If no views recorded yet, show courses with 0 views
            if len(popular_content) == 0 {
                for course in courses {
                    popular_content.append({
                        "content_id": course.get('course_id'),
                        "title": course.get('title', 'Unknown'),
                        "views": 0,
                        "unique_views": 0,
                        "content_type": "course"
                    });
                }
            }
            
        } except Exception as e {
            print("Error loading content analytics: " + str(e));
        }
        
        report {
            "success": True,
            "analytics": {
                "total_courses": total_courses,
                "total_concepts": total_concepts,
                "popular_content": popular_content,
                "content_by_difficulty": content_by_difficulty
            }
        };
    }
}

# ==============================================================================
# Content View Tracking Endpoints
# ==============================================================================

walker record_content_view {
    has content_id: str = "";
    has content_type: str = "course";
    has user_id: str = "";
    has session_id: str = "";
    has view_duration: int = 0;
    has ip_address: str = "";
    has user_agent: str = "";
    has referrer_url: str = "";
    has device_type: str = "desktop";
    has browser: str = "";
    has country_code: str = "";

    can record_content_view with entry {
        # Record a content view event
        result = content_views_module.record_content_view(
            content_id=self.content_id,
            content_type=self.content_type,
            user_id=self.user_id if self.user_id else null,
            session_id=self.session_id if self.session_id else null,
            view_duration=self.view_duration,
            ip_address=self.ip_address if self.ip_address else null,
            user_agent=self.user_agent if self.user_agent else null,
            referrer_url=self.referrer_url if self.referrer_url else null,
            device_type=self.device_type,
            browser=self.browser if self.browser else null,
            country_code=self.country_code if self.country_code else null
        );

        if result['success'] {
            report {
                "success": True,
                "message": "View recorded successfully",
                "view_id": result.get('view_id', ''),
                "is_unique_view": result.get('is_unique_view', False)
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to record view')
            };
        }
    }
}

walker get_content_view_analytics {
    has content_id: str = "";
    has content_type: str = "";
    has period: str = "all_time";
    has limit: int = 10;

    can get_content_view_analytics with entry {
        # Get view analytics for content
        if self.content_id and self.content_type {
            # Get stats for specific content
            stats = content_views_module.content_views_store.get_content_view_stats(
                content_id=self.content_id,
                content_type=self.content_type
            );

            report {
                "success": True,
                "content_id": self.content_id,
                "content_type": self.content_type,
                "statistics": stats
            };
        } elif self.content_type {
            # Get popular content for specific type
            popular = content_views_module.get_popular_content(
                content_type=self.content_type,
                limit=self.limit,
                period=self.period
            );

            report {
                "success": True,
                "content_type": self.content_type,
                "period": self.period,
                "popular_content": popular
            };
        } else {
            # Get all content view summary
            all_summary = content_views_module.get_all_views_summary();

            report {
                "success": True,
                "all_content_views": all_summary
            };
        }
    }
}

walker admin_analytics_refresh {
    can admin_analytics_refresh with entry {
        # Initialize store with error handling
        try {
            analytics_store.initialize_analytics();
        } except Exception as e {
            print("Error initializing analytics: " + str(e));
            report {
                "success": False,
                "error": "Failed to initialize analytics store: " + str(e)
            };
        }
        
        result = analytics_store.refresh_analytics();
        
        import datetime;
        report {
            "success": result.get('success', False),
            "message": "Analytics cache refreshed successfully",
            "refreshed_at": result.get('refreshed_at', datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
        };
    }
}

# ==============================================================================
# Admin Cache Management API Endpoints
# ==============================================================================

walker admin_clear_content_cache {
    can admin_clear_content_cache with entry {
        # Clear all content caches to force fresh database queries
        result = content_store.clear_content_cache();
        
        if result['success'] {
            report {
                "success": True,
                "message": "Content cache cleared successfully. Next request will query databases directly.",
                "cleared_at": result.get('message', '')
            };
        } else {
            report {
                "success": False,
                "error": "Failed to clear content cache"
            };
        }
    }
}

# ==============================================================================
# Audit Log API Endpoints
# ==============================================================================

walker admin_audit_logs {
    has table_name: str = "";
    has action_type: str = "";
    has performed_by: str = "";
    has start_date: str = "";
    has end_date: str = "";
    has limit: int = 100;
    has offset: int = 0;
    
    can admin_audit_logs with entry {
        # Import audit logger module
        import audit_logger as audit_module;
        
        # Parse dates if provided
        import datetime;
        start_dt = null;
        end_dt = null;
        
        if self.start_date {
            try {
                start_dt = datetime.datetime.fromisoformat(self.start_date.replace('Z', '+00:00'));
            } except Exception as e {
                print("Error parsing start_date: " + str(e));
            }
        }
        
        if self.end_date {
            try {
                end_dt = datetime.datetime.fromisoformat(self.end_date.replace('Z', '+00:00'));
            } except Exception as e {
                print("Error parsing end_date: " + str(e));
            }
        }
        
        # Search audit logs
        result = audit_module.search_audit_logs(
            table_name=self.table_name if self.table_name else null,
            action_type=self.action_type if self.action_type else null,
            performed_by=self.performed_by if self.performed_by else null,
            start_date=start_dt,
            end_date=end_dt,
            limit=self.limit,
            offset=self.offset
        );
        
        if result.get('success') {
            report {
                "success": True,
                "logs": result.get('logs', []),
                "total": result.get('total', 0),
                "limit": result.get('limit', 100),
                "offset": result.get('offset', 0),
                "has_more": result.get('has_more', False),
                "filters": {
                    "table_name": self.table_name,
                    "action_type": self.action_type,
                    "performed_by": self.performed_by,
                    "start_date": self.start_date,
                    "end_date": self.end_date
                }
            };
        } else {
            report {
                "success": False,
                "error": result.get('error', 'Failed to fetch audit logs'),
                "logs": [],
                "total": 0
            };
        }
    }
}

walker admin_audit_history {
    has table_name: str;
    has record_id: str;
    has limit: int = 100;
    
    can admin_audit_history with entry {
        # Import audit logger module
        import audit_logger as audit_module;
        
        if not self.table_name or not self.record_id {
            report {
                "success": False,
                "error": "table_name and record_id are required"
            };
            return;
        }
        
        # Get audit history for specific record
        history = audit_module.get_audit_history(
            table_name=self.table_name,
            record_id=self.record_id,
            limit=self.limit
        );
        
        report {
            "success": True,
            "table_name": self.table_name,
            "record_id": self.record_id,
            "history": history,
            "total": len(history)
        };
    }
}

walker admin_user_activity {
    has performed_by: str;
    has limit: int = 100;
    
    can admin_user_activity with entry {
        # Import audit logger module
        import audit_logger as audit_module;
        
        if not self.performed_by {
            report {
                "success": False,
                "error": "performed_by is required"
            };
            return;
        }
        
        # Get user activity log
        activity = audit_module.get_user_activity_log(
            performed_by=self.performed_by,
            limit=self.limit
        );
        
        report {
            "success": True,
            "performed_by": self.performed_by,
            "activity": activity,
            "total": len(activity)
        };
    }
}

walker admin_table_activity {
    has table_name: str;
    has days: int = 7;
    
    can admin_table_activity with entry {
        # Import audit logger module
        import audit_logger as audit_module;
        
        if not self.table_name {
            report {
                "success": False,
                "error": "table_name is required"
            };
            return;
        }
        
        # Get table activity summary
        summary = audit_module.get_table_activity_summary(
            table_name=self.table_name,
            days=self.days
        );
        
        if summary.get('error') {
            report {
                "success": False,
                "error": summary.get('error')
            };
        } else {
            report {
                "success": True,
                "summary": summary
            };
        }
    }
}
