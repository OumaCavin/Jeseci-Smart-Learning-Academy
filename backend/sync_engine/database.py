"""
Database Utilities for Sync Engine

This module provides database connection utilities for the synchronization
system, including PostgreSQL and Neo4j connections, session management,
and helper functions for database operations.

Author: Jeseci Development Team
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, List

import psycopg2
from psycopg2 import pool, extras
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from backend.sync_engine.config import get_database_config, get_redis_config
from backend.sync_engine.models import Base

logger = logging.getLogger(__name__)


class PostgresSyncManager:
    """
    PostgreSQL connection manager for synchronization operations.
    
    This class manages PostgreSQL connections for reading and writing
    synchronization events and status data. It uses connection pooling
    for efficient resource utilization.
    """
    
    _instance = None
    _pool = None
    _sqlalchemy_engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize connection pools"""
        db_config = get_database_config()
        
        # Initialize psycopg2 connection pool
        try:
            PostgresSyncManager._pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=5,
                host=db_config.postgres_host,
                port=db_config.postgres_port,
                database=db_config.postgres_db,
                user=db_config.postgres_user,
                password=db_config.postgres_password
            )
            logger.info(f"PostgreSQL sync pool initialized: {db_config.postgres_host}:{db_config.postgres_port}")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL sync pool: {e}")
            PostgresSyncManager._pool = None
        
        # Initialize SQLAlchemy engine
        try:
            connection_url = db_config.to_postgres_url()
            PostgresSyncManager._sqlalchemy_engine = create_engine(
                connection_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                echo=False
            )
            PostgresSyncManager._session_factory = sessionmaker(
                bind=PostgresSyncManager._sqlalchemy_engine
            )
            logger.info("SQLAlchemy engine initialized for sync operations")
        except Exception as e:
            logger.error(f"Failed to initialize SQLAlchemy engine: {e}")
            PostgresSyncManager._sqlalchemy_engine = None
    
    def get_connection(self):
        """Get a connection from the pool"""
        if PostgresSyncManager._pool is None:
            self._initialize()
        if PostgresSyncManager._pool:
            return PostgresSyncManager._pool.getconn()
        return None
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if PostgresSyncManager._pool and conn:
            PostgresSyncManager._pool.putconn(conn)
    
    @contextmanager
    def get_session(self) -> Session:
        """Get a SQLAlchemy session"""
        if PostgresSyncManager._session_factory is None:
            self._initialize()
        
        session = PostgresSyncManager._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dicts"""
        conn = self.get_connection()
        if conn is None:
            logger.error("No PostgreSQL connection available")
            return []
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"PostgreSQL query error: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an update/insert/delete and return affected rows"""
        conn = self.get_connection()
        if conn is None:
            logger.error("No PostgreSQL connection available")
            return 0
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"PostgreSQL update error: {e}")
            if conn:
                conn.rollback()
            return 0
        finally:
            self.return_connection(conn)
    
    def close(self):
        """Close all connections"""
        if PostgresSyncManager._pool:
            PostgresSyncManager._pool.closeall()
            PostgresSyncManager._pool = None
        if PostgresSyncManager._sqlalchemy_engine:
            PostgresSyncManager._sqlalchemy_engine.dispose()
            PostgresSyncManager._sqlalchemy_engine = None
        logger.info("PostgreSQL sync connections closed")
    
    @property
    def schema(self) -> str:
        """Get the current schema name"""
        return get_database_config().postgres_schema


class Neo4jSyncManager:
    """
    Neo4j connection manager for synchronization operations.
    
    This class manages Neo4j connections for reading and writing
    graph data during synchronization. It provides methods for
    creating, updating, and deleting nodes and relationships.
    """
    
    _instance = None
    _driver = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Neo4j driver"""
        from neo4j import GraphDatabase
        
        db_config = get_database_config()
        
        try:
            Neo4jSyncManager._driver = GraphDatabase.driver(
                db_config.neo4j_uri,
                auth=(db_config.neo4j_user, db_config.neo4j_password)
            )
            logger.info(f"Neo4j sync driver initialized: {db_config.neo4j_uri}")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j sync driver: {e}")
            Neo4jSyncManager._driver = None
    
    def get_session(self):
        """Get a Neo4j session"""
        if Neo4jSyncManager._driver is None:
            self._initialize()
        if Neo4jSyncManager._driver:
            return Neo4jSyncManager._driver.session()
        return None
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results"""
        session = self.get_session()
        if session is None:
            logger.error("No Neo4j session available")
            return []
        
        try:
            result = session.run(query, parameters)
            return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            return []
        finally:
            if session:
                session.close()
    
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> bool:
        """Execute a write operation and return success status"""
        session = self.get_session()
        if session is None:
            logger.error("No Neo4j session available")
            return False
        
        try:
            session.execute_write(lambda tx: tx.run(query, parameters))
            return True
        except Exception as e:
            logger.error(f"Neo4j write error: {e}")
            return False
        finally:
            if session:
                session.close()
    
    def close(self):
        """Close Neo4j driver"""
        if Neo4jSyncManager._driver:
            Neo4jSyncManager._driver.close()
            Neo4jSyncManager._driver = None
        logger.info("Neo4j sync connections closed")
    
    def get_node(self, label: str, property_name: str, property_value: str) -> Optional[Dict[str, Any]]:
        """Get a node by label and property"""
        query = f"""
        MATCH (n:{label} {{{property_name}: $value}})
        RETURN n
        """
        results = self.execute_query(query, {"value": property_value})
        return results[0].get("n") if results else None
    
    def node_exists(self, label: str, property_name: str, property_value: str) -> bool:
        """Check if a node exists"""
        query = f"""
        MATCH (n:{label} {{{property_name}: $value}})
        RETURN count(n) as count
        """
        results = self.execute_query(query, {"value": property_value})
        return results[0].get("count", 0) > 0 if results else False
    
    def get_node_version(self, label: str, property_name: str, property_value: str) -> Optional[int]:
        """Get the updated_at timestamp of a node"""
        query = f"""
        MATCH (n:{label} {{{property_name}: $value}})
        RETURN n.updated_at as version
        """
        results = self.execute_query(query, {"value": property_value})
        if results and results[0].get("version"):
            return int(results[0]["version"].timestamp())
        return None


class RedisSyncManager:
    """
    Redis connection manager for message queue operations.
    
    This class manages Redis connections for publishing and consuming
    synchronization events using Redis Streams.
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Redis connection pool"""
        import redis
        
        redis_config = get_redis_config()
        
        try:
            RedisSyncManager._pool = redis.ConnectionPool(
                host=redis_config.host,
                port=redis_config.port,
                db=redis_config.db,
                password=redis_config.password,
                ssl=redis_config.ssl,
                max_connections=redis_config.max_connections,
                socket_timeout=redis_config.socket_timeout,
                socket_connect_timeout=redis_config.socket_connect_timeout,
                decode_responses=True
            )
            logger.info(f"Redis sync pool initialized: {redis_config.host}:{redis_config.port}")
        except Exception as e:
            logger.error(f"Failed to initialize Redis sync pool: {e}")
            RedisSyncManager._pool = None
    
    def get_client(self):
        """Get a Redis client from the pool"""
        import redis
        
        if RedisSyncManager._pool is None:
            self._initialize()
        if RedisSyncManager._pool:
            return redis.Redis(connection_pool=RedisSyncManager._pool)
        return None
    
    def stream_exists(self, stream_name: str) -> bool:
        """Check if a stream exists"""
        client = self.get_client()
        if client is None:
            return False
        
        try:
            return client.exists(stream_name) > 0
        except Exception as e:
            logger.error(f"Redis stream check error: {e}")
            return False
    
    def create_stream_with_group(self, stream_name: str, group_name: str) -> bool:
        """Create a stream with consumer group if not exists"""
        client = self.get_client()
        if client is None:
            return False
        
        try:
            # Create stream with a dummy message if it doesn't exist
            if not self.stream_exists(stream_name):
                client.xadd(stream_name, {"init": "1"}, maxlen=1, approximate=True)
            
            # Create consumer group if it doesn't exist
            try:
                client.xgroup_create(stream_name, group_name, mkstream=True)
                logger.info(f"Created consumer group '{group_name}' for stream '{stream_name}'")
            except Exception:
                # Group may already exist
                pass
            
            return True
        except Exception as e:
            logger.error(f"Redis stream/group creation error: {e}")
            return False
    
    def close(self):
        """Close Redis connections"""
        if RedisSyncManager._pool:
            RedisSyncManager._pool.disconnect()
            RedisSyncManager._pool = None
        logger.info("Redis sync connections closed")


# Global instances
postgres_sync_manager = PostgresSyncManager()
neo4j_sync_manager = Neo4jSyncManager()
redis_sync_manager = RedisSyncManager()


def get_postgres_sync_manager() -> PostgresSyncManager:
    """Get the PostgreSQL sync manager instance"""
    return postgres_sync_manager


def get_neo4j_sync_manager() -> Neo4jSyncManager:
    """Get the Neo4j sync manager instance"""
    return neo4j_sync_manager


def get_redis_sync_manager() -> RedisSyncManager:
    """Get the Redis sync manager instance"""
    return redis_sync_manager


def close_all_sync_connections():
    """Close all database connections"""
    postgres_sync_manager.close()
    neo4j_sync_manager.close()
    redis_sync_manager.close()


def initialize_sync_database():
    """Initialize sync-related database tables"""
    db_config = get_database_config()
    
    try:
        # Create schema if needed
        postgres_sync_manager.execute_update(
            f"CREATE SCHEMA IF NOT EXISTS {db_config.postgres_schema}"
        )
        
        # Create tables using SQLAlchemy
        if postgres_sync_manager._sqlalchemy_engine:
            Base.metadata.create_all(postgres_sync_manager._sqlalchemy_engine)
            logger.info("Sync database tables initialized")
        
        # Initialize Redis stream
        redis_config = get_redis_config()
        redis_sync_manager.create_stream_with_group(
            redis_config.stream_name,
            redis_config.consumer_group
        )
        
        logger.info("Sync database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize sync database: {e}")
        return False
