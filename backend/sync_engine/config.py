"""
Configuration Module for Sync Engine

This module provides configuration management for the event-driven synchronization
system. It loads settings from environment variables and provides defaults.

Configuration includes:
- Redis connection settings
- PostgreSQL connection settings
- Neo4j connection settings
- Sync engine behavior parameters
- Retry and timeout settings

Author: Jeseci Development Team
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))


@dataclass
class RedisConfig:
    """Redis connection configuration"""
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", 6379))
    db: int = int(os.getenv("REDIS_DB", 0))
    password: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    ssl: bool = os.getenv("REDIS_SSL", "false").lower() == "true"
    
    # Stream configuration
    stream_name: str = os.getenv("REDIS_STREAM_NAME", "jeseci:sync:stream")
    consumer_group: str = os.getenv("REDIS_CONSUMER_GROUP", "jeseci:sync:consumers")
    
    # Connection pool settings
    max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", 10))
    socket_timeout: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", 5))
    socket_connect_timeout: int = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", 5))
    
    def to_url(self) -> str:
        """Generate Redis connection URL"""
        auth = f":{self.password}@" if self.password else ""
        ssl = "ssl=true" if self.ssl else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}?{ssl}" if self.password else f"redis://{self.host}:{self.port}/{self.db}"
    
    def __repr__(self) -> str:
        return f"RedisConfig(host={self.host}, port={self.port}, stream={self.stream_name})"


@dataclass
class SyncConfig:
    """Synchronization engine configuration"""
    
    # Batch processing
    batch_size: int = int(os.getenv("SYNC_BATCH_SIZE", 10))
    prefetch_count: int = int(os.getenv("SYNC_PREFETCH_COUNT", 10))
    
    # Retry settings
    max_retries: int = int(os.getenv("SYNC_MAX_RETRIES", 3))
    retry_delay_seconds: int = int(os.getenv("SYNC_RETRY_DELAY", 5))
    retry_backoff_multiplier: float = float(os.getenv("SYNC_RETRY_BACKOFF", 2.0))
    
    # Timeout settings
    event_processing_timeout_seconds: int = int(os.getenv("SYNC_PROCESSING_TIMEOUT", 30))
    consumer_idle_timeout_seconds: int = int(os.getenv("SYNC_CONSUMER_IDLE_TIMEOUT", 300))
    
    # Reconciliation job settings
    reconciliation_interval_seconds: int = int(os.getenv("SYNC_RECONCILIATION_INTERVAL", 300))
    reconciliation_batch_size: int = int(os.getenv("SYNC_RECONCILIATION_BATCH", 50))
    stale_event_threshold_minutes: int = int(os.getenv("SYNC_STALE_EVENT_THRESHOLD", 5))
    
    # Conflict resolution
    conflict_detection_enabled: bool = os.getenv("SYNC_CONFLICT_DETECTION", "true").lower() == "true"
    auto_repair_enabled: bool = os.getenv("SYNC_AUTO_REPAIR", "true").lower() == "true"
    
    # Logging
    log_level: str = os.getenv("SYNC_LOG_LEVEL", "INFO")
    
    def __repr__(self) -> str:
        return f"SyncConfig(batch_size={self.batch_size}, max_retries={self.max_retries}, reconciliation_interval={self.reconciliation_interval_seconds}s)"


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    
    # PostgreSQL (Source)
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_db: str = os.getenv("POSTGRES_DB", "jeseci_learning_academy")
    postgres_user: str = os.getenv("POSTGRES_USER", "jeseci_academy_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
    postgres_schema: str = os.getenv("POSTGRES_SCHEMA", "jeseci_academy")
    
    # Neo4j (Target)
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "neo4j_secure_password_2024")
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "jeseci_academy")
    
    def to_postgres_url(self) -> str:
        """Generate PostgreSQL connection URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    def __repr__(self) -> str:
        return f"DatabaseConfig(postgres={self.postgres_host}:{self.postgres_port}/{self.postgres_db}, neo4j={self.neo4j_uri})"


def get_redis_config() -> RedisConfig:
    """Get Redis configuration from environment"""
    return RedisConfig()


def get_sync_config() -> SyncConfig:
    """Get sync engine configuration from environment"""
    return SyncConfig()


def get_database_config() -> DatabaseConfig:
    """Get database configuration from environment"""
    return DatabaseConfig()


# Validate configuration on import
def validate_config() -> tuple[bool, list[str]]:
    """
    Validate that all required configuration is present.
    
    Returns:
        Tuple of (is_valid, list of missing configuration keys)
    """
    errors = []
    
    # Check Redis configuration
    redis_config = get_redis_config()
    if not redis_config.host:
        errors.append("REDIS_HOST")
    if redis_config.port <= 0:
        errors.append("REDIS_PORT (must be positive)")
    
    # Check PostgreSQL configuration
    db_config = get_database_config()
    if not db_config.postgres_host:
        errors.append("POSTGRES_HOST")
    if not db_config.postgres_user:
        errors.append("POSTGRES_USER")
    if not db_config.postgres_password:
        errors.append("POSTGRES_PASSWORD")
    if not db_config.postgres_schema:
        errors.append("POSTGRES_SCHEMA")
    
    # Check Neo4j configuration
    if not db_config.neo4j_uri:
        errors.append("NEO4J_URI")
    if not db_config.neo4j_user:
        errors.append("NEO4J_USER")
    if not db_config.neo4j_password:
        errors.append("NEO4J_PASSWORD")
    
    return len(errors) == 0, errors
