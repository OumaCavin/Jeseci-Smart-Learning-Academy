# ==============================================================================
# Jeseci Smart Learning Academy - Database Seeder for Jac Language Concepts
# ==============================================================================
# This module seeds the database with Jac programming language concepts,
# learning paths, and establishes relationships between them.
# ==============================================================================

import datetime;

# Database module for PostgreSQL and Neo4j connections
import database as db_module;

# ==============================================================================
# Helper Functions for Data Access
# ==============================================================================

# Get value from dictionary with key
def get_dict_value(d: dict, key: str, default: any) -> any {
    if key in d { return d[key]; }
    return default;
}

# Get concept by name from concepts list
def get_concept_by_name(concepts: list, name: str) -> dict {
    for c in concepts {
        if c['name'] == name { return c; }
    }
    return {};
}

# Get path by ID from paths list
def get_path_by_id(paths: list, path_id: str) -> dict {
    for p in paths {
        if p['path_id'] == path_id { return p; }
    }
    return {};
}

# ==============================================================================
# Jac Language Concept Data
# ==============================================================================

# Concept 1
jac_concept_1 = {
    "name": "jac_programming_fundamentals",
    "display_name": "JAC Programming Fundamentals",
    "description": "Introduction to JAC programming language",
    "detailed_description": "JAC introduces Object-Spatial Programming",
    "category": "JAC Programming",
    "subcategory": "Introduction",
    "domain": "Computer Science",
    "difficulty_level": "beginner",
    "complexity_score": 6.0,
    "cognitive_load": 6.5,
    "key_terms": ["JAC", "OSP", "nodes", "walkers"],
    "synonyms": ["JAC Language"]
};

# Concept 2
jac_concept_2 = {
    "name": "jac_variables_data_types",
    "display_name": "JAC Variables and Data Types",
    "description": "Understanding JAC type system",
    "detailed_description": "JAC uses strong typing with annotations",
    "category": "JAC Programming",
    "subcategory": "Fundamentals",
    "domain": "Computer Science",
    "difficulty_level": "beginner",
    "complexity_score": 4.0,
    "cognitive_load": 4.5,
    "key_terms": ["variable", "type", "annotation"],
    "synonyms": ["data types"]
};

# Concept 3
jac_concept_3 = {
    "name": "jac_control_flow",
    "display_name": "JAC Control Flow",
    "description": "Mastering conditionals and loops",
    "detailed_description": "JAC provides traditional control flow structures",
    "category": "JAC Programming",
    "subcategory": "Fundamentals",
    "domain": "Computer Science",
    "difficulty_level": "beginner",
    "complexity_score": 5.0,
    "cognitive_load": 5.5,
    "key_terms": ["if", "else", "while", "for"],
    "synonyms": ["conditionals", "loops"]
};

# Concept 4
jac_concept_4 = {
    "name": "jac_functions",
    "display_name": "JAC Functions",
    "description": "Creating reusable code blocks",
    "detailed_description": "JAC functions use def keyword with type annotations",
    "category": "JAC Programming",
    "subcategory": "Fundamentals",
    "domain": "Computer Science",
    "difficulty_level": "beginner",
    "complexity_score": 5.5,
    "cognitive_load": 6.0,
    "key_terms": ["function", "parameter", "return"],
    "synonyms": ["method", "procedure"]
};

# Concept 5
jac_concept_5 = {
    "name": "jac_collections",
    "display_name": "JAC Collections",
    "description": "Working with lists and dictionaries",
    "detailed_description": "JAC supports lists and dicts with strong typing",
    "category": "JAC Programming",
    "subcategory": "Intermediate",
    "domain": "Computer Science",
    "difficulty_level": "intermediate",
    "complexity_score": 6.5,
    "cognitive_load": 7.0,
    "key_terms": ["list", "dict", "collection"],
    "synonyms": ["data structures"]
};

# Concept 6
jac_concept_6 = {
    "name": "jac_oop",
    "display_name": "JAC Object-Oriented Programming",
    "description": "Implementing classes and objects",
    "detailed_description": "JAC supports OOP with obj keyword",
    "category": "JAC Programming",
    "subcategory": "Intermediate",
    "domain": "Computer Science",
    "difficulty_level": "intermediate",
    "complexity_score": 7.0,
    "cognitive_load": 7.5,
    "key_terms": ["object", "class", "method", "obj"],
    "synonyms": ["OOP"]
};

# Concept 7
jac_concept_7 = {
    "name": "jac_object_spatial_programming",
    "display_name": "JAC Object-Spatial Programming",
    "description": "Understanding OSP paradigm",
    "detailed_description": "OSP moves computation to data",
    "category": "JAC Programming",
    "subcategory": "Advanced",
    "domain": "Computer Science",
    "difficulty_level": "advanced",
    "complexity_score": 8.5,
    "cognitive_load": 9.0,
    "key_terms": ["OSP", "node", "edge", "walker"],
    "synonyms": ["graph programming"]
};

# Concept 8
jac_concept_8 = {
    "name": "jac_nodes_edges",
    "display_name": "JAC Nodes and Edges",
    "description": "Creating nodes and edges",
    "detailed_description": "Nodes and edges form graph structures",
    "category": "JAC Programming",
    "subcategory": "Advanced",
    "domain": "Computer Science",
    "difficulty_level": "advanced",
    "complexity_score": 8.0,
    "cognitive_load": 8.5,
    "key_terms": ["node", "edge", "graph"],
    "synonyms": ["vertices", "links"]
};

# Concept 9
jac_concept_9 = {
    "name": "jac_walkers",
    "display_name": "JAC Walkers and Graph Traversal",
    "description": "Implementing walkers for traversal",
    "detailed_description": "Walkers traverse graphs performing tasks",
    "category": "JAC Programming",
    "subcategory": "Advanced",
    "domain": "Computer Science",
    "difficulty_level": "advanced",
    "complexity_score": 8.5,
    "cognitive_load": 9.0,
    "key_terms": ["walker", "spawn", "visit"],
    "synonyms": ["mobile agents"]
};

# Concept 10
jac_concept_10 = {
    "name": "jac_ai_integration",
    "display_name": "JAC AI Integration with byLLM",
    "description": "Integrating LLMs into JAC apps",
    "detailed_description": "JAC provides native AI integration",
    "category": "JAC Programming",
    "subcategory": "Expert",
    "domain": "Computer Science",
    "difficulty_level": "expert",
    "complexity_score": 9.0,
    "cognitive_load": 9.5,
    "key_terms": ["byLLM", "AI", "LLM"],
    "synonyms": ["AI integration"]
};

# Concept 11
jac_concept_11 = {
    "name": "jac_scale_agnostic_programming",
    "display_name": "JAC Scale-Agnostic Programming",
    "description": "Building scalable applications",
    "detailed_description": "JAC enables scale-agnostic programming",
    "category": "JAC Programming",
    "subcategory": "Expert",
    "domain": "Computer Science",
    "difficulty_level": "expert",
    "complexity_score": 9.0,
    "cognitive_load": 9.0,
    "key_terms": ["scale", "distributed", "persistence"],
    "synonyms": ["elastic programming"]
};

# Global concept data list
jac_concepts_data = [
    jac_concept_1, jac_concept_2, jac_concept_3, jac_concept_4,
    jac_concept_5, jac_concept_6, jac_concept_7, jac_concept_8,
    jac_concept_9, jac_concept_10, jac_concept_11
];

# ==============================================================================
# Learning Path Data
# ==============================================================================

# Path 1
jac_path_1 = {
    "path_id": "jac_fundamentals_journey",
    "name": "JAC Programming Fundamentals Journey",
    "title": "JAC Programming Fundamentals Journey",
    "description": "Master essential JAC concepts",
    "category": "JAC Programming",
    "difficulty_level": "beginner",
    "estimated_duration": 40,
    "target_audience": "Beginner programmers",
    "concepts": ["jac_programming_fundamentals", "jac_variables_data_types", "jac_control_flow", "jac_functions"]
};

# Path 2
jac_path_2 = {
    "path_id": "jac_oop_collections_mastery",
    "name": "JAC OOP and Collections Mastery",
    "title": "JAC OOP and Collections Mastery",
    "description": "Advanced JAC with OOP and collections",
    "category": "JAC Programming",
    "difficulty_level": "intermediate",
    "estimated_duration": 35,
    "target_audience": "Intermediate programmers",
    "concepts": ["jac_collections", "jac_oop"]
};

# Path 3
jac_path_3 = {
    "path_id": "jac_osp_expert",
    "name": "JAC OSP Expert",
    "title": "JAC OSP Expert",
    "description": "Master OSP with nodes, edges, walkers",
    "category": "JAC Programming",
    "difficulty_level": "advanced",
    "estimated_duration": 50,
    "target_audience": "Advanced programmers",
    "concepts": ["jac_object_spatial_programming", "jac_nodes_edges", "jac_walkers"]
};

# Path 4
jac_path_4 = {
    "path_id": "jac_ai_expert",
    "name": "JAC AI Integration Expert",
    "title": "JAC AI Integration Expert",
    "description": "Expert JAC with AI integration",
    "category": "JAC Programming",
    "difficulty_level": "expert",
    "estimated_duration": 45,
    "target_audience": "Expert programmers",
    "concepts": ["jac_ai_integration", "jac_scale_agnostic_programming"]
};

# Global learning paths list
jac_learning_paths = [jac_path_1, jac_path_2, jac_path_3, jac_path_4];

# ==============================================================================
# Relationship Data (stored as list of tuples for Jac compatibility)
# ==============================================================================

# Relationships stored as list: [from, to, type, strength]
jac_rel_1 = ["jac_programming_fundamentals", "jac_variables_data_types", "PREREQUISITE", 1];
jac_rel_2 = ["jac_variables_data_types", "jac_control_flow", "PREREQUISITE", 1];
jac_rel_3 = ["jac_control_flow", "jac_functions", "PREREQUISITE", 1];
jac_rel_4 = ["jac_functions", "jac_collections", "PREREQUISITE", 1];
jac_rel_5 = ["jac_collections", "jac_oop", "PREREQUISITE", 1];
jac_rel_6 = ["jac_oop", "jac_object_spatial_programming", "PREREQUISITE", 1];
jac_rel_7 = ["jac_object_spatial_programming", "jac_nodes_edges", "PREREQUISITE", 1];
jac_rel_8 = ["jac_nodes_edges", "jac_walkers", "PREREQUISITE", 1];
jac_rel_9 = ["jac_walkers", "jac_ai_integration", "PREREQUISITE", 1];
jac_rel_10 = ["jac_ai_integration", "jac_scale_agnostic_programming", "PREREQUISITE", 1];

# Related concepts
jac_rel_11 = ["jac_control_flow", "jac_functions", "RELATED_TO", 0.5];
jac_rel_12 = ["jac_variables_data_types", "jac_collections", "RELATED_TO", 0.5];
jac_rel_13 = ["jac_oop", "jac_collections", "RELATED_TO", 0.5];
jac_rel_14 = ["jac_object_spatial_programming", "jac_walkers", "RELATED_TO", 0.5];
jac_rel_15 = ["jac_nodes_edges", "jac_walkers", "RELATED_TO", 0.5];
jac_rel_16 = ["jac_ai_integration", "jac_walkers", "RELATED_TO", 0.5];

# Builds upon relationships
jac_rel_17 = ["jac_oop", "jac_object_spatial_programming", "BUILDS_UPON", 1];
jac_rel_18 = ["jac_nodes_edges", "jac_ai_integration", "BUILDS_UPON", 0.8];
jac_rel_19 = ["jac_scale_agnostic_programming", "jac_object_spatial_programming", "BUILDS_UPON", 0.8];

# Global relationships list
jac_relationships = [
    jac_rel_1, jac_rel_2, jac_rel_3, jac_rel_4, jac_rel_5,
    jac_rel_6, jac_rel_7, jac_rel_8, jac_rel_9, jac_rel_10,
    jac_rel_11, jac_rel_12, jac_rel_13, jac_rel_14, jac_rel_15, jac_rel_16,
    jac_rel_17, jac_rel_18, jac_rel_19
];

# ==============================================================================
# Main Seeder Walker
# ==============================================================================

walker seeder {
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
    can seed_concepts_to_neo4j(manager, dry_run, verbose) {
        if dry_run {
            print("Dry run - concepts not seeded");
            return {"success": true, "concepts_created": 0};
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
            # Get values using helper function
            name = get_dict_value(concept_data, "name", "");
            display_name = get_dict_value(concept_data, "display_name", "");
            category = get_dict_value(concept_data, "category", "");
            subcategory = get_dict_value(concept_data, "subcategory", "");
            domain = get_dict_value(concept_data, "domain", "");
            difficulty_level = get_dict_value(concept_data, "difficulty_level", "");
            complexity_score = get_dict_value(concept_data, "complexity_score", 0);
            cognitive_load = get_dict_value(concept_data, "cognitive_load", 0);
            description = get_dict_value(concept_data, "description", "");
            detailed_description = get_dict_value(concept_data, "detailed_description", "");
            key_terms = get_dict_value(concept_data, "key_terms", []);
            synonyms = get_dict_value(concept_data, "synonyms", []);

            # Generate concept_id
            concept_id = "jac_" + name;

            create_query = """
            MERGE (c:Concept {concept_id: $concept_id})
            SET c.name = $name,
                c.display_name = $display_name,
                c.category = $category,
                c.subcategory = $subcategory,
                c.domain = $domain,
                c.difficulty = $difficulty_level,
                c.complexity_score = $complexity_score,
                c.cognitive_load = $cognitive_load,
                c.description = $description,
                c.detailed_description = $detailed_description,
                c.key_terms = $key_terms,
                c.synonyms = $synonyms,
                c.created_at = datetime()
            """;

            params = {
                "concept_id": concept_id,
                "name": name,
                "display_name": display_name,
                "category": category,
                "subcategory": subcategory,
                "domain": domain,
                "difficulty_level": difficulty_level,
                "complexity_score": complexity_score,
                "cognitive_load": cognitive_load,
                "description": description,
                "detailed_description": detailed_description,
                "key_terms": key_terms,
                "synonyms": synonyms
            };

            try {
                manager.execute_query(create_query, params);
                concepts_created += 1;
                if verbose {
                    print("Created concept: " + display_name);
                }
            } except Exception as e {
                concepts_skipped += 1;
                if verbose {
                    print("Failed to create: " + display_name + " - " + str(e));
                }
            }
        }

        print("Concepts created: " + str(concepts_created));
        return {"success": true, "concepts_created": concepts_created};
    }

    # Helper to seed learning paths to Neo4j
    can seed_paths_to_neo4j(manager, dry_run, verbose) {
        if dry_run {
            print("Dry run - paths not seeded");
            return {"success": true, "paths_created": 0};
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
            path_id = get_dict_value(path_data, "path_id", "");
            name = get_dict_value(path_data, "name", "");
            title = get_dict_value(path_data, "title", "");
            description = get_dict_value(path_data, "description", "");
            category = get_dict_value(path_data, "category", "");
            difficulty_level = get_dict_value(path_data, "difficulty_level", "");
            estimated_duration = get_dict_value(path_data, "estimated_duration", 0);
            target_audience = get_dict_value(path_data, "target_audience", "");
            concepts = get_dict_value(path_data, "concepts", []);

            concept_count = len(concepts);

            create_path_query = """
            MERGE (p:LearningPath {path_id: $path_id})
            SET p.name = $name,
                p.title = $title,
                p.description = $description,
                p.category = $category,
                p.difficulty = $difficulty_level,
                p.estimated_duration = $estimated_duration,
                p.target_audience = $target_audience,
                p.concept_count = $concept_count,
                p.created_at = datetime()
            """;

            path_params = {
                "path_id": path_id,
                "name": name,
                "title": title,
                "description": description,
                "category": category,
                "difficulty_level": difficulty_level,
                "estimated_duration": estimated_duration,
                "target_audience": target_audience,
                "concept_count": concept_count
            };

            try {
                manager.execute_query(create_path_query, path_params);
                paths_created += 1;
                if verbose {
                    print("Created learning path: " + title);
                }

                # Link concepts to path
                order = 1;
                for concept_name in concepts {
                    concept_id = "jac_" + concept_name;

                    link_query = """
                    MATCH (p:LearningPath {path_id: $path_id})
                    MATCH (c:Concept {name: $concept_name})
                    MERGE (p)-[r:PathContains {order_index: $order, is_required: true, created_at: datetime()}]->(c)
                    """;

                    link_params = {
                        "path_id": path_id,
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
                    print("Failed to create path: " + title + " - " + str(e));
                }
            }
        }

        print("Paths created: " + str(paths_created));
        print("Path-concept relationships: " + str(relationships_created));
        return {"success": true, "paths_created": paths_created};
    }

    # Helper to seed relationships to Neo4j
    can seed_relationships_to_neo4j(manager, dry_run, verbose) {
        if dry_run {
            print("Dry run - relationships not seeded");
            return {"success": true, "relationships_created": 0};
        }

        relationships_created = 0;
        relationships_skipped = 0;

        for rel in jac_relationships {
            # rel is [from, to, type, strength]
            from_name = rel[0];
            to_name = rel[1];
            rel_type = rel[2];
            strength = rel[3];

            # Build query based on relationship type
            rel_query = "";
            if rel_type == "PREREQUISITE" {
                rel_query = """
                MATCH (a:Concept {name: $from_name})
                MATCH (b:Concept {name: $to_name})
                MERGE (a)-[r:PREREQUISITE {strength: $strength, created_at: datetime()}]->(b)
                SET r.type = "PREREQUISITE"
                """;
            } elif rel_type == "RELATED_TO" {
                rel_query = """
                MATCH (a:Concept {name: $from_name})
                MATCH (b:Concept {name: $to_name})
                MERGE (a)-[r:RELATED_TO {strength: $strength, created_at: datetime()}]->(b)
                SET r.type = "RELATED_TO"
                """;
            } else {
                rel_query = """
                MATCH (a:Concept {name: $from_name})
                MATCH (b:Concept {name: $to_name})
                MERGE (a)-[r:BUILDS_UPON {strength: $strength, created_at: datetime()}]->(b)
                SET r.type = "BUILDS_UPON"
                """;
            }

            params = {
                "from_name": from_name,
                "to_name": to_name,
                "type": rel_type,
                "strength": strength
            };

            try {
                manager.execute_query(rel_query, params);
                relationships_created += 1;
                if verbose {
                    print("Created: " + from_name + " --[" + rel_type + "]--> " + to_name);
                }
            } except Exception as e {
                relationships_skipped += 1;
                if verbose {
                    print("Failed: " + from_name + " --[" + rel_type + "]--> " + to_name);
                }
            }
        }

        print("Relationships created: " + str(relationships_created));
        return {"success": true, "relationships_created": relationships_created};
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

        if self.mode == "all" or self.mode == "concepts" {
            print("\nSeeding Concepts...");
            print("-" * 50);
            self.seed_concepts_to_neo4j(manager, self.dry_run, self.verbose);
        }

        if self.mode == "all" or self.mode == "paths" {
            print("\nSeeding Learning Paths...");
            print("-" * 50);
            self.seed_paths_to_neo4j(manager, self.dry_run, self.verbose);
        }

        if self.mode == "all" or self.mode == "relationships" {
            print("\nSeeding Relationships...");
            print("-" * 50);
            self.seed_relationships_to_neo4j(manager, self.dry_run, self.verbose);
        }

        end_time = datetime.datetime.now();
        duration = (end_time - start_time).total_seconds();

        print("\n" + "=" * 70);
        print("Seeding Complete!");
        print("=" * 70);
        print("Duration: " + str(duration) + " seconds");
        print("=" * 70);

        report {"success": true};
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
        jac_concepts_count = 0;
        if concept_result and len(concept_result) > 0 {
            jac_concepts_count = concept_result[0]['count'];
        }

        # Count learning paths
        path_query = "MATCH (p:LearningPath {category: 'JAC Programming'}) RETURN count(p) AS count";
        path_result = manager.execute_query(path_query, None);
        jac_paths_count = 0;
        if path_result and len(path_result) > 0 {
            jac_paths_count = path_result[0]['count'];
        }

        # Count relationships
        rel_query = """
        MATCH (a:Concept)-[r:PREREQUISITE|RELATED_TO|BUILDS_UPON]->(b:Concept)
        WHERE a.category = 'JAC Programming' OR b.category = 'JAC Programming'
        RETURN count(r) AS count
        """;
        rel_result = manager.execute_query(rel_query, None);
        jac_rels_count = 0;
        if rel_result and len(rel_result) > 0 {
            jac_rels_count = rel_result[0]['count'];
        }

        report {
            "success": true,
            "jac_concepts": jac_concepts_count,
            "jac_learning_paths": jac_paths_count,
            "jac_relationships": jac_rels_count
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
        MATCH (a:Concept)-[r:PREREQUISITE|RELATED_TO|BUILDS_UPON|PathContains]->(b:Concept)
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
        report {"success": true};
    }
}

# ==============================================================================
# Entry Point - Run seeder when file is executed
# ==============================================================================

# Simple entry point - spawn the seeder walker with defaults
print("Starting Database Seeder...");
spawn seeder(mode="all", dry_run=false, verbose=true)::run;
print("Seeding completed!");
