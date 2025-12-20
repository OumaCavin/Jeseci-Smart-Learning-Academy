"""
Database configuration and connection management
Supports PostgreSQL, SQLite, Redis, and Neo4j
"""

import os
from typing import Generator, Optional, Union
from sqlalchemy import create_engine, MetaData, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import ARRAY
import redis
import neo4j
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# PostgreSQL configuration
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_USER = os.getenv("POSTGRES_USER", "jeseci_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
POSTGRES_DB = os.getenv("POSTGRES_DB", "jeseci_learning_academy")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Neo4j configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j_secure_password_2024")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_postgres_url() -> str:
    """Build PostgreSQL URL with explicit driver specification"""
    return f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

def get_sqlite_url() -> str:
    """Build SQLite URL"""
    return f"sqlite:///{os.getenv('SQLITE_DB_PATH', './jeseci_dev.db')}"

# =============================================================================
# DATABASE URL CONFIGURATION
# =============================================================================

# Database URLs - Auto-detect based on environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Use environment setting to determine database type
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment == "production":
        # Use PostgreSQL in production
        postgres_url = get_postgres_url()
        DATABASE_URL = postgres_url
    else:
        # Default to SQLite for development
        sqlite_url = get_sqlite_url()
        DATABASE_URL = sqlite_url

# =============================================================================
# DATABASE TYPE DETECTION
# =============================================================================

# Database type detection
IS_POSTGRES = "postgresql" in DATABASE_URL
IS_SQLITE = "sqlite" in DATABASE_URL

# =============================================================================
# CROSS-DATABASE COMPATIBILITY
# =============================================================================

def get_array_type():
    """Get appropriate array type for current database"""
    if IS_POSTGRES:
        return ARRAY(String)
    else:
        # For SQLite, we'll use JSON and handle conversion in the model
        return Text

def get_json_type():
    """Get JSON type for current database"""
    from sqlalchemy import JSON
    return JSON

# =============================================================================
# DATABASE SETUP
# =============================================================================

# SQLAlchemy setup
engine_kwargs = {
    "echo": os.getenv("DEBUG", "false").lower() == "true",
    "poolclass": StaticPool if "sqlite" in DATABASE_URL else None,
}

# Create engine
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base for declarative models
Base = declarative_base()
metadata = MetaData()

# Redis connection pool
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD if REDIS_PASSWORD else None,
    db=REDIS_DB,
    decode_responses=True
)

# Neo4j driver
neo4j_driver = None

# =============================================================================
# CONNECTION FUNCTIONS
# =============================================================================

def get_redis_connection() -> redis.Redis:
    """Get Redis connection from pool"""
    return redis.Redis(connection_pool=redis_pool)


def get_neo4j_driver():
    """Get Neo4j driver instance"""
    global neo4j_driver
    if neo4j_driver is None:
        neo4j_driver = neo4j.GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
    return neo4j_driver


def create_db_session() -> Generator[Session, None, None]:
    """Create database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions"""
    yield from create_db_session()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def close_db_connections():
    """Close all database connections"""
    engine.dispose()
    if neo4j_driver:
        neo4j_driver.close()

# =============================================================================
# HEALTH CHECK FUNCTIONS
# =============================================================================

def check_postgres_connection() -> bool:
    """Check PostgreSQL connection"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False


def check_redis_connection() -> bool:
    """Check Redis connection"""
    try:
        r = get_redis_connection()
        r.ping()
        return True
    except Exception:
        return False


def check_neo4j_connection() -> bool:
    """Check Neo4j connection"""
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            session.run("RETURN 1")
        return True
    except Exception:
        return False


def check_all_connections() -> dict:
    """Check all database connections"""
    return {
        "postgres": check_postgres_connection(),
        "redis": check_redis_connection(),
        "neo4j": check_neo4j_connection(),
        "sqlite": IS_SQLITE,
        "database_type": "postgresql" if IS_POSTGRES else "sqlite"
    }