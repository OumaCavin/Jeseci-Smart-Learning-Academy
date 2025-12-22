# ==============================================================================
# Jeseci Graph Knowledge Engine - Neo4j Graph-Based Learning Features
# ==============================================================================
# This module implements graph-based features using Neo4j for:
# - Learning path relationships and management
# - Concept dependency graphs with prerequisite tracking
# - User progress tracking through graph traversals
# - Intelligent recommendations based on graph algorithms
# - Analytics and learning insights from graph data
# ==============================================================================

import from python { PyModule }
import from datetime { datetime }

glob neo4j_db = PyModule("backend.database");

# ==============================================================================
# GRAPH NODES - Data Models for Neo4j
# ==============================================================================

## User node representing a learner in the knowledge graph
node GraphUser {
    has user_id: str;
    has username: str;
    has display_name: str;
    has email: str;
    has skill_level: str = "beginner";
    has learning_style: str = "visual";
    has created_at: int = 0;
    has last_active: int = 0;
}

## Concept node representing a learning topic in the knowledge graph
node GraphConcept {
    has concept_id: str;
    has name: str;
    has display_name: str;
    has category: str;
    has difficulty: str = "beginner";
    has difficulty_score: int = 1;
    has description: str = "";
    has estimated_duration: int = 30;
    has prerequisites_count: int = 0;
    has related_count: int = 0;
    has created_at: int = 0;
    has updated_at: int = 0;
}

## Learning path node representing a structured curriculum
node GraphLearningPath {
    has path_id: str;
    has name: str;
    has title: str;
    has description: str = "";
    has difficulty: str = "beginner";
    has difficulty_score: int = 1;
    has estimated_duration: int = 60;
    has concept_count: int = 0;
    has total_prerequisites: int = 0;
    has created_at: int = 0;
    has updated_at: int = 0;
}

## Achievement node for gamification
node GraphAchievement {
    has achievement_id: str;
    has name: str;
    has description: str = "";
    has icon: str = "";
    has category: str = "general";
    has criteria_type: str = "concepts_completed";
    has criteria_value: int = 1;
    has points: int = 10;
    has rarity: str = "common";
}

## Learning session node for tracking study sessions
node GraphSession {
    has session_id: str;
    has concept_id: str;
    has path_id: str = "";
    has duration_minutes: int = 0;
    has progress_percent: int = 0;
    has score: float = 0.0;
    has status: str = "in_progress";
    has started_at: int = 0;
    has completed_at: int = 0;
}

# ==============================================================================
# GRAPH RELATIONSHIPS - Edges for the Knowledge Graph
# ==============================================================================

## Concept dependency relationships
edge Prerequisite {
    has strength: int = 1;
    has description: str = "";
    has created_at: int = 0;
}

## Related concepts (lateral connections)
edge RelatedTo {
    has weight: float = 1.0;
    has relevance: str = "medium";
    has created_at: int = 0;
}

## Hierarchical relationships
edge PartOf {
    has order_index: int = 0;
    has created_at: int = 0;
}

## Building block relationships
edge BuildsUpon {
    has strength: int = 1;
    has difficulty_jump: int = 1;
    has created_at: int = 0;
}

## Learning path containment
edge PathContains {
    has order_index: int = 0;
    has is_required: bool = true;
    has created_at: int = 0;
}

## User enrollment in learning path
edge EnrolledIn {
    has enrolled_at: int = 0;
    has status: str = "active";
    has progress_percent: int = 0;
    has started_at: int = 0;
    has last_accessed: int = 0;
}

## User completion of concept
edge Completed {
    has completed_at: int = 0;
    has score: float = 0.0;
    has time_spent: int = 0;
    has attempts: int = 1;
}

## User progress on concept (in progress)
edge ProgressOn {
    has progress_percent: int = 0;
    has time_spent: int = 0;
    has started_at: int = 0;
    has last_accessed: int = 0;
}

## User achievement earned
edge Earned {
    has earned_at: int = 0;
    has points: int = 0;
}

# ==============================================================================
# GRAPH MANAGER WALKER - Core Graph Operations
# ==============================================================================

walker GraphManager {
    ## Initialize the graph database connection
    can init_graph with entry {
        print("Initializing Graph Knowledge Engine...");
        
        result = neo4j_db.test_all_connections();
        
        print("Neo4j: " + ("Connected" if result['neo4j'] else "Disconnected"));
        print("PostgreSQL: " + ("Connected" if result['postgresql'] else "Disconnected"));
        
        report {
            "graph_engine": "initialized",
            "neo4j": result['neo4j'],
            "postgresql": result['postgresql'],
            "timestamp": datetime.now().isoformat()
        };
    }
    
    ## Test graph database connection
    can test_connection with entry {
        result = neo4j_db.test_all_connections();
        
        report {
            "connected": result['neo4j'],
            "database": "neo4j",
            "status": "healthy" if result['neo4j'] else "unavailable"
        };
    }
    
    ## Get graph statistics
    can get_graph_stats with entry {
        manager = neo4j_db.get_neo4j_manager();
        
        concept_count = manager.execute_query("MATCH (c:Concept) RETURN count(c) AS count", None);
        user_count = manager.execute_query("MATCH (u:User) RETURN count(u) AS count", None);
        path_count = manager.execute_query("MATCH (p:LearningPath) RETURN count(p) AS count", None);
        relationship_count = manager.execute_query("MATCH ()-[r]->() RETURN count(r) AS count", None);
        
        stats = {
            "concepts": concept_count[0]['count'] if concept_count else 0,
            "users": user_count[0]['count'] if user_count else 0,
            "learning_paths": path_count[0]['count'] if path_count else 0,
            "relationships": relationship_count[0]['count'] if relationship_count else 0
        };
        
        report {
            "success": true,
            "graph_stats": stats
        };
    }
    
    ## Create a constraint in Neo4j
    can create_constraint with entry {
        constraint_type = "concept_id";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.concept_id IS UNIQUE";
        result = manager.execute_query(query, None);
        
        report {
            "success": true,
            "constraint": constraint_type,
            "message": "Constraint created successfully"
        };
    }
}

# ==============================================================================
# CONCEPT MANAGER WALKER - Concept Graph Operations
# ==============================================================================

walker ConceptManager {
    ## Create a new concept in the graph
    can create_concept with entry {
        concept_id = "concept_" + str(datetime.now().timestamp()).replace(".", "_");
        name = "New Concept";
        display_name = "New Concept";
        category = "General";
        difficulty = "beginner";
        description = "";
        estimated_duration = 30;
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        CREATE (c:Concept {
            concept_id: $concept_id,
            name: $name,
            display_name: $display_name,
            category: $category,
            difficulty: $difficulty,
            difficulty_score: 1,
            description: $description,
            estimated_duration: $estimated_duration,
            prerequisites_count: 0,
            related_count: 0,
            created_at: timestamp(),
            updated_at: timestamp()
        })
        RETURN c
        """;
        
        result = manager.execute_query(query, {
            "concept_id": concept_id,
            "name": name,
            "display_name": display_name,
            "category": category,
            "difficulty": difficulty,
            "description": description,
            "estimated_duration": estimated_duration
        });
        
        report {
            "success": result != None,
            "concept_id": concept_id,
            "name": name,
            "operation": "create_concept"
        };
    }
    
    ## Get all concepts from the graph
    can get_all_concepts with entry {
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (c:Concept)
        RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
               c.category AS category, c.difficulty AS difficulty,
               c.description AS description, c.estimated_duration AS duration,
               c.prerequisites_count AS prereq_count, c.related_count AS related_count
        ORDER BY c.name
        """;
        
        result = manager.execute_query(query, None);
        
        report {
            "success": result != None,
            "concepts": result or [],
            "count": len(result) if result else 0
        };
    }
    
    ## Get concept by ID with relationships
    can get_concept with entry {
        concept_id = "concept_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (c:Concept {concept_id: $concept_id})
        OPTIONAL MATCH (c)-[r:PREREQUISITE]->(prereq:Concept)
        OPTIONAL MATCH (c)-[:RELATED_TO]->(related:Concept)
        RETURN c,
               collect(DISTINCT {id: prereq.concept_id, name: prereq.name}) AS prerequisites,
               collect(DISTINCT {id: related.concept_id, name: related.name}) AS related
        """;
        
        result = manager.execute_query(query, {"concept_id": concept_id});
        
        report {
            "success": result != None,
            "concept": result[0] if result else None,
            "concept_id": concept_id
        };
    }
    
    ## Add prerequisite relationship between concepts
    can add_prerequisite with entry {
        source_id = "concept_source";
        target_id = "concept_target";
        strength = 1;
        description = "";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (a:Concept {concept_id: $source_id})
        MATCH (b:Concept {concept_id: $target_id})
        MERGE (a)-[r:PREREQUISITE {strength: $strength, description: $description, created_at: timestamp()}]->(b)
        RETURN a.name, b.name
        """;
        
        result = manager.execute_query(query, {
            "source_id": source_id,
            "target_id": target_id,
            "strength": strength,
            "description": description
        });
        
        report {
            "success": result != None,
            "source": source_id,
            "target": target_id,
            "relationship": "PREREQUISITE"
        };
    }
    
    ## Add related concept relationship
    can add_related with entry {
        concept_id1 = "concept_1";
        concept_id2 = "concept_2";
        weight = 1.0;
        relevance = "medium";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (a:Concept {concept_id: $id1})
        MATCH (b:Concept {concept_id: $id2})
        MERGE (a)-[r:RELATED_TO {weight: $weight, relevance: $relevance, created_at: timestamp()}]->(b)
        RETURN a.name, b.name
        """;
        
        result = manager.execute_query(query, {
            "id1": concept_id1,
            "id2": concept_id2,
            "weight": weight,
            "relevance": relevance
        });
        
        report {
            "success": result != None,
            "concept1": concept_id1,
            "concept2": concept_id2,
            "relationship": "RELATED_TO"
        };
    }
    
    ## Get concept dependency tree
    can get_dependency_tree with entry {
        concept_id = "concept_root";
        depth = 3;
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH path = (c:Concept {concept_id: $concept_id})-[*1..""" + str(depth) + """]-(related:Concept)
        RETURN c, collect(DISTINCT related) AS dependencies, length(path) AS depth
        """;
        
        result = manager.execute_query(query, {"concept_id": concept_id});
        
        report {
            "success": result != None,
            "root_concept": concept_id,
            "depth": depth,
            "dependencies": result or []
        };
    }
}

# ==============================================================================
# LEARNING PATH MANAGER WALKER - Path Graph Operations
# ==============================================================================

walker PathManager {
    ## Create a learning path
    can create_path with entry {
        path_id = "path_" + str(datetime.now().timestamp()).replace(".", "_");
        name = "new_path";
        title = "New Learning Path";
        description = "";
        difficulty = "beginner";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        CREATE (p:LearningPath {
            path_id: $path_id,
            name: $name,
            title: $title,
            description: $description,
            difficulty: $difficulty,
            difficulty_score: 1,
            estimated_duration: 60,
            concept_count: 0,
            total_prerequisites: 0,
            created_at: timestamp(),
            updated_at: timestamp()
        })
        RETURN p
        """;
        
        result = manager.execute_query(query, {
            "path_id": path_id,
            "name": name,
            "title": title,
            "description": description,
            "difficulty": difficulty
        });
        
        report {
            "success": result != None,
            "path_id": path_id,
            "name": name,
            "title": title
        };
    }
    
    ## Add concept to learning path
    can add_concept_to_path with entry {
        path_id = "path_test";
        concept_id = "concept_test";
        order_index = 0;
        is_required = true;
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (p:LearningPath {path_id: $path_id})
        MATCH (c:Concept {concept_id: $concept_id})
        MERGE (p)-[r:PathContains {order_index: $order_index, is_required: $is_required, created_at: timestamp()}]->(c)
        RETURN p.title, c.name, r.order_index
        """;
        
        result = manager.execute_query(query, {
            "path_id": path_id,
            "concept_id": concept_id,
            "order_index": order_index,
            "is_required": is_required
        });
        
        report {
            "success": result != None,
            "path_id": path_id,
            "concept_id": concept_id,
            "order_index": order_index
        };
    }
    
    ## Get learning path with concepts
    can get_path with entry {
        path_id = "path_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (p:LearningPath {path_id: $path_id})
        OPTIONAL MATCH (p)-[r:PathContains]->(c:Concept)
        WITH p, collect({
            concept_id: c.concept_id,
            name: c.name,
            display_name: c.display_name,
            category: c.category,
            difficulty: c.difficulty,
            order_index: r.order_index,
            is_required: r.is_required
        }) AS concepts
        RETURN p.path_id AS id, p.name AS name, p.title AS title, p.description AS description,
               p.difficulty AS difficulty, p.estimated_duration AS duration,
               p.concept_count AS concept_count, concepts
        """;
        
        result = manager.execute_query(query, {"path_id": path_id});
        
        report {
            "success": result != None,
            "path": result[0] if result else None
        };
    }
    
    ## Get all learning paths
    can get_all_paths with entry {
        manager = neo4j_db.get_neo4j_manager();
        
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
            "success": result != None,
            "paths": result or [],
            "count": len(result) if result else 0
        };
    }
    
    ## Get path structure as tree
    can get_path_structure with entry {
        path_id = "path_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH path = (p:LearningPath {path_id: $path_id})-[:PathContains*1..10]->(c:Concept)
        WITH p, c, relationships(path) AS rels
        WITH p, collect({
            concept_id: c.concept_id,
            name: c.name,
            display_name: c.display_name,
            category: c.category,
            difficulty: c.difficulty,
            estimated_duration: c.estimated_duration,
            order_index: rels[0].order_index
        }) AS concept_list
        UNWIND concept_list AS c
        WITH p, c
        ORDER BY c.order_index
        RETURN p.path_id AS id, p.title AS title, collect(c) AS concepts
        """;
        
        result = manager.execute_query(query, {"path_id": path_id});
        
        report {
            "success": result != None,
            "path_structure": result[0] if result else None
        };
    }
}

# ==============================================================================
# USER PROGRESS TRACKER WALKER - Graph-Based Progress Tracking
# ==============================================================================

walker ProgressTracker {
    ## Create or update user in graph
    can upsert_user with entry {
        user_id = "user_test";
        username = "testuser";
        display_name = "Test User";
        email = "test@example.com";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MERGE (u:User {user_id: $user_id})
        SET u.username = $username,
            u.display_name = $display_name,
            u.email = $email,
            u.last_active = timestamp()
        RETURN u
        """;
        
        result = manager.execute_query(query, {
            "user_id": user_id,
            "username": username,
            "display_name": display_name,
            "email": email
        });
        
        report {
            "success": result != None,
            "user_id": user_id,
            "username": username
        };
    }
    
    ## Enroll user in learning path
    can enroll_in_path with entry {
        user_id = "user_test";
        path_id = "path_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (p:LearningPath {path_id: $path_id})
        MERGE (u)-[r:EnrolledIn {
            enrolled_at: timestamp(),
            status: 'active',
            progress_percent: 0,
            started_at: timestamp(),
            last_accessed: timestamp()
        }]->(p)
        RETURN u.username, p.title
        """;
        
        result = manager.execute_query(query, {
            "user_id": user_id,
            "path_id": path_id
        });
        
        report {
            "success": result != None,
            "user_id": user_id,
            "path_id": path_id,
            "status": "enrolled"
        };
    }
    
    ## Mark concept as completed
    can complete_concept with entry {
        user_id = "user_test";
        concept_id = "concept_test";
        score = 85.0;
        time_spent = 30;
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (c:Concept {concept_id: $concept_id})
        MERGE (u)-[r:Completed {
            completed_at: timestamp(),
            score: $score,
            time_spent: $time_spent,
            attempts: 1
        }]->(c)
        RETURN u.username, c.name, r.score
        """;
        
        result = manager.execute_query(query, {
            "user_id": user_id,
            "concept_id": concept_id,
            "score": score,
            "time_spent": time_spent
        });
        
        report {
            "success": result != None,
            "user_id": user_id,
            "concept_id": concept_id,
            "score": score,
            "status": "completed"
        };
    }
    
    ## Update progress on concept
    can update_progress with entry {
        user_id = "user_test";
        concept_id = "concept_test";
        progress = 50;
        time_spent = 15;
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (c:Concept {concept_id: $concept_id})
        MERGE (u)-[r:ProgressOn {
            progress_percent: $progress,
            time_spent: $time_spent,
            started_at: coalesce(r.started_at, timestamp()),
            last_accessed: timestamp()
        }]->(c)
        RETURN u.username, c.name, r.progress_percent
        """;
        
        result = manager.execute_query(query, {
            "user_id": user_id,
            "concept_id": concept_id,
            "progress": progress,
            "time_spent": time_spent
        });
        
        report {
            "success": result != None,
            "user_id": user_id,
            "concept_id": concept_id,
            "progress_percent": progress
        };
    }
    
    ## Get user progress in a path
    can get_path_progress with entry {
        user_id = "user_test";
        path_id = "path_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (p:LearningPath {path_id: $path_id})
        OPTIONAL MATCH (p)-[:PathContains]->(c:Concept)
        OPTIONAL MATCH (u)-[:Completed]->(c)
        WITH p, c, collect(DISTINCT c) AS all_concepts, collect(DISTINCT {concept: c, completed: true}) AS completed_concepts
        WITH p, all_concepts, [x IN completed_concepts WHERE x.completed IS NOT NULL] AS completed
        RETURN p.title AS path_title,
               size(all_concepts) AS total_concepts,
               size(completed) AS completed_concepts,
               CASE WHEN size(all_concepts) > 0 THEN tointeger(size(completed) * 100.0 / size(all_concepts)) ELSE 0 END AS progress_percent
        """;
        
        result = manager.execute_query(query, {
            "user_id": user_id,
            "path_id": path_id
        });
        
        report {
            "success": result != None,
            "user_id": user_id,
            "path_id": path_id,
            "progress": result[0] if result else None
        };
    }
    
    ## Get user completed concepts
    can get_completed_concepts with entry {
        user_id = "user_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (u:User {user_id: $user_id})-[r:Completed]->(c:Concept)
        RETURN c.concept_id AS id, c.name AS name, c.category AS category,
               c.difficulty AS difficulty, r.score AS score, r.completed_at AS completed_at
        ORDER BY r.completed_at DESC
        """;
        
        result = manager.execute_query(query, {"user_id": user_id});
        
        report {
            "success": result != None,
            "user_id": user_id,
            "completed_concepts": result or [],
            "count": len(result) if result else 0
        };
    }
}

# ==============================================================================
# KNOWLEDGE RECOMMENDER WALKER - Intelligent Recommendations
# ==============================================================================

walker KnowledgeRecommender {
    ## Get personalized recommendations based on completed concepts
    can get_recommendations with entry {
        user_id = "user_test";
        path_id = "";
        limit = 5;
        
        manager = neo4j_db.get_neo4j_manager();
        
        if path_id {
            query = """
            MATCH (u:User {user_id: $user_id})
            MATCH (p:LearningPath {path_id: $path_id})
            MATCH (p)-[:PathContains]->(c:Concept)
            WHERE NOT (u)-[:Completed]->(c)
            OPTIONAL MATCH (c)-[:PREREQUISITE]->(prereq:Concept)
            WITH u, c, collect(DISTINCT prereq.concept_id) AS prereqs
            WHERE all(prereq IN prereqs WHERE (u)-[:Completed]->(:Concept {concept_id: prereq}))
            RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
                   c.category AS category, c.difficulty AS difficulty,
                   c.estimated_duration AS duration, size(prereqs) AS prereq_count
            LIMIT $limit
            """;
        } else {
            query = """
            MATCH (u:User {user_id: $user_id})
            MATCH (c:Concept)
            WHERE NOT (u)-[:Completed]->(c)
            OPTIONAL MATCH (c)-[:PREREQUISITE]->(prereq:Concept)
            WITH u, c, collect(DISTINCT prereq.concept_id) AS prereqs
            WHERE all(prereq IN prereqs WHERE (u)-[:Completed]->(:Concept {concept_id: prereq}))
            RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
                   c.category AS category, c.difficulty AS difficulty,
                   c.estimated_duration AS duration, size(prereqs) AS prereq_count
            LIMIT $limit
            """;
        }
        
        result = manager.execute_query(query, {
            "user_id": user_id,
            "path_id": path_id,
            "limit": limit
        });
        
        report {
            "success": result != None,
            "user_id": user_id,
            "recommendations": result or [],
            "count": len(result) if result else 0
        };
    }
    
    ## Get next concept in learning path
    can get_next_concept with entry {
        user_id = "user_test";
        path_id = "path_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (u:User {user_id: $user_id})
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
               c.category AS category, c.difficulty AS difficulty, r.order_index AS position
        """;
        
        result = manager.execute_query(query, {
            "user_id": user_id,
            "path_id": path_id
        });
        
        report {
            "success": result != None,
            "user_id": user_id,
            "path_id": path_id,
            "next_concept": result[0] if result else None
        };
    }
    
    ## Get concepts user is ready to learn (prerequisites met)
    can get_unlocked_concepts with entry {
        user_id = "user_test";
        limit = 10;
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (c:Concept)
        WHERE NOT (u)-[:Completed]->(c)
        OPTIONAL MATCH (c)-[:PREREQUISITE]->(prereq:Concept)
        WITH c, collect(DISTINCT prereq.concept_id) AS prereqs
        WHERE all(prereq IN prereqs WHERE (u)-[:Completed]->(:Concept {concept_id: prereq}))
        RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
               c.category AS category, c.difficulty AS difficulty, size(prereqs) AS prereq_count
        LIMIT $limit
        """;
        
        result = manager.execute_query(query, {
            "user_id": user_id,
            "limit": limit
        });
        
        report {
            "success": result != None,
            "user_id": user_id,
            "unlocked_concepts": result or [],
            "count": len(result) if result else 0
        };
    }
    
    ## Get concepts user cannot yet access (prerequisites not met)
    can get_locked_concepts with entry {
        user_id = "user_test";
        limit = 10;
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (c:Concept)
        WHERE NOT (u)-[:Completed]->(c)
        OPTIONAL MATCH (c)-[:PREREQUISITE]->(prereq:Concept)
        WITH c, collect(DISTINCT prereq.concept_id) AS prereqs
        WHERE NOT all(prereq IN prereqs WHERE (u)-[:Completed]->(:Concept {concept_id: prereq}))
        RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
               c.category AS category, c.difficulty AS difficulty, size(prereqs) AS prereq_count
        LIMIT $limit
        """;
        
        result = manager.execute_query(query, {
            "user_id": user_id,
            "limit": limit
        });
        
        report {
            "success": result != None,
            "user_id": user_id,
            "locked_concepts": result or [],
            "count": len(result) if result else 0
        };
    }
    
    ## Get similar concepts based on graph relationships
    can get_similar_concepts with entry {
        concept_id = "concept_test";
        limit = 5;
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (c:Concept {concept_id: $concept_id})
        OPTIONAL MATCH (c)-[:RELATED_TO]->(related:Concept)
        OPTIONAL MATCH (c)-[:PREREQUISITE]->(next:Concept)
        OPTIONAL MATCH (c)<-[:PREREQUISITE]-(prev:Concept)
        WITH c,
             collect(DISTINCT {id: related.concept_id, name: related.name, type: 'related', weight: related.weight}) +
             collect(DISTINCT {id: next.concept_id, name: next.name, type: 'builds_to', weight: 1.0}) +
             collect(DISTINCT {id: prev.concept_id, name: prev.name, type: 'builds_from', weight: 1.0}) AS connections
        UNWIND connections AS conn
        RETURN conn.id AS id, conn.name AS name, conn.type AS connection_type, conn.weight AS weight
        LIMIT $limit
        """;
        
        result = manager.execute_query(query, {
            "concept_id": concept_id,
            "limit": limit
        });
        
        report {
            "success": result != None,
            "concept_id": concept_id,
            "similar_concepts": result or [],
            "count": len(result) if result else 0
        };
    }
}

# ==============================================================================
# LEARNING ANALYTICS WALKER - Graph-Based Analytics
# ==============================================================================

walker LearningAnalytics {
    ## Get user learning analytics
    can get_user_analytics with entry {
        user_id = "user_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        concepts_query = """
        MATCH (u:User {user_id: $user_id})-[r:Completed]->(c:Concept)
        RETURN count(c) AS total_completed, avg(r.score) AS avg_score, sum(r.time_spent) AS total_time
        """;
        
        paths_query = """
        MATCH (u:User {user_id: $user_id})-[r:EnrolledIn]->(p:LearningPath)
        RETURN count(p) AS total_paths, avg(r.progress_percent) AS avg_progress
        """;
        
        concepts_result = manager.execute_query(concepts_query, {"user_id": user_id});
        paths_result = manager.execute_query(paths_query, {"user_id": user_id});
        
        analytics = {
            "total_completed": concepts_result[0]['total_completed'] if concepts_result else 0,
            "average_score": concepts_result[0]['avg_score'] if concepts_result else 0,
            "total_time_minutes": concepts_result[0]['total_time'] if concepts_result else 0,
            "total_paths": paths_result[0]['total_paths'] if paths_result else 0,
            "average_progress": paths_result[0]['avg_progress'] if paths_result else 0
        };
        
        report {
            "success": true,
            "user_id": user_id,
            "analytics": analytics
        };
    }
    
    ## Get path completion analytics
    can get_path_analytics with entry {
        path_id = "path_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (p:LearningPath {path_id: $path_id})
        OPTIONAL MATCH (u:User)-[r:EnrolledIn]->(p)
        OPTIONAL MATCH (u)-[:Completed]->(p)-[:PathContains]->(c:Concept)
        WITH p, count(DISTINCT u) AS enrolled_users, count(DISTINCT c) AS total_concepts
        OPTIONAL MATCH (u)-[:Completed]->(c)
        WITH p, enrolled_users, total_concepts, count(DISTINCT {user: u, concept: c}) AS completions
        RETURN p.title AS path_title, enrolled_users, total_concepts,
               CASE WHEN total_concepts > 0 THEN tointeger(completions * 100.0 / enrolled_users / total_concepts) ELSE 0 END AS completion_rate
        """;
        
        result = manager.execute_query(query, {"path_id": path_id});
        
        report {
            "success": result != None,
            "path_id": path_id,
            "analytics": result[0] if result else None
        };
    }
    
    ## Get concept difficulty analysis
    can get_concept_difficulty with entry {
        concept_id = "concept_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (c:Concept {concept_id: $concept_id})
        OPTIONAL MATCH (u:User)-[r:Completed]->(c)
        RETURN c.name AS name, c.difficulty AS difficulty,
               count(r) AS attempts, avg(r.score) AS avg_score, avg(r.time_spent) AS avg_time
        """;
        
        result = manager.execute_query(query, {"concept_id": concept_id});
        
        report {
            "success": result != None,
            "concept_id": concept_id,
            "difficulty_analysis": result[0] if result else None
        };
    }
    
    ## Get popular concepts
    def get_popular_concepts(limit: int = 10) -> dict {
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (c:Concept)
        OPTIONAL MATCH (u:User)-[r:Completed]->(c)
        RETURN c.concept_id AS id, c.name AS name, c.display_name AS display_name,
               c.category AS category, c.difficulty AS difficulty,
               count(r) AS completion_count, avg(r.score) AS avg_score
        ORDER BY completion_count DESC
        LIMIT $limit
        """;
        
        result = manager.execute_query(query, {"limit": limit});
        
        return {
            "success": result != None,
            "popular_concepts": result or [],
            "count": len(result) if result else 0
        };
    }
    
    ## Get learning journey visualization data
    can get_learning_journey with entry {
        user_id = "user_test";
        
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (u:User {user_id: $user_id})-[r:Completed]->(c:Concept)
        WITH c, r
        ORDER BY r.completed_at
        RETURN c.concept_id AS id, c.name AS name, c.category AS category,
               c.difficulty AS difficulty, r.score AS score, r.completed_at AS completed_at
        """;
        
        result = manager.execute_query(query, {"user_id": user_id});
        
        report {
            "success": result != None,
            "user_id": user_id,
            "journey": result or [],
            "count": len(result) if result else 0
        };
    }
}

# ==============================================================================
# GRAPH SEEDER WALKER - Initialize Graph with Sample Data
# ==============================================================================

walker GraphSeeder {
    ## Seed the graph with sample learning data
    can seed_graph with entry {
        print("Seeding graph with sample learning data...");
        
        manager = neo4j_db.get_neo4j_manager();
        
        ## Create sample concepts
        concepts = [
            {"id": "prog_basics", "name": "programming_basics", "display_name": "Programming Basics", "category": "Programming", "difficulty": "beginner", "duration": 30},
            {"id": "variables", "name": "variables_data_types", "display_name": "Variables and Data Types", "category": "Programming", "difficulty": "beginner", "duration": 45},
            {"id": "control_flow", "name": "control_flow", "display_name": "Control Flow", "category": "Programming", "difficulty": "beginner", "duration": 45},
            {"id": "functions", "name": "functions", "display_name": "Functions", "category": "Programming", "difficulty": "intermediate", "duration": 60},
            {"id": "data_structures", "name": "data_structures", "display_name": "Data Structures", "category": "Programming", "difficulty": "intermediate", "duration": 90},
            {"id": "oop", "name": "oop", "display_name": "Object-Oriented Programming", "category": "Programming", "difficulty": "intermediate", "duration": 90},
            {"id": "algorithms", "name": "algorithms", "display_name": "Algorithms", "category": "Computer Science", "difficulty": "advanced", "duration": 120},
            {"id": "web_basics", "name": "web_basics", "display_name": "Web Development Basics", "category": "Web Dev", "difficulty": "beginner", "duration": 60},
            {"id": "databases", "name": "databases", "display_name": "Databases", "category": "Data Management", "difficulty": "intermediate", "duration": 90},
            {"id": "graph_concepts", "name": "graph_concepts", "display_name": "Graph Concepts", "category": "Computer Science", "difficulty": "advanced", "duration": 90}
        ];
        
        for concept in concepts {
            create_query = """
            MERGE (c:Concept {concept_id: $id})
            SET c.name = $name, c.display_name = $display_name, c.category = $category,
                c.difficulty = $difficulty, c.difficulty_score = CASE $difficulty
                    WHEN 'beginner' THEN 1
                    WHEN 'intermediate' THEN 2
                    WHEN 'advanced' THEN 3
                    ELSE 1 END,
                c.estimated_duration = $duration, c.created_at = timestamp()
            """;
            manager.execute_query(create_query, concept);
        }
        
        ## Create prerequisite relationships
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
        
        ## Create learning path
        path_query = """
        MERGE (p:LearningPath {path_id: "programming_fundamentals"})
        SET p.name = "programming_fundamentals", p.title = "Programming Fundamentals",
            p.description = "Master the fundamentals of programming from basics to advanced concepts",
            p.difficulty = "beginner", p.difficulty_score = 1,
            p.estimated_duration = 480, p.concept_count = 6,
            p.created_at = timestamp()
        """;
        manager.execute_query(path_query, None);
        
        ## Add concepts to path
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
            MERGE (p)-[:PathContains {order_index: $order, is_required: true, created_at: timestamp()}]->(c)
            """;
            manager.execute_query(contain_query, pc);
        }
        
        report {
            "success": true,
            "message": "Graph seeded successfully",
            "concepts_created": len(concepts),
            "prerequisites_created": len(prereqs),
            "paths_created": 1
        };
    }
    
    ## Clear all graph data
    can clear_graph with entry {
        manager = neo4j_db.get_neo4j_manager();
        
        query = """
        MATCH (n)
        DETACH DELETE n
        """;
        
        result = manager.execute_query(query, None);
        
        report {
            "success": true,
            "message": "Graph cleared successfully"
        };
    }
}
