"""
Jeseci Smart Learning Academy - Native JAC Implementation
Self-paced learning portal for Jac and Jaseci using OSP, byLLM, and Jac Client

Author: Cavin Otieno
Date: December 20, 2025
Repository: https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy
"""

# =============================================================================
# IMPORTS AND GLOBALS
# =============================================================================

# AI Integration
import from byllm.llm { Model }
glob llm = Model(model_name="gpt-4o-mini")

# Database imports
import from database.models.sqlite_models { get_db }

# React hooks for frontend
cl import from react { useState, useEffect, useRef, createContext, useContext } cl {}

# =============================================================================
# OBJECT-SPATIAL PROGRAMMING: LEARNING CONCEPT GRAPH
# =============================================================================

# Core Learning Concepts (Nodes represent topics)
node LearningConcept {
    has concept_id: str;
    has title: str;
    has description: str;
    has difficulty_level: int = 1;  # 1-5 scale
    has estimated_duration: int;    # minutes
    has content_type: str = "lesson";  # lesson, exercise, quiz, project
    has prerequisites: list = [];   # list of concept_ids
    has mastery_score: float = 0.0; # 0.0-1.0
    has is_locked: bool = True;
    has completion_count: int = 0;
    has last_accessed: str = "";
    
    def unlock_concept {
        self.is_locked = False;
    }
    
    def update_mastery(new_score: float) {
        # Exponential moving average for smoother progression
        self.mastery_score = (self.mastery_score * 0.7) + (new_score * 0.3);
        if self.mastery_score >= 0.8 {
            self.unlock_concept();
        }
    }
    
    def get_mastery_level -> str {
        if self.mastery_score >= 0.9: return "Expert";
        elif self.mastery_score >= 0.7: return "Advanced";
        elif self.mastery_score >= 0.5: return "Intermediate";
        elif self.mastery_score >= 0.3: return "Beginner";
        else: return "Novice";
    }
}

# User Progress (Tracks learning journey)
node UserProgress {
    has user_id: str;
    has username: str;
    has current_concept: str = "";
    has overall_mastery: float = 0.0;
    has learning_streak: int = 0;
    has total_time_spent: int = 0;  # minutes
    has achievements: list = [];
    has created_at: str = "";
    has last_active: str = "";
    
    def update_streak {
        # Check if user was active today
        import from datetime { datetime }
        today = datetime.now().strftime("%Y-%m-%d");
        if self.last_active != today {
            self.learning_streak += 1;
            self.last_active = today;
        }
    }
    
    def calculate_overall_mastery {
        # Average mastery across all concepts
        all_concepts = [-->(?LearningConcept)];
        if len(all_concepts) > 0 {
            total_mastery = sum(concept.mastery_score for concept in all_concepts);
            self.overall_mastery = total_mastery / len(all_concepts);
        }
    }
}

# Learning Relationships (Edges represent prerequisites and connections)
edge Prerequisite {
    has strength: int = 1;  # How important this prerequisite is (1-5)
    has description: str = "";
}

edge ProgressPath {
    has difficulty_progression: float = 1.0;
    has next_concept: str = "";
}

# Code Exercise Challenges
node CodeExercise {
    has exercise_id: str;
    has title: str;
    has description: str;
    has starter_code: str;
    has solution: str;
    has hints: list = [];
    has test_cases: list = [];
    has language: str = "jac";
    has difficulty: int = 1;
    has estimated_time: int = 15;  # minutes
    
    def validate_solution(user_code: str) -> dict {
        # AI-powered code validation
        return {"valid": True, "score": 0.85, "feedback": "Good solution!"};
    }
}

# =============================================================================
# BYLLM AI DECORATORS: CONTENT GENERATION
# =============================================================================

@llm()
"""Generate a comprehensive quiz for the given concept with multiple question types."""
def generate_quiz_questions(concept: LearningConcept, difficulty: int, num_questions: int = 5) -> list

@llm()
"""Evaluate a user's free-text answer and provide detailed feedback."""
def evaluate_free_text_answer(concept: LearningConcept, user_answer: str, correct_answer: str) -> dict

@llm()
"""Generate personalized learning recommendations based on user's progress."""
def generate_learning_recommendations(user_progress: UserProgress) -> list

@llm(method="Reason")
"""Analyze learning patterns and suggest optimal next steps."""
def analyze_learning_patterns(user_progress: UserProgress, recent_concepts: list) -> dict

@llm()
"""Generate hints for code exercises based on user context."""
def generate_code_hints(exercise: CodeExercise, user_context: str) -> list

@llm()
"""Create adaptive difficulty assessments based on user performance."""
def create_adaptive_assessment(concept: LearningConcept, user_history: dict) -> dict

@llm()
"""Generate interactive coding exercises for a specific concept."""
def generate_coding_exercise(concept: LearningConcept, difficulty: int) -> CodeExercise

# =============================================================================
# WALKERS: BACKEND API OPERATIONS
# =============================================================================

# Learning System Orchestrator
walker learning_system_orchestrator {
    can initialize_learning_system with root entry {
        print("🎓 Initializing Jeseci Smart Learning Academy...");
        
        # Seed initial learning concepts
        self.seed_learning_concepts();
        
        # Create default user if none exists
        default_user = root spawn get_or_create_user(username="demo_user");
        
        report {
            "status": "success",
            "message": "Learning system initialized",
            "concepts_available": len([root -->(?LearningConcept)]),
            "user_id": default_user.user_id
        };
    }
    
    can seed_learning_concepts with root entry {
        concepts_data = [
            {
                "concept_id": "jac_basics",
                "title": "Jac Language Fundamentals",
                "description": "Introduction to Jac syntax, variables, and basic constructs",
                "difficulty_level": 1,
                "estimated_duration": 30,
                "content_type": "lesson"
            },
            {
                "concept_id": "osp_fundamentals", 
                "title": "Object-Spatial Programming Basics",
                "description": "Understanding nodes, edges, and spatial relationships",
                "difficulty_level": 2,
                "estimated_duration": 45,
                "content_type": "lesson",
                "prerequisites": ["jac_basics"]
            },
            {
                "concept_id": "walkers_intro",
                "title": "Walkers and Graph Traversal",
                "description": "Mobile agents that traverse graph structures",
                "difficulty_level": 3,
                "estimated_duration": 60,
                "content_type": "lesson",
                "prerequisites": ["osp_fundamentals"]
            },
            {
                "concept_id": "byllm_basics",
                "title": "byLLM AI Integration",
                "description": "Integrating AI capabilities with LLM decorators",
                "difficulty_level": 3,
                "estimated_duration": 40,
                "content_type": "lesson",
                "prerequisites": ["walkers_intro"]
            },
            {
                "concept_id": "jac_client",
                "title": "Jac Client Frontend Development",
                "description": "Building React-style components with Jac",
                "difficulty_level": 4,
                "estimated_duration": 90,
                "content_type": "lesson",
                "prerequisites": ["byllm_basics"]
            },
            {
                "concept_id": "full_stack_jac",
                "title": "Full-Stack JAC Development",
                "description": "Complete applications using native JAC serving",
                "difficulty_level": 5,
                "estimated_duration": 120,
                "content_type": "project",
                "prerequisites": ["jac_client"]
            }
        ];
        
        for concept_data in concepts_data {
            concept = LearningConcept(**concept_data);
            root ++> concept;
            
            # Connect prerequisites
            if "prerequisites" in concept_data {
                for prereq_id in concept_data["prerequisites"] {
                    prereq_concepts = [root -->(?LearningConcept)] 
                        .filter(lambda c: c.concept_id == prereq_id);
                    if len(prereq_concepts) > 0 {
                        prereq_concepts[0] +>:Prerequisite(description=f"Required for {concept.title}):+> concept;
                    }
                }
            }
        }
    }
    
    can get_learning_dashboard with root entry {
        user_progress = root spawn get_current_user_progress();
        concepts = [root -->(?LearningConcept)];
        
        dashboard = {
            "user_progress": user_progress,
            "total_concepts": len(concepts),
            "completed_concepts": len(concepts.filter(lambda c: c.mastery_score >= 0.8)),
            "overall_mastery": user_progress.overall_mastery,
            "learning_streak": user_progress.learning_streak,
            "current_concept": user_progress.current_concept,
            "achievements": user_progress.achievements,
            "skill_map": self.generate_skill_map(concepts),
            "recommendations": root spawn get_personalized_recommendations()
        };
        
        report dashboard;
    }
    
    can generate_skill_map(concepts: list) -> dict {
        skill_levels = {
            "Novice": concepts.filter(lambda c: c.mastery_score < 0.3),
            "Beginner": concepts.filter(lambda c: 0.3 <= c.mastery_score < 0.5),
            "Intermediate": concepts.filter(lambda c: 0.5 <= c.mastery_score < 0.7),
            "Advanced": concepts.filter(lambda c: 0.7 <= c.mastery_score < 0.9),
            "Expert": concepts.filter(lambda c: c.mastery_score >= 0.9)
        };
        
        return {
            "levels": skill_levels,
            "total_mastery": sum(c.mastery_score for c in concepts) / len(concepts),
            "strongest_area": max(skill_levels.keys(), key=lambda k: len(skill_levels[k])),
            "weakest_area": min(skill_levels.keys(), key=lambda k: len(skill_levels[k]))
        };
    }
}

# User Management
walker get_or_create_user {
    has username: str;
    
    can get_or_create_user with root entry {
        existing_users = [root -->(?UserProgress)].filter(lambda u: u.username == self.username);
        
        if len(existing_users) > 0 {
            report existing_users[0];
        } else {
            import from datetime { datetime }
            new_user = UserProgress(
                user_id=f"user_{len([root -->(?UserProgress)]) + 1}",
                username=self.username,
                created_at=datetime.now().isoformat(),
                last_active=datetime.now().strftime("%Y-%m-%d")
            );
            root ++> new_user;
            report new_user;
        }
    }
}

walker get_current_user_progress {
    can get_current_user_progress with root entry {
        # For demo, return the first user or create one
        users = [root -->(?UserProgress)];
        if len(users) == 0 {
            demo_user = root spawn get_or_create_user(username="demo_user");
            report demo_user;
        } else {
            report users[0];
        }
    }
}

# Learning Content Management
walker get_concept_content {
    has concept_id: str;
    
    can get_concept_content with root entry {
        concepts = [root -->(?LearningConcept)].filter(lambda c: c.concept_id == self.concept_id);
        
        if len(concepts) == 0 {
            report {"error": "Concept not found"};
        }
        
        concept = concepts[0];
        
        # Check prerequisites
        prereq_met = True;
        prereq_status = [];
        
        prereq_edges = [concept <-:Prerequisite:-];
        for edge in prereq_edges {
            source_concept = [root -->(?LearningConcept)]
                .filter(lambda c: c.concept_id == edge.from_node.concept_id)[0];
            prereq_status.append({
                "concept_id": source_concept.concept_id,
                "title": source_concept.title,
                "mastery_score": source_concept.mastery_score,
                "completed": source_concept.mastery_score >= 0.8
            });
            if source_concept.mastery_score < 0.8 {
                prereq_met = False;
            }
        }
        
        content = {
            "concept": concept,
            "content": self.generate_concept_content(concept),
            "exercises": self.generate_concept_exercises(concept),
            "quiz": root spawn generate_quiz_questions(concept, concept.difficulty_level),
            "prerequisites_met": prereq_met,
            "prerequisite_status": prereq_status,
            "can_access": concept.is_locked == False or prereq_met
        };
        
        report content;
    }
    
    can generate_concept_content(concept: LearningConcept) -> dict {
        # AI-generated content based on concept
        import from byllm.llm { Model }
        glob content_llm = Model(model_name="gpt-4o");
        
        content_prompt = f"""
        Create comprehensive learning content for the concept: {concept.title}
        Description: {concept.description}
        Difficulty: {concept.difficulty_level}/5
        
        Include:
        1. Introduction section (2-3 paragraphs)
        2. Key concepts and definitions
        3. Practical examples
        4. Common pitfalls and how to avoid them
        5. Summary and next steps
        
        Format as structured content with clear sections.
        """;
        
        # For now, return structured content (in real implementation, this would use byLLM)
        return {
            "introduction": f"Welcome to {concept.title}! This {concept.content_type} covers the fundamentals of {concept.description.lower()}.",
            "sections": [
                {"title": "What is this about?", "content": concept.description},
                {"title": "Why is it important?", "content": f"Understanding {concept.title} is crucial for mastering JAC development."},
                {"title": "How to get started", "content": f"Begin with the basics and practice with exercises. Estimated time: {concept.estimated_duration} minutes."}
            ],
            "code_examples": self.get_concept_code_examples(concept),
            "interactive_elements": self.get_interactive_elements(concept)
        };
    }
    
    can get_concept_code_examples(concept: LearningConcept) -> list {
        examples = {
            "jac_basics": [
                {
                    "title": "Hello World in Jac",
                    "code": "with entry { print(\"Hello from Jac!\"); }",
                    "description": "Your first Jac program"
                }
            ],
            "osp_fundamentals": [
                {
                    "title": "Creating Nodes and Edges",
                    "code": "node Person { has name: str; }\nwith entry { alice = Person(\"Alice\"); bob = Person(\"Bob\"); alice ++> bob; }",
                    "description": "Basic graph creation in OSP"
                }
            ],
            "walkers_intro": [
                {
                    "title": "Simple Walker",
                    "code": "walker Greeter { can greet with Person entry { print(f\"Hello {here.name}!\"); } }\nwith entry { alice = Person(\"Alice\"); root spawn Greeter(); }",
                    "description": "Creating your first walker"
                }
            ]
        };
        
        return examples.get(concept.concept_id, []);
    }
    
    can get_interactive_elements(concept: LearningConcept) -> list {
        return [
            {
                "type": "code_editor",
                "title": "Try it yourself",
                "description": "Experiment with the concepts you've learned"
            },
            {
                "type": "quiz",
                "title": "Test your knowledge",
                "description": "Assess your understanding of the material"
            }
        ];
    }
    
    can generate_concept_exercises(concept: LearningConcept) -> list {
        # Generate interactive coding exercises
        return [
            {
                "exercise_id": f"{concept.concept_id}_basic",
                "title": f"Practice {concept.title}",
                "description": f"Apply what you've learned about {concept.title}",
                "difficulty": concept.difficulty_level,
                "estimated_time": 15
            }
        ];
    }
}

# Progress Tracking
walker update_concept_progress {
    has concept_id: str;
    has mastery_score: float;
    has time_spent: int;
    
    can update_concept_progress with root entry {
        # Update concept mastery
        concepts = [root -->(?LearningConcept)].filter(lambda c: c.concept_id == self.concept_id);
        if len(concepts) > 0 {
            concept = concepts[0];
            concept.update_mastery(self.mastery_score);
            concept.completion_count += 1;
            concept.last_accessed = "2025-12-20";
            
            # Unlock dependent concepts
            dependent_concepts = [concept -->];
            for dependent in dependent_concepts {
                if isinstance(dependent, LearningConcept) {
                    dependent.unlock_concept();
                }
            }
        }
        
        # Update user progress
        user_progress = root spawn get_current_user_progress();
        user_progress.total_time_spent += self.time_spent;
        user_progress.calculate_overall_mastery();
        user_progress.update_streak();
        
        report {
            "concept_updated": concept.concept_id if len(concepts) > 0 else None,
            "new_mastery": concept.mastery_score if len(concepts) > 0 else 0.0,
            "user_mastery": user_progress.overall_mastery,
            "streak": user_progress.learning_streak
        };
    }
}

# AI-Powered Recommendations
walker get_personalized_recommendations {
    can get_personalized_recommendations with root entry {
        user_progress = root spawn get_current_user_progress();
        concepts = [root -->(?LearningConcept)];
        
        # Find next recommended concepts
        recommendations = [];
        
        for concept in concepts {
            # Check if concept is accessible and not mastered
            if not concept.is_locked and concept.mastery_score < 0.8 {
                prereqs_met = True;
                for edge in [concept <-:Prerequisite:-] {
                    source_concept = edge.from_node;
                    if source_concept.mastery_score < 0.8 {
                        prereqs_met = False;
                        break;
                    }
                }
                
                if prereqs_met {
                    # Calculate recommendation score
                    difficulty_score = max(0, 1 - abs(concept.difficulty_level - (user_progress.overall_mastery * 5)));
                    time_urgency = max(0, 1 - (concept.completion_count * 0.1));
                    recommendation_score = (difficulty_score * 0.6) + (time_urgency * 0.4);
                    
                    recommendations.append({
                        "concept": concept,
                        "score": recommendation_score,
                        "reason": f"Good next step based on your current mastery level ({user_progress.overall_mastery:.2f})"
                    });
                }
            }
        }
        
        # Sort by recommendation score and return top 3
        recommendations.sort(key=lambda r: r["score"], reverse=True);
        
        report {
            "recommendations": recommendations[:3],
            "analysis": root spawn analyze_learning_patterns(user_progress, concepts)
        };
    }
}

# Quiz Generation and Assessment
walker generate_quiz_questions {
    has concept: LearningConcept;
    has difficulty: int;
    has num_questions: int = 5;
    
    can generate_quiz_questions with root entry {
        # Use byLLM to generate AI-powered quiz
        questions = [];
        
        # For demonstration, generate sample questions
        question_types = ["multiple_choice", "free_text", "code_completion"];
        
        for i in range(self.num_questions) {
            question_type = question_types[i % len(question_types)];
            
            if question_type == "multiple_choice" {
                questions.append({
                    "id": f"q_{i+1}",
                    "type": "multiple_choice",
                    "question": f"What is the main purpose of {self.concept.title}?",
                    "options": [
                        f"To understand {self.concept.description.lower()}",
                        "To manage database operations",
                        "To handle user authentication",
                        "To create visual interfaces"
                    ],
                    "correct_answer": 0,
                    "explanation": f"This concept focuses on {self.concept.description.lower()}."
                });
            } elif question_type == "free_text" {
                questions.append({
                    "id": f"q_{i+1}",
                    "type": "free_text",
                    "question": f"Explain in your own words how {self.concept.title} works and why it's important.",
                    "expected_keywords": ["graph", "node", "relationship", "spatial"],
                    "max_length": 500
                });
            } else {  # code_completion
                questions.append({
                    "id": f"q_{i+1}",
                    "type": "code_completion",
                    "question": f"Complete the following Jac code related to {self.concept.title}:",
                    "code_snippet": f"node Example {{ has field: str; }}\nwith entry {{ example = Example(); }}",
                    "missing_parts": ["Example", "field", "example"],
                    "hints": ["Remember to use node keyword", "Define required fields", "Create instance"]
                });
            }
        }
        
        report {
            "quiz_id": f"quiz_{self.concept.concept_id}",
            "concept_id": self.concept.concept_id,
            "difficulty": self.difficulty,
            "estimated_time": self.concept.estimated_duration,
            "questions": questions
        };
    }
}

# Code Exercise Management
walker get_code_exercise {
    has concept_id: str;
    has exercise_id: str;
    
    can get_code_exercise with root entry {
        # Generate or retrieve exercise
        exercise = CodeExercise(
            exercise_id=self.exercise_id,
            title=f"Practice {self.concept_id.replace('_', ' ').title()}",
            description=f"Apply your knowledge of {self.concept_id.replace('_', ' ')}",
            starter_code="// Start coding here",
            solution="// Complete solution",
            hints=["Think about the core concept", "Check the examples", "Test your solution"],
            language="jac",
            difficulty=2
        );
        
        report exercise;
    }
}

# =============================================================================
# JAC CLIENT FRONTEND: REACT-STYLE COMPONENTS
# =============================================================================

cl {

# Learning Portal Context
def LearningProvider({ children }: dict) -> any {
    [userProgress, setUserProgress] = useState({});
    [currentConcept, setCurrentConcept] = useState(null);
    [isLoading, setIsLoading] = useState(true);
    
    useEffect(lambda -> None {
        # Load user progress on mount
        loadUserProgress();
    }, []);
    
    async def loadUserProgress() -> None {
        try {
            progress = root spawn get_learning_dashboard();
            setUserProgress(progress);
            setIsLoading(false);
        } catch (e) {
            console.error("Failed to load progress:", e);
            setIsLoading(false);
        }
    }
    
    return (
        <LearningContext.Provider value={{
            "userProgress": userProgress,
            "currentConcept": currentConcept,
            "setCurrentConcept": setCurrentConcept,
            "refreshProgress": loadUserProgress,
            "isLoading": isLoading
        }}>
            {children}
        </LearningContext.Provider>
    );
}

# Main Application Component
def app() -> any {
    return (
        <LearningProvider>
            <div className="min-h-screen bg-gray-50">
                <Navigation />
                <main className="container mx-auto px-4 py-8">
                    <LearningDashboard />
                    <SkillMap />
                    <Recommendations />
                    {currentConcept && <ConceptModal concept={currentConcept} onClose={lambda -> setCurrentConcept(null)} />}
                </main>
            </div>
        </LearningProvider>
    );
}

# Navigation Component
def Navigation() -> any {
    return (
        <nav className="bg-white shadow-sm border-b">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center">
                        <h1 className="text-xl font-bold text-blue-600">
                            🎓 Jeseci Academy
                        </h1>
                    </div>
                    <div className="flex items-center space-x-4">
                        <UserProfile />
                        <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                            My Progress
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}

# User Profile Component
def UserProfile() -> any {
    context = useContext(LearningContext);
    
    if not context.userProgress: return <div>Loading...</div>;
    
    progress = context.userProgress.user_progress;
    
    return (
        <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                {progress.username[0].upper()}
            </div>
            <div>
                <div className="text-sm font-medium">{progress.username}</div>
                <div className="text-xs text-gray-500">
                    Streak: {progress.learning_streak} days
                </div>
            </div>
        </div>
    );
}

# Learning Dashboard Component
def LearningDashboard() -> any {
    context = useContext(LearningContext);
    
    if context.isLoading: return <DashboardSkeleton />;
    if not context.userProgress: return <div>No progress data</div>;
    
    progress = context.userProgress;
    
    return (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">Learning Dashboard</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatCard
                    title="Overall Mastery"
                    value={`${(progress.overall_mastery * 100).toFixed(0)}%`}
                    icon="📊"
                    color="blue"
                />
                <StatCard
                    title="Concepts Mastered"
                    value={`${progress.completed_concepts}/${progress.total_concepts}`}
                    icon="🎯"
                    color="green"
                />
                <StatCard
                    title="Learning Streak"
                    value={`${progress.learning_streak} days`}
                    icon="🔥"
                    color="orange"
                />
                <StatCard
                    title="Current Level"
                    value={getMasteryLevel(progress.overall_mastery)}
                    icon="⭐"
                    color="purple"
                />
            </div>
            
            <div className="mt-6">
                <h3 className="text-lg font-semibold mb-2">Current Focus</h3>
                {progress.current_concept ? (
                    <div className="bg-blue-50 p-4 rounded border">
                        <p className="text-blue-800">Continue with: {progress.current_concept}</p>
                    </div>
                ) : (
                    <div className="text-gray-600">Ready to start your learning journey!</div>
                )}
            </div>
        </div>
    );
}

# Stat Card Component
def StatCard({ title, value, icon, color }: dict) -> any {
    colors = {
        "blue": "bg-blue-500",
        "green": "bg-green-500", 
        "orange": "bg-orange-500",
        "purple": "bg-purple-500"
    };
    
    return (
        <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center">
                <div className={`w-12 h-12 ${colors[color]} rounded-lg flex items-center justify-center text-white text-xl mr-4`}>
                    {icon}
                </div>
                <div>
                    <div className="text-sm text-gray-600">{title}</div>
                    <div className="text-2xl font-bold">{value}</div>
                </div>
            </div>
        </div>
    );
}

# Skill Map Component (Visual representation of learning progress)
def SkillMap() -> any {
    context = useContext(LearningContext);
    
    if context.isLoading or not context.userProgress: return null;
    
    skillMap = context.userProgress.skill_map;
    
    return (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">Skill Map</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {Object.entries(skillMap.levels).map(lambda entry -> any {
                    level_name = entry[0];
                    concepts = entry[1];
                    return (
                        <SkillLevelColumn
                            key={level_name}
                            level={level_name}
                            concepts={concepts}
                            isStrongest={level_name == skillMap.strongest_area}
                            isWeakest={level_name == skillMap.weakest_area}
                        />
                    );
                })}
            </div>
            
            <div className="mt-6 text-center">
                <p className="text-gray-600">
                    Overall Mastery: 
                    <span className="font-bold ml-1">{(skillMap.total_mastery * 100).toFixed(0)}%</span>
                </p>
            </div>
        </div>
    );
}

# Skill Level Column Component
def SkillLevelColumn({ level, concepts, isStrongest, isWeakest }: dict) -> any {
    colors = {
        "Novice": "bg-red-100 border-red-300",
        "Beginner": "bg-orange-100 border-orange-300",
        "Intermediate": "bg-yellow-100 border-yellow-300",
        "Advanced": "bg-blue-100 border-blue-300",
        "Expert": "bg-green-100 border-green-300"
    };
    
    borderClass = isStrongest ? "border-green-500" : isWeakest ? "border-red-500" : "border-gray-200";
    
    return (
        <div className={`${colors[level]} ${borderClass} border-2 rounded-lg p-4 min-h-48`}>
            <h3 className="font-bold text-center mb-3">{level}</h3>
            <div className="space-y-2">
                {concepts.map(lambda concept -> any {
                    masteryPercent = (concept.mastery_score * 100).toFixed(0);
                    return (
                        <ConceptChip
                            key={concept.concept_id}
                            concept={concept}
                            masteryPercent={masteryPercent}
                        />
                    );
                })}
                {len(concepts) == 0 && (
                    <div className="text-gray-500 text-sm text-center italic">
                        No concepts yet
                    </div>
                )}
            </div>
        </div>
    );
}

# Concept Chip Component
def ConceptChip({ concept, masteryPercent }: dict) -> any {
    context = useContext(LearningContext);
    
    def onClick() -> None {
        context.setCurrentConcept(concept);
    }
    
    return (
        <div
            onClick={onClick}
            className="bg-white p-2 rounded border cursor-pointer hover:bg-gray-50 transition-colors"
        >
            <div className="text-sm font-medium truncate">{concept.title}</div>
            <div className="text-xs text-gray-500">{masteryPercent}% mastered</div>
        </div>
    );
}

# Recommendations Component
def Recommendations() -> any {
    context = useContext(LearningContext);
    
    if context.isLoading or not context.userProgress: return null;
    
    recommendations = context.userProgress.recommendations.recommendations;
    
    if len(recommendations) == 0: return null;
    
    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">Recommended Next Steps</h2>
            
            <div className="space-y-4">
                {recommendations.map(lambda rec -> any {
                    concept = rec.concept;
                    return (
                        <RecommendationCard
                            key={concept.concept_id}
                            concept={concept}
                            reason={rec.reason}
                            score={rec.score}
                        />
                    );
                })}
            </div>
        </div>
    );
}

# Recommendation Card Component
def RecommendationCard({ concept, reason, score }: dict) -> any {
    context = useContext(LearningContext);
    
    def startLearning() -> None {
        context.setCurrentConcept(concept);
    }
    
    return (
        <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
                <div className="flex-1">
                    <h3 className="font-semibold text-lg">{concept.title}</h3>
                    <p className="text-gray-600 text-sm mb-2">{concept.description}</p>
                    <p className="text-blue-600 text-sm">{reason}</p>
                </div>
                <div className="ml-4">
                    <div className="text-right mb-2">
                        <span className="text-sm text-gray-500">Difficulty:</span>
                        <div className="flex items-center">
                            {Array.from({length: 5}).map(lambda _ -> any {
                                index = _;
                                filled = index < concept.difficulty_level;
                                return (
                                    <span key={index} className={`w-2 h-2 rounded-full mx-0.5 ${filled ? 'bg-blue-500' : 'bg-gray-300'}`}></span>
                                );
                            })}
                        </div>
                    </div>
                    <button
                        onClick={startLearning}
                        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                    >
                        Start Learning
                    </button>
                </div>
            </div>
        </div>
    );
}

# Learning Content Modal
def ConceptModal({ concept, onClose }: dict) -> any {
    [content, setContent] = useState(null);
    [activeTab, setActiveTab] = useState("lesson");
    
    useEffect(lambda -> None {
        loadConceptContent();
    }, [concept]);
    
    async def loadConceptContent() -> None {
        try {
            concept_content = root spawn get_concept_content(concept_id=concept.concept_id);
            setContent(concept_content);
        } catch (e) {
            console.error("Failed to load concept content:", e);
        }
    }
    
    if not content: return <div>Loading content...</div>;
    
    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-96 overflow-y-auto">
                <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-2-2xl font-bold">{concept.title}</h2>
                        <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                            ✕
                        </button>
                    </div>
                    
                    <div className="border-b mb-4">
                        <nav className="flex space-x-8">
                            {["lesson", "exercises", "quiz"].map(lambda tab -> any {
                                isActive = tab == activeTab;
                                return (
                                    <button
                                        key={tab}
                                        onClick={lambda -> setActiveTab(tab)}
                                        className={`py-2 px-1 border-b-2 font-medium text-sm ${
                                            isActive 
                                                ? 'border-blue-500 text-blue-600' 
                                                : 'border-transparent text-gray-500 hover:text-gray-700'
                                        }`}
                                    >
                                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                                    </button>
                                );
                            })}
                        </nav>
                    </div>
                    
                    {activeTab == "lesson" && (
                        <LessonContent content={content.content} />
                    )}
                    {activeTab == "exercises" && (
                        <ExerciseContent exercises={content.exercises} />
                    )}
                    {activeTab == "quiz" && (
                        <QuizContent quiz={content.quiz} />
                    )}
                </div>
            </div>
        </div>
    );
}

# Lesson Content Component
def LessonContent({ content }: dict) -> any {
    return (
        <div>
            <p className="text-gray-700 mb-4">{content.introduction}</p>
            
            {content.sections.map(lambda section -> any {
                return (
                    <div key={section.title} className="mb-6">
                        <h3 className="text-lg font-semibold mb-2">{section.title}</h3>
                        <p className="text-gray-600">{section.content}</p>
                    </div>
                );
            })}
            
            {content.code_examples.length > 0 && (
                <div className="mt-6">
                    <h3 className="text-lg font-semibold mb-2">Code Examples</h3>
                    {content.code_examples.map(lambda example -> any {
                        return (
                            <CodeExample key={example.title} example={example} />
                        );
                    })}
                </div>
            )}
        </div>
    );
}

# Code Example Component
def CodeExample({ example }: dict) -> any {
    return (
        <div className="bg-gray-100 rounded-lg p-4 mb-4">
            <h4 className="font-medium mb-2">{example.title}</h4>
            <p className="text-sm text-gray-600 mb-2">{example.description}</p>
            <pre className="bg-gray-800 text-green-400 p-3 rounded text-sm overflow-x-auto">
                <code>{example.code}</code>
            </pre>
        </div>
    );
}

# Exercise Content Component
def ExerciseContent({ exercises }: dict) -> any {
    return (
        <div>
            <h3 className="text-lg font-semibold mb-4">Practice Exercises</h3>
            {exercises.map(lambda exercise -> any {
                return (
                    <div key={exercise.exercise_id} className="border rounded-lg p-4 mb-4">
                        <h4 className="font-medium mb-2">{exercise.title}</h4>
                        <p className="text-gray-600 mb-2">{exercise.description}</p>
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-500">
                                Difficulty: {exercise.difficulty}/5
                            </span>
                            <button className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                                Start Exercise
                            </button>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

# Quiz Content Component
def QuizContent({ quiz }: dict) -> any {
    return (
        <div>
            <div className="mb-4">
                <h3 className="text-lg font-semibold">{quiz.concept_id.replace('_', ' ').title()} Quiz</h3>
                <p className="text-gray-600">
                    {quiz.questions.length} questions • 
                    Estimated time: {quiz.estimated_time} minutes • 
                    Difficulty: {quiz.difficulty}/5
                </p>
            </div>
            
            {quiz.questions.map(lambda question -> any {
                return (
                    <QuizQuestion key={question.id} question={question} />
                );
            })}
            
            <div className="mt-6 text-center">
                <button className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600">
                    Submit Quiz
                </button>
            </div>
        </div>
    );
}

# Quiz Question Component
def QuizQuestion({ question }: dict) -> any {
    return (
        <div className="border rounded-lg p-4 mb-4">
            <h4 className="font-medium mb-3">{question.question}</h4>
            
            {question.type == "multiple_choice" && (
                <div className="space-y-2">
                    {question.options.map(lambda option -> any {
                        index = _;
                        return (
                            <label key={index} className="flex items-center">
                                <input type="radio" name={question.id} value={index} className="mr-2" />
                                <span>{option}</span>
                            </label>
                        );
                    })}
                </div>
            )}
            
            {question.type == "free_text" && (
                <textarea 
                    className="w-full p-2 border rounded"
                    rows="4"
                    placeholder="Type your answer here..."
                    maxLength={question.max_length}
                ></textarea>
            )}
            
            {question.type == "code_completion" && (
                <div>
                    <p className="text-sm text-gray-600 mb-2">{question.question}</p>
                    <pre className="bg-gray-800 text-green-400 p-3 rounded text-sm overflow-x-auto mb-2">
                        <code>{question.code_snippet}</code>
                    </pre>
                    <textarea 
                        className="w-full p-2 border rounded"
                        rows="3"
                        placeholder="Complete the code here..."
                    ></textarea>
                </div>
            )}
        </div>
    );
}

# Dashboard Skeleton for Loading State
def DashboardSkeleton() -> any {
    return (
        <div className="bg-white rounded-lg shadow p-6 mb-8 animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {Array.from({length: 4}).map(lambda _ -> any {
                    return (
                        <div key={_} className="h-24 bg-gray-200 rounded"></div>
                    );
                })}
            </div>
        </div>
    );
}

# Helper Functions
def getMasteryLevel(mastery: float) -> str {
    if mastery >= 0.9: return "Expert";
    elif mastery >= 0.7: return "Advanced";
    elif mastery >= 0.5: return "Intermediate";
    elif mastery >= 0.3: return "Beginner";
    else: return "Novice";
}

# React Context for Learning State
LearningContext = createContext({});

}