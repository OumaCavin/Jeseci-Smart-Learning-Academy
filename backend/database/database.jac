## Database Module for Jeseci Smart Learning Companion
##
## This module provides database connectivity for PostgreSQL and Neo4j
## through Python integration. It wraps the Python database connection
## managers with Jaclang-compatible interfaces.
##
## Usage:
##   import from database.database { DatabaseManager, test_db_connections }
##

import from python { PyModule }

glob py_db = PyModule("backend.database");

## Database Connection Status
node DatabaseStatus {
    has postgresql_connected: bool = False;
    has neo4j_connected: bool = False;
    has last_check: str = "";
}

## Concept node for graph database representation
node ConceptNode {
    has concept_id: str;
    has name: str;
    has display_name: str;
    has category: str;
    has difficulty_level: str;
    has description: str;
    has created_at: int = 0;
}

## Learning path node for graph representation
node LearningPathNode {
    has path_id: str;
    has name: str;
    has title: str;
    has difficulty: str;
    has estimated_duration: int;
    has description: str;
}

## User progress tracking node
node ProgressNode {
    has user_id: str;
    has concept_id: str;
    has progress_percent: int;
    has mastery_level: int;
    has last_accessed: int;
}

## Database Configuration
node DatabaseConfig {
    has postgres_host: str = "localhost";
    has postgres_port: int = 5432;
    has postgres_db: str = "jeseci_learning_academy";
    has neo4j_uri: str = "bolt://localhost:7687";
    has neo4j_database: str = "jeseci_academy";
}

## Main Database Manager Walker
## Provides database operations for the application
walker DatabaseManager {
    ## Initialize database connections
    can init_connections with entry {
        print("Initializing database connections...");
        
        result = py_db.test_all_connections();
        
        pg_status = "Connected" if result['postgresql'] else "Disconnected";
        neo4j_status = "Connected" if result['neo4j'] else "Disconnected";
        print("PostgreSQL: " + pg_status);
        print("Neo4j: " + neo4j_status);
        
        report {
            "postgresql": result['postgresql'],
            "neo4j": result['neo4j'],
            "initialized": True
        };
    }
    
    ## Test PostgreSQL connection
    can test_postgresql with entry {
        result = py_db.test_all_connections();
        
        report {
            "connected": result['postgresql'],
            "database": "postgresql",
            "status": "healthy" if result['postgresql'] else "unavailable"
        };
    }
    
    ## Test Neo4j connection
    can test_neo4j with entry {
        result = py_db.test_all_connections();
        
        report {
            "connected": result['neo4j'],
            "database": "neo4j",
            "status": "healthy" if result['neo4j'] else "unavailable"
        };
    }
    
    ## Get full database status
    can get_status with entry {
        result = py_db.test_all_connections();
        
        config = py_db.DatabaseConfig();
        
        report {
            "postgresql": {
                "connected": result['postgresql'],
                "host": config.postgres_host,
                "port": config.postgres_port,
                "database": config.postgres_db
            },
            "neo4j": {
                "connected": result['neo4j'],
                "uri": config.neo4j_uri,
                "database": config.neo4j_database
            }
        };
    }
    
    ## Execute custom PostgreSQL query
    can query_postgres with entry {
        query = "SELECT 1 AS test";
        manager = py_db.get_postgres_manager();
        db_result = manager.execute_query(query, None);
        
        if db_result {
            report {
                "success": True,
                "data": db_result,
                "count": len(db_result)
            };
        } else {
            report {
                "success": False,
                "error": "Query execution failed"
            };
        }
    }
    
    ## Execute custom Neo4j Cypher query
    can query_neo4j with entry {
        query = "RETURN 1 AS test";
        manager = py_db.get_neo4j_manager();
        db_result = manager.execute_query(query, None);
        
        if db_result {
            report {
                "success": True,
                "data": db_result,
                "count": len(db_result)
            };
        } else {
            report {
                "success": False,
                "error": "Query execution failed"
            };
        }
    }
    
    ## Sync a concept to Neo4j graph
    can sync_concept with entry {
        concept_id = "test_concept";
        name = "test_name";
        display_name = "Test Name";
        category = "test";
        difficulty_level = "beginner";
        description = "";
        
        manager = py_db.get_dual_write_manager();
        sync_result = manager.sync_concept_to_neo4j(
            concept_id, name, display_name, category, difficulty_level, description
        );
        
        report {
            "success": sync_result != None,
            "operation": "sync_concept",
            "concept_id": concept_id
        };
    }
    
    ## Create relationship between concepts
    can create_relationship with entry {
        source_id = "source_1";
        target_id = "target_1";
        relationship_type = "RELATED_TO";
        strength = 1;
        
        manager = py_db.get_dual_write_manager();
        result = manager.create_concept_relationship(
            source_id, target_id, relationship_type, strength
        );
        
        report {
            "success": result != None,
            "operation": "create_relationship",
            "source": source_id,
            "target": target_id,
            "type": relationship_type
        };
    }
    
    ## Get personalized learning recommendations
    can get_recommendations with entry {
        user_id = "user_1";
        completed_ids = [];
        limit = 5;
        
        manager = py_db.get_dual_write_manager();
        result = manager.get_learning_recommendations(user_id, completed_ids, limit);
        
        report {
            "success": result != None,
            "data": result or [],
            "user_id": user_id,
            "limit": limit
        };
    }
    
    ## Get concept graph from Neo4j
    can get_concept_graph with entry {
        concept_id = "concept_1";
        depth = 2;
        
        manager = py_db.get_dual_write_manager();
        result = manager.get_concept_graph(concept_id, depth);
        
        report {
            "success": result != None,
            "data": result or [],
            "concept_id": concept_id,
            "depth": depth
        };
    }
    
    ## Close all database connections
    can close_connections with entry {
        py_db.close_all_connections();
        
        report {
            "success": True,
            "message": "All database connections closed"
        };
    }
}

## Database Initialization Walker
## Call this at application startup to initialize database connections
walker InitDatabase {
    can init with entry {
        manager = py_db.DualWriteManager();
        
        report {
            "initialized": True,
            "message": "Database module ready"
        };
    }
}

## Quick connection test walker
walker test_db_connections {
    can run with entry {
        result = py_db.test_all_connections();
        report result;
    }
}
