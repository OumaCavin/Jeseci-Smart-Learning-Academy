# Database Architecture: Neo4j vs PostgreSQL

The Jeseci Smart Learning Academy project implements a **polyglot persistence architecture** that leverages both Neo4j (graph database) and PostgreSQL (relational database) for different types of data. Each database serves a distinct purpose based on its strengths in handling specific data models and query patterns.

## PostgreSQL Database (Relational Data)

PostgreSQL serves as the **primary system of record** for the application, storing all structured, transactional, and user-related data. The data stored in PostgreSQL follows traditional relational patterns with foreign key relationships and normalized structures designed for consistency, ACID compliance, and complex querying across multiple tables.

### PostgreSQL Data Domains

The PostgreSQL database contains the following data domains, all organized within the `jeseci_academy` schema:

#### User Management Domain

This domain includes core authentication data such as user credentials, email addresses, password hashes, administrative privileges, and account status. Extended user information encompasses personal profiles with names, biographies, avatar URLs, timezone preferences, and language settings. Learning preferences store daily study goals, preferred difficulty levels, content type preferences, notification settings, and UI preferences like dark mode.

#### Content Management Domain

This domain contains learning concepts with comprehensive metadata including difficulty levels, complexity scores, cognitive load assessments, key terms, synonyms, learning objectives, practical applications, and real-world examples. Concept content stores generated lesson materials, quizzes associated with concepts, and the relationships between concepts such as prerequisites, related topics, and build-upon connections implemented as a many-to-many association table.

#### Learning Progress Domain

This domain tracks user progress through various entities including concept progress records showing which concepts users have started and completed, learning path progress indicating enrollment and completion status of learning paths, lesson progress for granular tracking of individual lesson completion, and learning sessions that record study duration, timestamps, and activity metrics.

#### Assessment Domain

This domain encompasses quiz definitions with questions, answers, and scoring criteria, as well as quiz attempts that store user responses, scores, earned points, and timestamps for each assessment attempt.

#### Gamification Domain

This domain contains achievement definitions with criteria and rewards, user achievements tracking earned accomplishments with timestamps, badge definitions including icon URLs and descriptions, and user badges linking earned badges to specific users.

#### System Domain

This domain stores system logs for audit trails and debugging, system health metrics for monitoring, and AI agent configurations for content generation settings.

#### Authentication Data

Additionally, the `user_auth.py` module handles authentication-specific data including email verification tokens, verification status, and JWT token management, all stored in PostgreSQL.

## Neo4j Database (Graph Data)

Neo4j serves as the **knowledge graph and recommendation engine**, optimized for traversing relationships between concepts and generating personalized learning recommendations. The graph database excels at queries that involve navigating connections between entities, such as finding prerequisite chains, discovering related topics, and generating recommendations based on completed concepts.

### Neo4j Graph Structures

The Neo4j database stores the following graph structures:

#### Concept Nodes

Concept nodes represent learning concepts as first-class entities with properties including concept_id, name, display_name, category, subcategory, domain, difficulty level, complexity score, cognitive load, description, detailed description, key terms, synonyms, learning objectives, practical applications, and real-world examples. Each concept node can be indexed and constrained for uniqueness on concept_id.

#### Learning Path Nodes

Learning path nodes represent structured learning journeys containing path_id, name, title, description, category, difficulty level, estimated duration, target audience, concept count, and creation timestamp. Learning paths link to the concepts they contain through PathContains relationships with order_index and is_required properties.

#### Relationship Types

Relationship types define the connections between concepts and paths. PREREQUISITE relationships indicate that one concept must be completed before another can be started, with a strength property indicating dependency importance. RELATED_TO relationships suggest topics that are connected but not strictly required, useful for cross-referencing and expanded learning. BUILDS_UPON relationships indicate that a concept extends or enhances understanding of a prerequisite concept. PathContains relationships link learning paths to their constituent concepts with ordering information.

#### User Nodes

User nodes exist in Neo4j for tracking purposes but are minimal compared to PostgreSQL, primarily used for relationship-based queries connecting users to concepts and paths they've interacted with.

## Synchronization Strategy

The project implements a **dual-write architecture** through the `DualWriteManager` class located in `backend/database/__init__.py`, which coordinates writes to both databases to maintain consistency for certain data types. This approach recognizes that some data needs to exist in both systems for different query patterns and performance optimization.

### Data That Requires Synchronization

This includes concepts and learning content, which are created and updated in PostgreSQL via the SQLAlchemy ORM models, then mirrored to Neo4j through the `sync_concept_to_neo4j` method. This ensures that the knowledge graph remains synchronized with the relational content database. When a concept is created or updated in PostgreSQL, the dual-write manager creates or updates the corresponding node in Neo4j with the same properties. Similarly, learning path structures defined in PostgreSQL are synced to Neo4j with PathContains relationships connecting path nodes to concept nodes. The relationship definitions between concepts (prerequisites, related topics, builds-upon) are maintained in both databases to enable both relational queries in PostgreSQL and graph traversal queries in Neo4j.

### Data That Remains Database-Specific

User authentication data stays exclusively in PostgreSQL for security and consistency. User credentials, password hashes, email verification tokens, and JWT secrets must remain in PostgreSQL with proper ACID guarantees. User profiles and preferences also remain exclusively in PostgreSQL since they don't participate in graph-based queries and require strong consistency. Progress tracking data exists in PostgreSQL for reporting and analytics, though some minimal user-concept relationships may exist in Neo4j for recommendation purposes. Quiz and assessment data stays in PostgreSQL due to its transactional nature and complex relationships with concepts and users. Gamification achievements and badges remain in PostgreSQL for leaderboard calculations and user-facing displays.

### Current Synchronization Implementation

The `DualWriteManager` class provides methods for synchronization including `sync_concept_to_neo4j` for creating or updating concept nodes, `create_concept_relationship` for establishing graph relationships, `get_learning_recommendations` for personalized recommendations based on completed concepts, and `get_concept_graph` for retrieving related concepts up to a specified depth. The seeder script in `backend/seed.py` demonstrates the intended synchronization pattern by seeding concepts, learning paths, and relationships to Neo4j, while the same content exists in PostgreSQL through SQLAlchemy models.

### When Synchronization Should Occur

Synchronization happens during content creation when new concepts or learning paths are added through administrative interfaces, during batch imports when the seed script runs to populate initial content, and potentially during content updates if administrators modify concept metadata that should propagate to the graph. Real-time synchronization may not be strictly necessary for all updates depending on query patterns and acceptable data freshness.

## Recommendations for Production

For a production deployment, consider implementing event-driven synchronization where content creation and updates publish events to a message queue, and consumers update both databases asynchronously. This approach ensures loose coupling between databases while maintaining eventual consistency. You may want to implement a synchronization status tracking mechanism to detect and resolve conflicts between the two databases, especially if concepts are modified in both locations. Consider implementing a background reconciliation job that periodically compares the two databases and repairs any inconsistencies, which would be particularly valuable during development and testing phases when database state may become temporarily inconsistent.

## Architecture Summary

The current architecture is sound for a learning management system where concepts and their relationships form the core knowledge graph used for navigation and recommendations, while PostgreSQL handles all user-centric, transactional data requiring strong consistency. This polyglot persistence approach leverages the strengths of each database technology for optimal performance and functionality across different query patterns and use cases within the Jeseci Smart Learning Academy platform.
