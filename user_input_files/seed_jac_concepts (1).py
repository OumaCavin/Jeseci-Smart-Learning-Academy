#!/usr/bin/env python3
"""
JAC Programming Language Concepts Seeding Script
Based on the comprehensive JAC Learning Guide provided
"""

import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from database.models.sqlite_models import (
    User, Concept, LearningPath, LearningPathConcept, 
    UserProgress, UserLearningPreferences
)

def create_jac_concepts(db: Session):
    """Create JAC programming concepts from the learning guide"""
    print("🎯 Creating JAC Programming Language Concepts...")
    
    # Check if JAC concepts already exist
    existing_jac_concepts = db.query(Concept).filter(Concept.category == "JAC Programming").count()
    if existing_jac_concepts > 0:
        print("✅ JAC concepts already exist")
        return
    
    # Define JAC concepts based on the learning guide
    jac_concepts = [
        {
            "name": "jac_programming_fundamentals",
            "display_name": "JAC Programming Fundamentals",
            "description": "Introduction to JAC (Java-like Architecture for Computation) programming language with Object-Spatial Programming paradigm",
            "detailed_description": "JAC is a revolutionary programming language that introduces Object-Spatial Programming (OSP) where computation moves to data, enabling scalable and distributed applications. It offers a unique dual paradigm: traditional programming and Object-Spatial Programming.",
            "category": "JAC Programming",
            "subcategory": "Introduction",
            "domain": "Computer Science",
            "difficulty_level": "beginner",
            "complexity_score": 6.0,
            "cognitive_load": 6.5,
            "key_terms": ["JAC", "Object-Spatial Programming", "OSP", "nodes", "edges", "walkers"],
            "synonyms": ["Java-like Architecture for Computation", "JAC Language"],
            "learning_objectives": [
                "Understand what JAC programming language is and its unique features",
                "Learn the dual programming paradigm approach",
                "Identify the advantages of Object-Spatial Programming",
                "Set up JAC development environment"
            ],
            "practical_applications": [
                "Building scalable distributed applications",
                "Creating graph-based data structures",
                "Developing applications with automatic persistence",
                "Implementing multi-user isolated systems"
            ],
            "real_world_examples": [
                "Social network applications with friend relationships",
                "Knowledge graph systems for educational content",
                "Distributed computing applications",
                "AI-powered recommendation systems"
            ],
            "common_misconceptions": [
                "JAC is just another programming language like Java",
                "Object-Spatial Programming is too complex for beginners",
                "Traditional programming concepts don't apply to JAC",
                "JAC only works for graph-based applications"
            ]
        },
        {
            "name": "jac_variables_data_types",
            "display_name": "JAC Variables and Data Types",
            "description": "Understanding JAC's type system, variable declarations, and data type annotations",
            "detailed_description": "JAC uses strong typing with type annotations for all variables and collections. Variables are declared with the assignment operator and require explicit type annotations. Supported types include str, int, float, bool, list, dict, set, and tuples.",
            "category": "JAC Programming",
            "subcategory": "Fundamentals",
            "domain": "Computer Science",
            "difficulty_level": "beginner",
            "complexity_score": 4.0,
            "cognitive_load": 4.5,
            "key_terms": ["variable", "type annotation", "string", "integer", "float", "boolean", "list", "dict", "set"],
            "synonyms": ["data types", "variable declaration", "type system"],
            "learning_objectives": [
                "Declare variables with proper type annotations",
                "Understand JAC's primitive data types",
                "Work with collection types (lists, dictionaries, sets)",
                "Use f-strings for string formatting"
            ],
            "practical_applications": [
                "Storing user information and profiles",
                "Managing collections of data",
                "Creating data structures for applications",
                "Implementing type-safe programming patterns"
            ],
            "real_world_examples": [
                "Student grade management system",
                "User profile with contact information",
                "Inventory tracking with quantities and prices",
                "Social media post data storage"
            ],
            "common_misconceptions": [
                "Type annotations are optional in JAC",
                "JAC uses dynamic typing like Python",
                "Collections don't need type specifications",
                "Type annotations only apply to function parameters"
            ]
        },
        {
            "name": "jac_control_flow",
            "display_name": "JAC Control Flow",
            "description": "Mastering conditional statements, loops, and pattern matching in JAC",
            "detailed_description": "JAC provides traditional control flow structures including if-elif-else statements, while loops, for loops (counting and iterating), and advanced pattern matching. All control structures use curly braces for block definition.",
            "category": "JAC Programming",
            "subcategory": "Fundamentals", 
            "domain": "Computer Science",
            "difficulty_level": "beginner",
            "complexity_score": 5.0,
            "cognitive_load": 5.5,
            "key_terms": ["if", "elif", "else", "while", "for", "break", "continue", "pattern matching", "comparison operators"],
            "synonyms": ["conditionals", "loops", "decision making", "iteration"],
            "learning_objectives": [
                "Write conditional statements with proper syntax",
                "Implement loops for repetitive tasks",
                "Use comparison and logical operators effectively",
                "Apply pattern matching for complex conditions"
            ],
            "practical_applications": [
                "User input validation and processing",
                "Data filtering and processing",
                "Game logic and state management",
                "Business rule implementation"
            ],
            "real_world_examples": [
                "Grade calculation and letter grade assignment",
                "User authentication and authorization",
                "Inventory management and stock checking",
                "Game scoring and level progression"
            ],
            "common_misconceptions": [
                "JAC uses Python-style indentation for blocks",
                "Pattern matching replaces all if-elif-else chains",
                "Loops automatically handle boundary conditions",
                "Comparison operators work the same as in other languages"
            ]
        },
        {
            "name": "jac_functions",
            "display_name": "JAC Functions",
            "description": "Creating reusable code blocks with parameters, return values, and default arguments",
            "detailed_description": "JAC functions are defined using the 'def' keyword with type annotations for parameters and return types. Functions support default parameters, named parameters, and can return values using the 'return' statement.",
            "category": "JAC Programming",
            "subcategory": "Fundamentals",
            "domain": "Computer Science",
            "difficulty_level": "beginner",
            "complexity_score": 5.5,
            "cognitive_load": 6.0,
            "key_terms": ["function", "parameter", "return", "default parameter", "type annotation", "named parameter"],
            "synonyms": ["method", "procedure", "subroutine", "function definition"],
            "learning_objectives": [
                "Define functions with proper type annotations",
                "Use parameters and return values effectively",
                "Implement default parameters for flexibility",
                "Apply functions to solve programming problems"
            ],
            "practical_applications": [
                "Creating utility functions for common operations",
                "Building calculator and mathematical functions",
                "Implementing data validation and processing",
                "Creating reusable code components"
            ],
            "real_world_examples": [
                "Mathematical calculator functions",
                "Data validation and sanitization functions",
                "User interface helper functions",
                "API response processing functions"
            ],
            "common_misconceptions": [
                "Functions don't need return type annotations",
                "Default parameters work like Python",
                "Functions can only return one value",
                "Type annotations are optional for function parameters"
            ]
        },
        {
            "name": "jac_collections",
            "display_name": "JAC Collections and Data Structures",
            "description": "Working with lists, dictionaries, sets, and collection comprehensions in JAC",
            "detailed_description": "JAC supports lists, dictionaries, sets, and tuples with strong typing. All collections require explicit type annotations and support comprehensions similar to Python. Collections are fundamental for organizing and managing data.",
            "category": "JAC Programming",
            "subcategory": "Intermediate",
            "domain": "Computer Science",
            "difficulty_level": "intermediate",
            "complexity_score": 6.5,
            "cognitive_load": 7.0,
            "key_terms": ["list", "dictionary", "set", "tuple", "collection comprehension", "append", "extend", "items"],
            "synonyms": ["data structures", "arrays", "maps", "hash tables"],
            "learning_objectives": [
                "Create and manipulate typed collections",
                "Use collection comprehensions for data processing",
                "Implement common collection operations",
                "Choose appropriate collection types for different use cases"
            ],
            "practical_applications": [
                "Managing user data and profiles",
                "Storing and processing large datasets",
                "Implementing lookup tables and caches",
                "Building data pipelines and transformations"
            ],
            "real_world_examples": [
                "Student gradebook with multiple subjects",
                "Inventory management system",
                "Social media post collections",
                "E-commerce product catalogs"
            ],
            "common_misconceptions": [
                "Collections can be created without type annotations",
                "List comprehensions work exactly like Python",
                "All collection types support the same operations",
                "Collections are automatically persisted"
            ]
        },
        {
            "name": "jac_oop",
            "display_name": "JAC Object-Oriented Programming",
            "description": "Implementing classes, objects, methods, and interface/implementation separation",
            "detailed_description": "JAC supports OOP with 'obj' keyword for defining classes, 'has' for attributes, and 'def' for methods. It encourages separation between interface (.jac) and implementation (.impl.jac) files for better code organization.",
            "category": "JAC Programming",
            "subcategory": "Intermediate",
            "domain": "Computer Science",
            "difficulty_level": "intermediate",
            "complexity_score": 7.0,
            "cognitive_load": 7.5,
            "key_terms": ["object", "class", "method", "attribute", "self", "interface", "implementation", "obj"],
            "synonyms": ["OOP", "object-oriented", "class-based programming"],
            "learning_objectives": [
                "Define objects with attributes and methods",
                "Implement interface/implementation separation",
                "Use 'self' reference correctly",
                "Create reusable object-oriented designs"
            ],
            "practical_applications": [
                "Building data models and entities",
                "Creating reusable business logic components",
                "Implementing game objects and entities",
                "Designing application architecture"
            ],
            "real_world_examples": [
                "Student and Course management systems",
                "E-commerce product and order objects",
                "Game characters and inventory systems",
                "Banking account and transaction objects"
            ],
            "common_misconceptions": [
                "JAC objects work exactly like Python classes",
                "Interface separation is optional",
                "All methods need 'self' parameter",
                "Objects are automatically persisted"
            ]
        },
        {
            "name": "jac_object_spatial_programming",
            "display_name": "JAC Object-Spatial Programming (OSP)",
            "description": "Understanding the revolutionary OSP paradigm with nodes, edges, and walkers",
            "detailed_description": "Object-Spatial Programming is JAC's unique paradigm where computation moves to data. Built on three fundamentals: Nodes (stateful entities), Edges (typed relationships), and Walkers (mobile computation that traverses graphs).",
            "category": "JAC Programming",
            "subcategory": "Advanced",
            "domain": "Computer Science",
            "difficulty_level": "advanced",
            "complexity_score": 8.5,
            "cognitive_load": 9.0,
            "key_terms": ["Object-Spatial Programming", "OSP", "node", "edge", "walker", "graph", "traversal", "scale-agnostic"],
            "synonyms": ["graph programming", "spatial computation", "distributed programming"],
            "learning_objectives": [
                "Understand the OSP paradigm fundamentals",
                "Create nodes and edges for data relationships",
                "Implement walkers for graph traversal",
                "Apply scale-agnostic programming principles"
            ],
            "practical_applications": [
                "Building social network applications",
                "Creating knowledge graph systems",
                "Implementing recommendation engines",
                "Developing distributed data processing"
            ],
            "real_world_examples": [
                "Facebook-style social network with friend relationships",
                "Academic paper citation networks",
                "E-commerce product recommendation systems",
                "Transportation route optimization"
            ],
            "common_misconceptions": [
                "OSP is just another name for graph databases",
                "Nodes and edges are the same as classes and relationships",
                "Walkers are like regular functions",
                "OSP only works for social networks"
            ]
        },
        {
            "name": "jac_nodes_edges",
            "display_name": "JAC Nodes and Edges",
            "description": "Creating and managing nodes (data entities) and edges (relationships) in JAC",
            "detailed_description": "Nodes are objects with location in graph structure, created using 'node' keyword. Edges create typed connections between nodes and can have properties. Both support inheritance and complex relationship modeling.",
            "category": "JAC Programming",
            "subcategory": "Advanced",
            "domain": "Computer Science",
            "difficulty_level": "advanced",
            "complexity_score": 8.0,
            "cognitive_load": 8.5,
            "key_terms": ["node", "edge", "relationship", "graph structure", "typed edge", "edge properties", "root"],
            "synonyms": ["vertices", "connections", "links", "associations"],
            "learning_objectives": [
                "Create nodes with appropriate attributes",
                "Define typed edges with properties",
                "Establish complex relationships between entities",
                "Understand graph traversal patterns"
            ],
            "practical_applications": [
                "Modeling complex business relationships",
                "Building knowledge representation systems",
                "Creating network topology models",
                "Implementing hierarchical data structures"
            ],
            "real_world_examples": [
                "Company organizational charts",
                "Academic course prerequisites",
                "Supply chain management systems",
                "Social media follower networks"
            ],
            "common_misconceptions": [
                "Nodes are just regular objects",
                "Edges can only connect two nodes",
                "Graph structure is automatically optimized",
                "All relationships are bidirectional"
            ]
        },
        {
            "name": "jac_walkers",
            "display_name": "JAC Walkers and Graph Traversal",
            "description": "Implementing mobile computation through walkers that traverse graphs of nodes and edges",
            "detailed_description": "Walkers are programs that traverse graphs performing tasks. They have 'can' abilities that execute when landing on specific node types. Walkers use 'visit' statements to traverse edges and 'spawn' to initiate traversal.",
            "category": "JAC Programming",
            "subcategory": "Advanced",
            "domain": "Computer Science",
            "difficulty_level": "advanced",
            "complexity_score": 8.5,
            "cognitive_load": 9.0,
            "key_terms": ["walker", "spawn", "visit", "traverse", "ability", "here", "entry"],
            "synonyms": ["mobile agents", "graph algorithms", "traversal agents"],
            "learning_objectives": [
                "Create walkers with appropriate abilities",
                "Implement graph traversal algorithms",
                "Use 'visit' and 'spawn' effectively",
                "Design efficient walker workflows"
            ],
            "practical_applications": [
                "Implementing search and discovery algorithms",
                "Building recommendation and suggestion systems",
                "Creating data analysis and reporting tools",
                "Developing network monitoring systems"
            ],
            "real_world_examples": [
                "Friend recommendation algorithms",
                "Web crawling and indexing systems",
                "Network diagnostic tools",
                "Social media content discovery"
            ],
            "common_misconceptions": [
                "Walkers are like regular functions",
                "Graph traversal is always linear",
                "Walkers automatically optimize their path",
                "All traversal requires manual edge navigation"
            ]
        },
        {
            "name": "jac_ai_integration",
            "display_name": "JAC AI Integration with byLLM",
            "description": "Integrating Large Language Models into JAC applications using byLLM annotations",
            "detailed_description": "JAC provides native AI integration through byLLM annotations. Functions can be marked with 'byllm()' to have their implementation generated by configured LLMs, enabling dynamic content generation and intelligent responses.",
            "category": "JAC Programming",
            "subcategory": "Expert",
            "domain": "Computer Science",
            "difficulty_level": "expert",
            "complexity_score": 9.0,
            "cognitive_load": 9.5,
            "key_terms": ["byLLM", "AI integration", "LLM", "Model", "artificial intelligence", "dynamic generation"],
            "synonyms": ["machine learning integration", "AI-powered programming", "LLM annotation"],
            "learning_objectives": [
                "Configure LLM models for JAC applications",
                "Implement functions with byLLM annotations",
                "Handle AI-generated content appropriately",
                "Build intelligent user interactions"
            ],
            "practical_applications": [
                "Creating conversational AI applications",
                "Generating dynamic content and responses",
                "Building intelligent tutoring systems",
                "Implementing automated code generation"
            ],
            "real_world_examples": [
                "AI-powered chatbots and virtual assistants",
                "Dynamic educational content generation",
                "Intelligent coding challenge creation",
                "Automated report and documentation generation"
            ],
            "common_misconceptions": [
                "byLLM functions work without configuration",
                "AI integration is only for text generation",
                "LLM responses are always accurate",
                "byLLM replaces traditional programming"
            ]
        },
        {
            "name": "jac_scale_agnostic_programming",
            "display_name": "JAC Scale-Agnostic Programming",
            "description": "Building applications that work seamlessly from single user to millions of users",
            "detailed_description": "JAC enables scale-agnostic programming where code works for single users or millions without changes. This is achieved through automatic persistence, multi-user isolation, and graph-based architecture.",
            "category": "JAC Programming",
            "subcategory": "Expert",
            "domain": "Computer Science",
            "difficulty_level": "expert",
            "complexity_score": 9.0,
            "cognitive_load": 9.0,
            "key_terms": ["scale-agnostic", "automatic persistence", "multi-user", "isolation", "distributed"],
            "synonyms": ["elastic programming", "auto-scaling", "cloud-native"],
            "learning_objectives": [
                "Understand scale-agnostic programming principles",
                "Implement applications that scale automatically",
                "Leverage automatic persistence features",
                "Design for multi-user environments"
            ],
            "practical_applications": [
                "Building cloud-native applications",
                "Creating auto-scaling services",
                "Implementing multi-tenant systems",
                "Developing global-scale applications"
            ],
            "real_world_examples": [
                "SaaS applications with automatic scaling",
                "Multi-tenant e-commerce platforms",
                "Global social media applications",
                "Enterprise collaboration systems"
            ],
            "common_misconceptions": [
                "Scale-agnostic means no performance considerations",
                "Automatic persistence works for all data types",
                "Multi-user isolation is automatic for all operations",
                "Scale-agnostic code works the same at all sizes"
            ]
        }
    ]
    
    # Create concepts
    for concept_data in jac_concepts:
        # Check if concept already exists
        existing_concept = db.query(Concept).filter(Concept.name == concept_data["name"]).first()
        if not existing_concept:
            concept = Concept(
                name=concept_data["name"],
                display_name=concept_data["display_name"],
                description=concept_data["description"],
                detailed_description=concept_data["detailed_description"],
                category=concept_data["category"],
                subcategory=concept_data["subcategory"],
                domain=concept_data["domain"],
                difficulty_level=concept_data["difficulty_level"],
                complexity_score=concept_data["complexity_score"],
                cognitive_load=concept_data["cognitive_load"],
                key_terms=concept_data["key_terms"],
                synonyms=concept_data["synonyms"],
                learning_objectives=concept_data["learning_objectives"],
                practical_applications=concept_data["practical_applications"],
                real_world_examples=concept_data["real_world_examples"],
                common_misconceptions=concept_data["common_misconceptions"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(concept)
            print(f"✅ Created concept: {concept_data['display_name']}")
        else:
            print(f"✅ Concept already exists: {concept_data['display_name']}")
    
    db.commit()

def create_jac_learning_paths(db: Session):
    """Create JAC-specific learning paths"""
    print("🛤️ Creating JAC Learning Paths...")
    
    # Check if JAC learning paths already exist
    existing_paths = db.query(LearningPath).filter(LearningPath.category == "JAC Programming").count()
    if existing_paths > 0:
        print("✅ JAC learning paths already exist")
        return
    
    # JAC Learning Paths based on the guide structure
    learning_paths = [
        {
            "name": "JAC Programming Fundamentals Journey",
            "description": "Master the essential concepts of JAC programming from basic syntax to Object-Spatial Programming",
            "category": "JAC Programming",
            "difficulty_level": "beginner",
            "estimated_duration": 40,
            "target_audience": "Beginner programmers new to JAC",
            "prerequisites": [],
            "learning_outcomes": [
                "Understand JAC's unique dual programming paradigm",
                "Master basic syntax, variables, and data types",
                "Implement control flow and functions effectively",
                "Set up and use JAC development environment"
            ],
            "is_public": True
        },
        {
            "name": "JAC Object-Oriented and Collections Mastery",
            "description": "Advanced JAC programming with OOP, collections, and interface separation",
            "category": "JAC Programming",
            "difficulty_level": "intermediate",
            "estimated_duration": 35,
            "target_audience": "Intermediate programmers with JAC basics",
            "prerequisites": ["JAC Programming Fundamentals Journey"],
            "learning_outcomes": [
                "Implement object-oriented programming in JAC",
                "Work effectively with collections and data structures",
                "Apply interface/implementation separation patterns",
                "Build complex data models and relationships"
            ],
            "is_public": True
        },
        {
            "name": "JAC Object-Spatial Programming Expert",
            "description": "Master the revolutionary OSP paradigm with nodes, edges, and walkers",
            "category": "JAC Programming",
            "difficulty_level": "advanced",
            "estimated_duration": 50,
            "target_audience": "Advanced programmers ready for OSP",
            "prerequisites": ["JAC Object-Oriented and Collections Mastery"],
            "learning_outcomes": [
                "Understand Object-Spatial Programming fundamentals",
                "Create and manage nodes and edges effectively",
                "Implement walkers for graph traversal",
                "Build scale-agnostic distributed applications"
            ],
            "is_public": True
        },
        {
            "name": "JAC AI Integration and Expert Level",
            "description": "Expert-level JAC with AI integration, production deployment, and advanced features",
            "category": "JAC Programming",
            "difficulty_level": "expert",
            "estimated_duration": 45,
            "target_audience": "Expert programmers and system architects",
            "prerequisites": ["JAC Object-Spatial Programming Expert"],
            "learning_outcomes": [
                "Integrate AI capabilities using byLLM",
                "Implement scale-agnostic programming patterns",
                "Deploy JAC applications in production",
                "Master advanced JAC language features"
            ],
            "is_public": True
        }
    ]
    
    # Create learning paths
    created_paths = []
    for path_data in learning_paths:
        path = LearningPath(
            name=path_data["name"],
            description=path_data["description"],
            category=path_data["category"],
            difficulty_level=path_data["difficulty_level"],
            estimated_duration=path_data["estimated_duration"],
            target_audience=path_data["target_audience"],
            prerequisites=path_data["prerequisites"],
            learning_outcomes=path_data["learning_outcomes"],
            is_public=path_data["is_public"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(path)
        created_paths.append((path, path_data))
        print(f"✅ Created learning path: {path_data['name']}")
    
    db.commit()
    db.refresh(created_paths[0][0])  # Refresh the first path
    
    # Link concepts to learning paths based on prerequisites and difficulty
    concepts = db.query(Concept).filter(Concept.category == "JAC Programming").all()
    
    # Path 1: Fundamentals (Beginner concepts)
    fundamentals_path = next((p for p, d in created_paths if d["name"] == "JAC Programming Fundamentals Journey"), None)
    if fundamentals_path:
        fundamental_concepts = [
            "jac_programming_fundamentals",
            "jac_variables_data_types", 
            "jac_control_flow",
            "jac_functions"
        ]
        
        order = 1
        for concept_name in fundamental_concepts:
            concept = next((c for c in concepts if c.name == concept_name), None)
            if concept:
                link = LearningPathConcept(
                    path_id=fundamentals_path.path_id,
                    concept_id=concept.concept_id,
                    sequence_order=order,
                    estimated_duration=10 if order <= 2 else 8,
                    required_mastery_level=0.0,
                    adaptive_difficulty=True
                )
                db.add(link)
                order += 1
    
    # Path 2: Intermediate (Collections and OOP)
    intermediate_path = next((p for p, d in created_paths if d["name"] == "JAC Object-Oriented and Collections Mastery"), None)
    if intermediate_path:
        intermediate_concepts = [
            "jac_collections",
            "jac_oop"
        ]
        
        order = 1
        for concept_name in intermediate_concepts:
            concept = next((c for c in concepts if c.name == concept_name), None)
            if concept:
                link = LearningPathConcept(
                    path_id=intermediate_path.path_id,
                    concept_id=concept.concept_id,
                    sequence_order=order,
                    estimated_duration=18 if order == 1 else 17,
                    required_mastery_level=0.7,
                    adaptive_difficulty=True
                )
                db.add(link)
                order += 1
    
    # Path 3: Advanced (OSP concepts)
    advanced_path = next((p for p, d in created_paths if d["name"] == "JAC Object-Spatial Programming Expert"), None)
    if advanced_path:
        advanced_concepts = [
            "jac_object_spatial_programming",
            "jac_nodes_edges",
            "jac_walkers"
        ]
        
        order = 1
        for concept_name in advanced_concepts:
            concept = next((c for c in concepts if c.name == concept_name), None)
            if concept:
                link = LearningPathConcept(
                    path_id=advanced_path.path_id,
                    concept_id=concept.concept_id,
                    sequence_order=order,
                    estimated_duration=17 if order <= 2 else 16,
                    required_mastery_level=0.8,
                    adaptive_difficulty=True
                )
                db.add(link)
                order += 1
    
    # Path 4: Expert (AI and scale)
    expert_path = next((p for p, d in created_paths if d["name"] == "JAC AI Integration and Expert Level"), None)
    if expert_path:
        expert_concepts = [
            "jac_ai_integration",
            "jac_scale_agnostic_programming"
        ]
        
        order = 1
        for concept_name in expert_concepts:
            concept = next((c for c in concepts if c.name == concept_name), None)
            if concept:
                link = LearningPathConcept(
                    path_id=expert_path.path_id,
                    concept_id=concept.concept_id,
                    sequence_order=order,
                    estimated_duration=23 if order == 1 else 22,
                    required_mastery_level=0.9,
                    adaptive_difficulty=True
                )
                db.add(link)
                order += 1
    
    db.commit()
    print("✅ Linked concepts to learning paths")

def main():
    """Main seeding function for JAC concepts and learning paths"""
    print("🎯 Starting JAC Programming Language Database Seeding...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create JAC concepts
        create_jac_concepts(db)
        
        # Create JAC learning paths
        create_jac_learning_paths(db)
        
        print("\n🎉 JAC Programming Database seeding completed successfully!")
        print("\n📊 Database Summary:")
        print(f"   • JAC Concepts: {db.query(Concept).filter(Concept.category == 'JAC Programming').count()}")
        print(f"   • JAC Learning Paths: {db.query(LearningPath).filter(LearningPath.category == 'JAC Programming').count()}")
        print(f"   • Total Concepts: {db.query(Concept).count()}")
        print(f"   • Total Learning Paths: {db.query(LearningPath).count()}")
        
    except Exception as e:
        print(f"❌ Error during JAC seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()