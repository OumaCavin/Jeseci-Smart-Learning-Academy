import os
import psycopg2
from psycopg2 import pool, extras, extensions
import logging
from typing import Optional, List, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

class PostgresManager:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresManager, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        """Initialize the connection pool and register types"""
        try:
            # ---------------------------------------------------------
            # FIX: Register Type Adapters for OID 1043 (varchar/text)
            # This prevents the "Unknown PG numeric type: 1043" crash
            # ---------------------------------------------------------
            def cast_text(value, cur):
                return value
            
            STRING_OIDS = (1043, 25, 705) # varchar, text, unknown
            new_type = extensions.new_type(STRING_OIDS, "STRING_TYPES", cast_text)
            extensions.register_type(new_type)
            # ---------------------------------------------------------

            self.schema = os.getenv("DB_SCHEMA", "jeseci_academy")
            
            # Initialize Pool
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", 5432)),
                database=os.getenv("POSTGRES_DB", "jeseci_learning_academy"),
                user=os.getenv("POSTGRES_USER", "jeseci_academy_user"),
                password=os.getenv("POSTGRES_PASSWORD", "jeseci_secure_password_2024")
            )
            logger.info(f"PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise

    def get_connection(self):
        return self._pool.getconn()

    def return_connection(self, conn):
        if self._pool:
            self._pool.putconn(conn)

    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Execute a query and return dictionary results"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                return [dict(row) for row in result]
            else:
                conn.commit()
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"Database query error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                self.return_connection(conn)

# Global accessor function used by your other files
def get_postgres_manager():
    return PostgresManager()
