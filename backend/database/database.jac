## Database Module for Jeseci Smart Learning Academy
##
## This module provides database connectivity for PostgreSQL and Neo4j
## through Python integration. It wraps the Python database connection
## managers with Jaclang-compatible interfaces.
##
## Usage:
##   import from database.database { DatabaseManager, test_db_connections }
##
import backend.database as py_db;
import os;

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
        std.out("PostgreSQL:", pg_status);
        std.out("Neo4j:", neo4j_status);

        report {
            "postgresql": result['postgresql'],
            "neo4j": result['neo4j'],
            "initialized": True
        } ;
    }

    ## Test PostgreSQL connection
    can test_postgresql with entry {
        result = py_db.test_all_connections();

        report {
            "connected": result['postgresql'],
            "database": "postgresql",
            "status": "healthy" if result['postgresql'] else "unavailable"
        } ;
    }

    ## Test Neo4j connection
    can test_neo4j with entry {
        result = py_db.test_all_connections();

        report {
            "connected": result['neo4j'],
            "database": "neo4j",
            "status": "healthy" if result['neo4j'] else "unavailable"
        } ;
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
        } ;
    }

    ## Execute custom PostgreSQL query
    can query_postgres with entry {
        query = "SELECT 1 AS test";
        manager = py_db.get_postgres_manager();
        db_result = manager.execute_query(query, None);

        if db_result {
            report {"success": True, "data": db_result, "count": len(db_result)} ;
        } else {
            report {"success": False, "error": "Query execution failed"} ;
        }
    }

    ## Execute custom Neo4j Cypher query
    can query_neo4j with entry {
        query = "RETURN 1 AS test";
        manager = py_db.get_neo4j_manager();
        db_result = manager.execute_query(query, None);

        if db_result {
            report {"success": True, "data": db_result, "count": len(db_result)} ;
        } else {
            report {"success": False, "error": "Query execution failed"} ;
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
        } ;
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
        } ;
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
        } ;
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
        } ;
    }

    ## Store contact form submission in database
    can store_contact_message with entry {
        contact_data = {
            "message_id": "test_msg_001",
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "Test message content",
            "phone": "",
            "contact_reason": "general",
            "timestamp": 0,
            "status": "pending",
            "ip_address": "127.0.0.1",
            "user_agent": "Test Agent"
        };

        manager = py_db.get_postgres_manager();
        schema = os.getenv("DB_SCHEMA", "jeseci_academy");
        table_name = schema + ".contact_messages";

        query = """
        INSERT INTO """ + table_name + """ (
            message_id, name, email, subject, message, phone,
            contact_reason, timestamp, status, ip_address, user_agent
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
        ) RETURNING message_id
        """;

        params = (
            contact_data['message_id'],
            contact_data['name'],
            contact_data['email'],
            contact_data['subject'],
            contact_data['message'],
            contact_data['phone'],
            contact_data['contact_reason'],
            contact_data['timestamp'],
            contact_data['status'],
            contact_data['ip_address'],
            contact_data['user_agent']
        );

        result = manager.execute_query(query, params);

        if result and len(result) > 0 {
            report {
                "success": True,
                "message_id": result[0]['message_id'],
                "message": "Contact message stored successfully"
            } ;
        } else {
            report {"success": False, "error": "Failed to store contact message"} ;
        }
    }

    ## Get contact messages from database
    can get_contact_messages with entry {
        manager = py_db.get_postgres_manager();
        schema = os.getenv("DB_SCHEMA", "jeseci_academy");
        table_name = schema + ".contact_messages";

        query = """
        SELECT
            message_id, name, email, subject, message, phone,
            contact_reason, timestamp, status, ip_address, user_agent
        FROM """ + table_name + """
        ORDER BY timestamp DESC
        LIMIT 50
        """;

        result = manager.execute_query(query, None);

        # Get total count and unread count
        count_query = "SELECT COUNT(*) as total FROM " + table_name;
        unread_query = "SELECT COUNT(*) as unread FROM " + table_name + " WHERE status = 'pending'";

        total_result = manager.execute_query(count_query, None);
        unread_result = manager.execute_query(unread_query, None);

        report {
            "success": True,
            "messages": result or [],
            "total": total_result[0]['total'] if total_result else 0,
            "unread_count": unread_result[0]['unread'] if unread_result else 0
        } ;
    }

    ## Mark contact message as read
    can mark_contact_as_read with entry {
        message_id = "test_msg_001";

        manager = py_db.get_postgres_manager();
        schema = os.getenv("DB_SCHEMA", "jeseci_academy");
        table_name = schema + ".contact_messages";

        query = "UPDATE " + table_name + " SET status = 'read' WHERE message_id = $1 RETURNING message_id";
        result = manager.execute_query(query, (message_id, ));

        if result and len(result) > 0 {
            report {"success": True, "message": "Message marked as read"} ;
        } else {
            report {"success": False, "error": "Message not found"} ;
        }
    }

    ## Store testimonial in database
    can store_testimonial with entry {
        testimonial_data = {
            "name": "Test User",
            "role": "Developer",
            "company": "Test Corp",
            "content": "Great learning platform!",
            "rating": 5,
            "avatar_url": "",
            "is_approved": False
        };

        manager = py_db.get_postgres_manager();
        schema = os.getenv("DB_SCHEMA", "jeseci_academy");
        table_name = schema + ".testimonials";

        query = """
        INSERT INTO """ + table_name + """ (
            name, role, company, content, rating, avatar_url,
            is_approved, is_active
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8
        ) RETURNING id
        """;

        params = (
            testimonial_data['name'],
            testimonial_data.get('role'),
            testimonial_data.get('company'),
            testimonial_data['content'],
            testimonial_data.get('rating', 5),
            testimonial_data.get('avatar_url'),
            testimonial_data.get('is_approved', False),
            True
        );

        result = manager.execute_query(query, params);

        if result and len(result) > 0 {
            report {
                "success": True,
                "id": result[0]['id'],
                "message": "Testimonial stored successfully"
            } ;
        } else {
            report {"success": False, "error": "Failed to store testimonial"} ;
        }
    }

    ## Get testimonials from database
    can get_testimonials with entry {
        manager = py_db.get_postgres_manager();
        schema = os.getenv("DB_SCHEMA", "jeseci_academy");
        table_name = schema + ".testimonials";

        query = """
        SELECT id, name, role, company, content, rating, avatar_url, created_at
        FROM """ + table_name + """
        WHERE is_approved = True AND is_active = True
        ORDER BY created_at DESC
        """;

        result = manager.execute_query(query, None);

        report {
            "success": True,
            "testimonials": result or [],
            "total": len(result) if result else 0
        } ;
    }

    ## Close all database connections
    can close_connections with entry {
        py_db.close_all_connections();

        report {"success": True, "message": "All database connections closed"} ;
    }
}

## Database Initialization Walker
## Call this application startup to initialize database connections
walker InitDatabase {
    can init with entry {
        manager = py_db.DualWriteManager();

        report {"initialized": True, "message": "Database module ready"} ;
    }
}

## Quick connection test walker
walker test_db_connections {
    can run with entry {
        result = py_db.test_all_connections();
        report result ;
    }
}
