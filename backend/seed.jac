# ==============================================================================
# Jeseci Smart Learning Academy - Database Seeder for Jac Language Concepts
# ==============================================================================
# This module seeds the database with Jac programming language concepts,
# learning paths, and establishes relationships between them.
# ==============================================================================
# Author: MiniMax Agent
# Created: 2025-12-24
# ==============================================================================

import datetime;

# Database module for PostgreSQL and Neo4j connections
import database as db_module;

# ==============================================================================
# Jac Language Concept Data
# Ported from seed_jac_concepts (1).py
# ==============================================================================

# Global concept data - accessible to all walkers
jac_concepts_data = [
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
        "synonyms": ["Java-like Architecture for Computation", "JAC Language"]
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
        "synonyms": ["data types", "variable declaration", "type system"]
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
        "synonyms": ["conditionals", "loops", "decision making", "iteration"]
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
        "synonyms": ["method", "procedure", "subroutine", "function definition"]
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
        "synonyms": ["data structures", "arrays", "maps", "hash tables"]
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
        "synonyms": ["OOP", "object-oriented", "class-based programming"]
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
        "synonyms": ["graph programming", "spatial computation", "distributed programming"]
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
        "synonyms": ["vertices", "connections", "links", "associations"]
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
        "synonyms": ["mobile agents", "graph algorithms", "traversal agents"]
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
        "synonyms": ["machine learning integration", "AI-powered programming", "LLM annotation"]
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
        "synonyms": ["elastic programming", "auto-scaling", "cloud-native"]
    }
];

# Learning path definitions
jac_learning_paths = [
    {
        "path_id": "jac_fundamentals_journey",
        "name": "JAC Programming Fundamentals Journey",
        "title": "JAC Programming Fundamentals Journey",
        "description": "Master the essential concepts of JAC programming from basic syntax to Object-Spatial Programming",
        "category": "JAC Programming",
        "difficulty_level": "beginner",
        "estimated_duration": 40,
        "target_audience": "Beginner programmers new to JAC",
        "concepts": [
            "jac_programming_fundamentals",
            "jac_variables_data_types",
            "jac_control_flow",
            "jac_functions"
        ]
    },
    {
        "path_id": "jac_oop_collections_mastery",
        "name": "JAC Object-Oriented and Collections Mastery",
        "title": "JAC Object-Oriented and Collections Mastery",
        "description": "Advanced JAC programming with OOP, collections, and interface separation",
        "category": "JAC Programming",
        "difficulty_level": "intermediate",
        "estimated_duration": 35,
        "target_audience": "Intermediate programmers with JAC basics",
        "concepts": [
            "jac_collections",
            "jac_oop"
        ]
    },
    {
        "path_id": "jac_osp_expert",
        "name": "JAC Object-Spatial Programming Expert",
        "title": "JAC Object-Spatial Programming Expert",
        "description": "Master the revolutionary OSP paradigm with nodes, edges, and walkers",
        "category": "JAC Programming",
        "difficulty_level": "advanced",
        "estimated_duration": 50,
        "target_audience": "Advanced programmers ready for OSP",
        "concepts": [
            "jac_object_spatial_programming",
            "jac_nodes_edges",
            "jac_walkers"
        ]
    },
    {
        "path_id": "jac_ai_expert",
        "name": "JAC AI Integration and Expert Level",
        "title": "JAC AI Integration and Expert Level",
        "description": "Expert-level JAC with AI integration, production deployment, and advanced features",
        "category": "JAC Programming",
        "difficulty_level": "expert",
        "estimated_duration": 45,
        "target_audience": "Expert programmers and system architects",
        "concepts": [
            "jac_ai_integration",
            "jac_scale_agnostic_programming"
        ]
    }
];

# Relationship definitions
jac_relationships = [
    # Hierarchy / Prerequisites
    {"from": "jac_programming_fundamentals", "to": "jac_variables_data_types", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_variables_data_types", "to": "jac_control_flow", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_control_flow", "to": "jac_functions", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_functions", "to": "jac_collections", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_collections", "to": "jac_oop", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_oop", "to": "jac_object_spatial_programming", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_object_spatial_programming", "to": "jac_nodes_edges", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_nodes_edges", "to": "jac_walkers", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_walkers", "to": "jac_ai_integration", "type": "PREREQUISITE", "strength": 1},
    {"from": "jac_ai_integration", "to": "jac_scale_agnostic_programming", "type": "PREREQUISITE", "strength": 1},

    # Related concepts (can be learned in parallel)
    {"from": "jac_control_flow", "to": "jac_functions", "type": "RELATED_TO", "strength": 0.5},
    {"from": "jac_variables_data_types", "to": "jac_collections", "type": "RELATED_TO", "strength": 0.5},
    {"from": "jac_oop", "to": "jac_collections", "type": "RELATED_TO", "strength": 0.5},
    {"from": "jac_object_spatial_programming", "to": "jac_walkers", "type": "RELATED_TO", "strength": 0.5},
    {"from": "jac_nodes_edges", "to": "jac_walkers", "type": "RELATED_TO", "strength": 0.5},
    {"from": "jac_ai_integration", "to": "jac_walkers", "type": "RELATED_TO", "strength": 0.5},

    # Builds upon relationships
    {"from": "jac_oop", "to": "jac_object_spatial_programming", "type": "BUILDS_UPON", "strength": 1},
    {"from": "jac_nodes_edges", "to": "jac_ai_integration", "type": "BUILDS_UPON", "strength": 0.8},
    {"from": "jac_scale_agnostic_programming", "to": "jac_object_spatial_programming", "type": "BUILDS_UPON", "strength": 0.8}
];

# ==============================================================================
# Main Seeder Walker
# ==============================================================================

walker seeder {
    # Operation mode: 'concepts', 'paths', 'relationships', 'all'
    has mode: str = "all";
    has dry_run: bool = false;
    has verbose: bool = true;

    # Helper to create Neo4j constraints
    can create_constraints(manager) {
        constraint_queries = [
            "CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE",
            "CREATE CONSTRAINT path_id_unique IF NOT EXISTS FOR (p:LearningPath) REQUIRE p.path_id IS UNIQUE"
        ];
        for cq in constraint_queries {
            try {
                manager.execute_query(cq, None);
            } except Exception as e {
                # Constraints may already exist
                pass;
            }
        }
    }

    # Helper to seed concepts to Neo4j
    can seed_concepts_to_neo4j(manager, dry_run, verbose) -> dict {
        if dry_run {
            return {"success": true, "concepts_created": 0, "message": "Dry run - concepts not seeded"};
        }

        # Clear existing Jac concepts
        try {
            clear_query = "MATCH (c:Concept {category: 'JAC Programming'}) DETACH DELETE c";
            manager.execute_query(clear_query, None);
            if verbose { print("Cleared existing JAC concepts"); }
        } except Exception as e {
            if verbose { print("Clear warning: " + str(e)); }
        }

        concepts_created = 0;
        concepts_skipped = 0;

        for concept_data in jac_concepts_data {
            concept_id = "jac_" + concept_data['name'].replace("jac_", "").replace("_", "_");

            create_query = """
            MERGE (c:Concept {concept_id: \$concept_id})
            SET c.name = \$name,
                c.display_name = \$display_name,
                c.category = \$category,
                c.subcategory = \$subcategory,
                c.domain = \$domain,
                c.difficulty = \$difficulty_level,
                c.complexity_score = \$complexity_score,
                c.cognitive_load = \$cognitive_load,
                c.description = \$description,
                c.detailed_description = \$detailed_description,
                c.key_terms = \$key_terms,
                c.synonyms = \$synonyms,
                c.created_at = datetime()
            """;

            params = {
                "concept_id": concept_id,
                "name": concept_data['name'],
                "display_name": concept_data['display_name'],
                "category": concept_data['category'],
                "subcategory": concept_data['subcategory'],
                "domain": concept_data['domain'],
                "difficulty_level": concept_data['difficulty_level'],
                "complexity_score": concept_data['complexity_score'],
                "cognitive_load": concept_data['cognitive_load'],
                "description": concept_data['description'],
                "detailed_description": concept_data['detailed_description'],
                "key_terms": concept_data['key_terms'],
                "synonyms": concept_data['synonyms']
            };

            try {
                manager.execute_query(create_query, params);
                concepts_created += 1;
                if verbose {
                    print("Created concept: " + concept_data['display_name']);
                }
            } except Exception as e {
                concepts_skipped += 1;
                if verbose {
                    print("Failed to create: " + concept_data['display_name'] + " - " + str(e));
                }
            }
        }

        return {
            "success": true,
            "concepts_created": concepts_created,
            "concepts_skipped": concepts_skipped,
            "message": "Concepts seeded successfully"
        };
    }

    # Helper to seed learning paths to Neo4j
    can seed_paths_to_neo4j(manager, dry_run, verbose) -> dict {
        if dry_run {
            return {"success": true, "paths_created": 0, "relationships_created": 0, "message": "Dry run - paths not seeded"};
        }

        # Clear existing learning paths
        try {
            clear_query = "MATCH (p:LearningPath {category: 'JAC Programming'}) DETACH DELETE p";
            manager.execute_query(clear_query, None);
            if verbose { print("Cleared existing JAC learning paths"); }
        } except Exception as e {
            if verbose { print("Clear warning: " + str(e)); }
        }

        paths_created = 0;
        relationships_created = 0;

        for path_data in jac_learning_paths {
            # Create path node
            create_path_query = """
            MERGE (p:LearningPath {path_id: \$path_id})
            SET p.name = \$name,
                p.title = \$title,
                p.description = \$description,
                p.category = \$category,
                p.difficulty = \$difficulty_level,
                p.estimated_duration = \$estimated_duration,
                p.target_audience = \$target_audience,
                p.concept_count = \$concept_count,
                p.created_at = datetime()
            """;

            path_params = {
                "path_id": path_data['path_id'],
                "name": path_data['name'],
                "title": path_data['title'],
                "description": path_data['description'],
                "category": path_data['category'],
                "difficulty_level": path_data['difficulty_level'],
                "estimated_duration": path_data['estimated_duration'],
                "target_audience": path_data['target_audience'],
                "concept_count": len(path_data['concepts'])
            };

            try {
                manager.execute_query(create_path_query, path_params);
                paths_created += 1;
                if verbose {
                    print("Created learning path: " + path_data['title']);
                }

                # Link concepts to path
                order = 1;
                for concept_name in path_data['concepts'] {
                    concept_id = "jac_" + concept_name.replace("jac_", "").replace("_", "_");

                    link_query = """
                    MATCH (p:LearningPath {path_id: \$path_id})
                    MATCH (c:Concept {name: \$concept_name})
                    MERGE (p)-[r:PathContains {order_index: \$order, is_required: true, created_at: datetime()}]->(c)
                    """;

                    link_params = {
                        "path_id": path_data['path_id'],
                        "concept_name": concept_name,
                        "order": order
                    };

                    try {
                        manager.execute_query(link_query, link_params);
                        relationships_created += 1;
                    } except Exception as e {
                        if verbose {
                            print("Failed to link concept: " + concept_name + " - " + str(e));
                        }
                    }
                    order += 1;
                }
            } except Exception as e {
                if verbose {
                    print("Failed to create path: " + path_data['title'] + " - " + str(e));
                }
            }
        }

        return {
            "success": true,
            "paths_created": paths_created,
            "relationships_created": relationships_created,
            "message": "Learning paths seeded successfully"
        };
    }

    # Helper to seed relationships to Neo4j
    can seed_relationships_to_neo4j(manager, dry_run, verbose) -> dict {
        if dry_run {
            return {"success": true, "relationships_created": 0, "message": "Dry run - relationships not seeded"};
        }

        relationships_created = 0;
        relationships_skipped = 0;

        for rel in jac_relationships {
            # Build dynamic query with correct relationship type
            rel_query = """
            MATCH (a:Concept {name: \$from_name})
            MATCH (b:Concept {name: \$to_name})
            MERGE (a)-[r:REL_TYPE {strength: \$strength, created_at: datetime()}]->(b)
            SET r.type = \$type
            """.replace("REL_TYPE", rel['type']);

            params = {
                "from_name": rel['from'],
                "to_name": rel['to'],
                "type": rel['type'],
                "strength": rel['strength']
            };

            try {
                manager.execute_query(rel_query, params);
                relationships_created += 1;
                if verbose {
                    print("Created relationship: " + rel['from'] + " --[" + rel['type'] + "]--> " + rel['to']);
                }
            } except Exception as e {
                relationships_skipped += 1;
                if verbose {
                    print("Failed: " + rel['from'] + " --[" + rel['type'] + "]--> " + rel['to']);
                }
            }
        }

        return {
            "success": true,
            "relationships_created": relationships_created,
            "relationships_skipped": relationships_skipped,
            "message": "Relationships seeded successfully"
        };
    }

    # Main entry point
    can run with entry {
        print("=" * 70);
        print("Database Seeder for Jac Programming Language Concepts");
        print("=" * 70);
        print("Mode: " + self.mode);
        print("Dry Run: " + str(self.dry_run));
        print("Verbose: " + str(self.verbose));
        print("=" * 70);

        start_time = datetime.datetime.now();

        # Get Neo4j manager
        manager = db_module.get_neo4j_manager();

        # Create constraints
        if self.mode == "all" or self.mode == "concepts" {
            self.create_constraints(manager);
        }

        results = {};

        if self.mode == "all" or self.mode == "concepts" {
            print("\nSeeding Concepts...");
            print("-" * 50);
            results['concepts'] = self.seed_concepts_to_neo4j(manager, self.dry_run, self.verbose);
        }

        if self.mode == "all" or self.mode == "paths" {
            print("\nSeeding Learning Paths...");
            print("-" * 50);
            results['paths'] = self.seed_paths_to_neo4j(manager, self.dry_run, self.verbose);
        }

        if self.mode == "all" or self.mode == "relationships" {
            print("\nSeeding Relationships...");
            print("-" * 50);
            results['relationships'] = self.seed_relationships_to_neo4j(manager, self.dry_run, self.verbose);
        }

        end_time = datetime.datetime.now();
        duration = (end_time - start_time).total_seconds();

        print("\n" + "=" * 70);
        print("Seeding Complete!");
        print("=" * 70);
        print("Duration: " + str(duration) + " seconds");

        # Calculate totals
        total_concepts = 0;
        total_paths = 0;
        total_relationships = 0;

        if 'concepts' in results and results['concepts'] {
            if 'concepts_created' in results['concepts'] {
                total_concepts = results['concepts']['concepts_created'];
            }
        }
        if 'paths' in results and results['paths'] {
            if 'paths_created' in results['paths'] {
                total_paths = results['paths']['paths_created'];
            }
        }
        if 'relationships' in results and results['relationships'] {
            if 'relationships_created' in results['relationships'] {
                total_relationships = results['relationships']['relationships_created'];
            }
        }

        print("Concepts Created: " + str(total_concepts));
        print("Learning Paths Created: " + str(total_paths));
        print("Relationships Created: " + str(total_relationships));
        print("=" * 70);

        report {
            "success": true,
            "mode": self.mode,
            "duration_seconds": duration,
            "summary": {
                "concepts_created": total_concepts,
                "paths_created": total_paths,
                "relationships_created": total_relationships
            },
            "results": results
        };
    }
}

# ==============================================================================
# Utility Walker for Checking Seeder Status
# ==============================================================================

walker seed_status {
    can seed_status with entry {
        manager = db_module.get_neo4j_manager();

        # Count concepts
        concept_query = "MATCH (c:Concept {category: 'JAC Programming'}) RETURN count(c) AS count";
        concept_result = manager.execute_query(concept_query, None);
        jac_concepts_count = concept_result[0]['count'] if concept_result else 0;

        # Count learning paths
        path_query = "MATCH (p:LearningPath {category: 'JAC Programming'}) RETURN count(p) AS count";
        path_result = manager.execute_query(path_query, None);
        jac_paths_count = path_result[0]['count'] if path_result else 0;

        # Count relationships
        rel_query = """
        MATCH (a:Concept)-[r:PREREQUISITE|RELATED_TO|BUILDS_UPON]->(b:Concept)
        WHERE a.category = 'JAC Programming' OR b.category = 'JAC Programming'
        RETURN count(r) AS count
        """;
        rel_result = manager.execute_query(rel_query, None);
        jac_rels_count = rel_result[0]['count'] if rel_result else 0;

        # Get all concepts
        concepts_query = """
        MATCH (c:Concept {category: 'JAC Programming'})
        RETURN c.name AS name, c.display_name AS display_name, c.difficulty AS difficulty
        ORDER BY c.name
        """;
        concepts_result = manager.execute_query(concepts_query, None);
        concepts_list = concepts_result or [];

        report {
            "success": true,
            "status": {
                "jac_concepts": jac_concepts_count,
                "jac_learning_paths": jac_paths_count,
                "jac_relationships": jac_rels_count,
                "is_seeded": jac_concepts_count > 0
            },
            "concepts": concepts_list,
            "message": "JAC seeder status retrieved successfully"
        };
    }
}

# ==============================================================================
# Walker to Reset/Clear All Jac Data
# ==============================================================================

walker seed_reset {
    has verbose: bool = true;

    can seed_reset with entry {
        print("=" * 70);
        print("Resetting Jac Database Seeder Data");
        print("=" * 70);

        manager = db_module.get_neo4j_manager();

        # Clear relationships first
        rel_query = """
        MATCH (a:Concept)-[r:PREREQUISITE|RELATED_TO|BUILDS_UPON|PathContains|NEXT_IN_PATH]->(b:Concept)
        WHERE a.category = 'JAC Programming' OR b.category = 'JAC Programming'
        DELETE r
        """;
        try {
            manager.execute_query(rel_query, None);
            if self.verbose { print("Cleared JAC relationships"); }
        } except Exception as e {
            if self.verbose { print("Relationship clear warning: " + str(e)); }
        }

        # Clear learning paths
        path_query = "MATCH (p:LearningPath {category: 'JAC Programming'}) DETACH DELETE p";
        try {
            manager.execute_query(path_query, None);
            if self.verbose { print("Cleared JAC learning paths"); }
        } except Exception as e {
            if self.verbose { print("Path clear warning: " + str(e)); }
        }

        # Clear concepts
        concept_query = "MATCH (c:Concept {category: 'JAC Programming'}) DETACH DELETE c";
        try {
            manager.execute_query(concept_query, None);
            if self.verbose { print("Cleared JAC concepts"); }
        } except Exception as e {
            if self.verbose { print("Concept clear warning: " + str(e)); }
        }

        print("\nReset complete! All JAC data has been cleared.");

        report {
            "success": true,
            "message": "JAC database reset completed successfully"
        };
    }
}

# ==============================================================================
# Walker to Get Concept Data (for verification)
# ==============================================================================

walker get_concepts {
    can get_concepts with entry {
        report {
            "success": true,
            "concepts": jac_concepts_data,
            "count": len(jac_concepts_data),
            "categories": {
                "beginner": 4,
                "intermediate": 2,
                "advanced": 3,
                "expert": 2
            }
        };
    }
}

# ==============================================================================
# Walker to Get Learning Path Data (for verification)
# ==============================================================================

walker get_paths {
    can get_paths with entry {
        report {
            "success": true,
            "paths": jac_learning_paths,
            "count": len(jac_learning_paths)
        };
    }
}

# ==============================================================================
# Walker to Get Relationship Data (for verification)
# ==============================================================================

walker get_relationships {
    can get_relationships with entry {
        report {
            "success": true,
            "relationships": jac_relationships,
            "count": len(jac_relationships)
        };
    }
}
