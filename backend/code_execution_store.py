#!/usr/bin/env python3
"""
Code Execution Store - Database operations for code snippets and execution history

Handles:
- Saving/loading code snippets
- Recording execution history
- Managing user code collections
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Ensure proper path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger_config import logger
import psycopg2
from psycopg2 import extras
from database import get_db_connection, DB_SCHEMA


@dataclass
class CodeSnippet:
    """Represents a saved code snippet"""
    id: str
    user_id: int
    title: str
    code_content: str
    language: str = "jac"
    description: Optional[str] = None
    is_public: bool = False
    folder_id: Optional[str] = None
    execution_count: int = 0
    last_executed_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class ExecutionHistory:
    """Represents a code execution record"""
    id: str
    snippet_id: Optional[str]
    user_id: int
    code_content: str
    status: str  # 'success', 'error', 'timeout'
    output: str
    error_message: Optional[str] = None
    execution_time_ms: int = 0
    entry_point: str = "init"
    created_at: datetime = None


@dataclass
class CodeFolder:
    """Represents a folder for organizing code snippets"""
    id: str
    user_id: int
    name: str
    description: Optional[str] = None
    parent_folder_id: Optional[str] = None
    color: str = "#3b82f6"
    created_at: datetime = None
    updated_at: datetime = None


def create_code_snippets_table(cursor):
    """Create code snippets and related tables"""
    logger.info("Creating code snippets tables...")
    
    # Code folders table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.code_folders (
            id VARCHAR(64) PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            parent_folder_id VARCHAR(64) REFERENCES {DB_SCHEMA}.code_folders(id) ON DELETE SET NULL,
            color VARCHAR(20) DEFAULT '#3b82f6',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Code snippets table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.code_snippets (
            id VARCHAR(64) PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            code_content TEXT NOT NULL,
            language VARCHAR(50) DEFAULT 'jac',
            description TEXT,
            is_public BOOLEAN DEFAULT FALSE,
            folder_id VARCHAR(64) REFERENCES {DB_SCHEMA}.code_folders(id) ON DELETE SET NULL,
            execution_count INTEGER DEFAULT 0,
            last_executed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Execution history table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.execution_history (
            id VARCHAR(64) PRIMARY KEY,
            snippet_id VARCHAR(64) REFERENCES {DB_SCHEMA}.code_snippets(id) ON DELETE SET NULL,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            code_content TEXT NOT NULL,
            status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'error', 'timeout', 'memory_exceeded')),
            output TEXT,
            error_message TEXT,
            execution_time_ms INTEGER DEFAULT 0,
            entry_point VARCHAR(100) DEFAULT 'init',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_code_snippets_user 
        ON {DB_SCHEMA}.code_snippets(user_id)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_code_snippets_folder 
        ON {DB_SCHEMA}.code_snippets(folder_id)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_execution_history_user 
        ON {DB_SCHEMA}.execution_history(user_id, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_execution_history_snippet 
        ON {DB_SCHEMA}.execution_history(snippet_id, created_at DESC)
    """)
    
    logger.info("✓ Code snippets tables created: code_folders, code_snippets, execution_history")


class CodeSnippetStore:
    """Database operations for code snippets and execution history"""
    
    def __init__(self):
        """Initialize the store"""
        self.table_snippets = f"{DB_SCHEMA}.code_snippets"
        self.table_folders = f"{DB_SCHEMA}.code_folders"
        self.table_history = f"{DB_SCHEMA}.execution_history"
    
    # =========================================================================
    # Snippet Operations
    # =========================================================================
    
    def create_snippet(self, user_id: int, title: str, code_content: str, 
                       language: str = "jac", description: str = None,
                       is_public: bool = False, folder_id: str = None) -> str:
        """Create a new code snippet"""
        snippet_id = f"snippet_{uuid.uuid4().hex[:12]}"
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {self.table_snippets} 
                (id, user_id, title, code_content, language, description, is_public, folder_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (snippet_id, user_id, title, code_content, language, description, is_public, folder_id))
            
            conn.commit()
            logger.info(f"Created code snippet: {snippet_id}")
            return snippet_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating snippet: {e}")
            raise
        finally:
            conn.close()
    
    def get_snippet(self, snippet_id: str, user_id: int = None) -> Optional[Dict]:
        """Get a code snippet by ID"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute(f"""
                    SELECT * FROM {self.table_snippets}
                    WHERE id = %s AND (user_id = %s OR is_public = TRUE)
                """, (snippet_id, user_id))
            else:
                cursor.execute(f"""
                    SELECT * FROM {self.table_snippets}
                    WHERE id = %s
                """, (snippet_id,))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_snippet(row)
            return None
            
        finally:
            conn.close()
    
    def get_user_snippets(self, user_id: int, folder_id: str = None, 
                          limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get all snippets for a user"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            if folder_id:
                cursor.execute(f"""
                    SELECT * FROM {self.table_snippets}
                    WHERE user_id = %s AND folder_id = %s
                    ORDER BY updated_at DESC
                    LIMIT %s OFFSET %s
                """, (user_id, folder_id, limit, offset))
            else:
                cursor.execute(f"""
                    SELECT * FROM {self.table_snippets}
                    WHERE user_id = %s
                    ORDER BY updated_at DESC
                    LIMIT %s OFFSET %s
                """, (user_id, limit, offset))
            
            return [self._row_to_snippet(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def update_snippet(self, snippet_id: str, user_id: int, 
                       title: str = None, code_content: str = None,
                       description: str = None, is_public: bool = None,
                       folder_id: str = None) -> bool:
        """Update a code snippet"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = %s")
                params.append(title)
            if code_content is not None:
                updates.append("code_content = %s")
                params.append(code_content)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if is_public is not None:
                updates.append("is_public = %s")
                params.append(is_public)
            if folder_id is not None:
                updates.append("folder_id = %s")
                params.append(folder_id)
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.extend([snippet_id, user_id])
            
            cursor.execute(f"""
                UPDATE {self.table_snippets}
                SET {', '.join(updates)}
                WHERE id = %s AND user_id = %s
            """, params)
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating snippet: {e}")
            raise
        finally:
            conn.close()
    
    def delete_snippet(self, snippet_id: str, user_id: int) -> bool:
        """Delete a code snippet"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                DELETE FROM {self.table_snippets}
                WHERE id = %s AND user_id = %s
            """, (snippet_id, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting snippet: {e}")
            raise
        finally:
            conn.close()
    
    def increment_execution_count(self, snippet_id: str):
        """Increment the execution count for a snippet"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE {self.table_snippets}
                SET execution_count = execution_count + 1,
                    last_executed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (snippet_id,))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error incrementing execution count: {e}")
        finally:
            conn.close()
    
    # =========================================================================
    # Execution History Operations
    # =========================================================================
    
    def record_execution(self, user_id: int, code_content: str, status: str,
                         output: str, error_message: str = None,
                         execution_time_ms: int = 0, entry_point: str = "init",
                         snippet_id: str = None) -> str:
        """Record a code execution"""
        history_id = f"exec_{uuid.uuid4().hex[:12]}"
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {self.table_history}
                (id, snippet_id, user_id, code_content, status, output, error_message, execution_time_ms, entry_point)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (history_id, snippet_id, user_id, code_content, status, output, 
                  error_message, execution_time_ms, entry_point))
            
            conn.commit()
            return history_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error recording execution: {e}")
            raise
        finally:
            conn.close()
    
    def get_execution_history(self, user_id: int, limit: int = 20, 
                              offset: int = 0) -> List[Dict]:
        """Get execution history for a user"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {self.table_history}
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, limit, offset))
            
            return [self._row_to_history(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_snippet_history(self, snippet_id: str, limit: int = 10) -> List[Dict]:
        """Get execution history for a specific snippet"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {self.table_history}
                WHERE snippet_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (snippet_id, limit))
            
            return [self._row_to_history(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    # =========================================================================
    # Folder Operations
    # =========================================================================
    
    def create_folder(self, user_id: int, name: str, description: str = None,
                      parent_folder_id: str = None, color: str = "#3b82f6") -> str:
        """Create a new folder for organizing snippets"""
        folder_id = f"folder_{uuid.uuid4().hex[:12]}"
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {self.table_folders}
                (id, user_id, name, description, parent_folder_id, color)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (folder_id, user_id, name, description, parent_folder_id, color))
            
            conn.commit()
            return folder_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating folder: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_folders(self, user_id: int, parent_folder_id: str = None) -> List[Dict]:
        """Get all folders for a user"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            if parent_folder_id:
                cursor.execute(f"""
                    SELECT * FROM {self.table_folders}
                    WHERE user_id = %s AND parent_folder_id = %s
                    ORDER BY name ASC
                """, (user_id, parent_folder_id))
            else:
                cursor.execute(f"""
                    SELECT * FROM {self.table_folders}
                    WHERE user_id = %s AND parent_folder_id IS NULL
                    ORDER BY name ASC
                """, (user_id,))
            
            return [self._row_to_folder(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def delete_folder(self, folder_id: str, user_id: int, 
                      move_contents_to: str = None) -> bool:
        """Delete a folder"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            if move_contents_to:
                # Move snippets to new folder
                cursor.execute(f"""
                    UPDATE {self.table_snippets}
                    SET folder_id = %s
                    WHERE folder_id = %s AND user_id = %s
                """, (move_contents_to, folder_id, user_id))
            
            # Delete folder
            cursor.execute(f"""
                DELETE FROM {self.table_folders}
                WHERE id = %s AND user_id = %s
            """, (folder_id, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting folder: {e}")
            raise
        finally:
            conn.close()
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _row_to_snippet(self, row) -> Dict:
        """Convert database row to snippet dict"""
        return {
            "id": row[0],
            "user_id": row[1],
            "title": row[2],
            "code_content": row[3],
            "language": row[4],
            "description": row[5],
            "is_public": row[6],
            "folder_id": row[7],
            "execution_count": row[8],
            "last_executed_at": row[9].isoformat() if row[9] else None,
            "created_at": row[10].isoformat() if row[10] else None,
            "updated_at": row[11].isoformat() if row[11] else None
        }
    
    def _row_to_history(self, row) -> Dict:
        """Convert database row to history dict"""
        return {
            "id": row[0],
            "snippet_id": row[1],
            "user_id": row[2],
            "code_content": row[3],
            "status": row[4],
            "output": row[5],
            "error_message": row[6],
            "execution_time_ms": row[7],
            "entry_point": row[8],
            "created_at": row[9].isoformat() if row[9] else None
        }
    
    def _row_to_folder(self, row) -> Dict:
        """Convert database row to folder dict"""
        return {
            "id": row[0],
            "user_id": row[1],
            "name": row[2],
            "description": row[3],
            "parent_folder_id": row[4],
            "color": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None
        }


# Singleton instance
_code_snippet_store = None

def get_code_snippet_store() -> CodeSnippetStore:
    """Get the code snippet store singleton"""
    global _code_snippet_store
    if _code_snippet_store is None:
        _code_snippet_store = CodeSnippetStore()
    return _code_snippet_store
