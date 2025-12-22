# Database Module for Jeseci Smart Learning Companion

This module provides comprehensive database connectivity for PostgreSQL and Neo4j databases, enabling persistent storage and graph-based knowledge management for the learning platform.

## Features

### PostgreSQL Integration
- Thread-safe connection pooling
- RealDictCursor for dictionary-style result access
- Batch operations for efficient bulk inserts
- Automatic connection management

### Neo4j Graph Database
- Concept relationship management
- Learning path recommendations
- Graph traversal for personalized learning
- Knowledge graph visualization support

### Dual-Write Architecture
- Automatic synchronization between PostgreSQL and Neo4j
- Concept and learning path relationship management
- User progress tracking across both databases

## Installation

1. Install required dependencies:
```bash
pip install -r backend/database/requirements.txt
```

2. Configure database connections in `config/.env`:
```bash
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jeseci_learning_academy
POSTGRES_USER=jeseci_user
POSTGRES_PASSWORD=your_password

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=jeseci_academy
```

3. Run the database setup script:
```bash
bash backend/database/setup_databases.sh
```

## Usage

### Basic Database Operations

```jaclang
import from database.database { DatabaseManager, test_db_connections }

## Initialize and test connections
walker init_db {
    can init with entry {
        manager = DatabaseManager();
        status = manager.init_connections();
        print(status);
    }
}

## Test connection status
walker check_status {
    can status with entry {
        result = test_db_connections();
        print(result);
    }
}
```

### PostgreSQL Query Operations

```jaclang
walker DatabaseManager {
    can query_postgres(query: str, params: dict = None) with entry {
        # Execute custom PostgreSQL query
        result = self.query_postgres("SELECT * FROM concepts LIMIT 10");
        print(result);
    }
}
```

### Neo4j Graph Operations

```jaclang
walker DatabaseManager {
    can get_recommendations(user_id: str, completed_ids: list, limit: int = 5) with entry {
        # Get personalized learning recommendations
        result = self.get_recommendations(user_id, completed_ids, 5);
        print(result);
    }
    
    can get_concept_graph(concept_id: str, depth: int = 2) with entry {
        # Get related concepts from knowledge graph
        result = self.get_concept_graph(concept_id, depth);
        print(result);
    }
}
```

### Concept Synchronization

```jaclang
walker DatabaseManager {
    can sync_concept(concept_id: str, name: str, display_name: str, 
                     category: str, difficulty_level: str, description: str = "") with entry {
        # Sync concept to Neo4j graph
        result = self.sync_concept(concept_id, name, display_name, category, difficulty_level, description);
        print(result);
    }
    
    can create_relationship(source_id: str, target_id: str, 
                           relationship_type: str, strength: int = 1) with entry {
        # Create relationship between concepts
        result = self.create_relationship(source_id, target_id, relationship_type, strength);
        print(result);
    }
}
```

## Database Schema

### PostgreSQL Tables

| Table | Description |
|-------|-------------|
| `users` | User accounts and authentication |
| `concepts` | Learning concepts and content |
| `learning_paths` | Curated learning paths |
| `learning_path_concepts` | Path-concept relationships |
| `user_concept_progress` | User progress tracking |
| `user_learning_paths` | User path progress |
| `achievements` | Achievement definitions |
| `user_achievements` | User earned achievements |
| `quiz_attempts` | Quiz performance records |

### Neo4j Graph Structure

```
(Concept)-[:PREREQUISITE]->(Concept)
(Concept)-[:RELATED_TO]->(Concept)
(Concept)-[:PART_OF]->(Concept)
(Concept)-[:BUILDS_UPON]->(Concept)
(User)-[:COMPLETED]->(Concept)
(User)-[:ENROLLED_IN]->(LearningPath)
```

## API Reference

### DatabaseManager Walker

| Ability | Parameters | Description |
|---------|------------|-------------|
| `init_connections` | None | Initialize all database connections |
| `test_postgresql` | None | Test PostgreSQL connection |
| `test_neo4j` | None | Test Neo4j connection |
| `get_status` | None | Get full database status |
| `query_postgres` | query: str, params: dict | Execute PostgreSQL query |
| `query_neo4j` | query: str, params: dict | Execute Cypher query |
| `sync_concept` | concept_id, name, display_name, category, difficulty_level, description | Sync concept to Neo4j |
| `create_relationship` | source_id, target_id, relationship_type, strength | Create concept relationship |
| `get_recommendations` | user_id, completed_ids, limit | Get learning recommendations |
| `get_concept_graph` | concept_id, depth | Get concept subgraph |
| `close_connections` | None | Close all connections |

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U jeseci_user -d jeseci_learning_academy
```

### Neo4j Connection Issues

```bash
# Check Neo4j status
cypher-shell -u neo4j -p password "RETURN 1"

# View Neo4j logs
tail -f /var/log/neo4j/neo4j.log
```

### Python Module Import Errors

```bash
# Reinstall dependencies
pip install -r backend/database/requirements.txt

# Check Python path
python -c "import sys; sys.path.insert(0, 'backend'); from database import postgres_manager; print('Import successful')"
```

## Performance Considerations

1. **Connection Pooling**: PostgreSQL connections are pooled (5+10 overflow)
2. **Query Optimization**: Use parameterized queries to prevent SQL injection
3. **Graph Queries**: Limit depth in graph traversal operations
4. **Batch Operations**: Use batch inserts for bulk data loading

## Security Notes

1. Never commit `.env` files with real credentials
2. Use environment variables for sensitive data in production
3. Rotate database passwords regularly
4. Limit database user permissions to required operations
5. Enable SSL/TLS for production database connections
