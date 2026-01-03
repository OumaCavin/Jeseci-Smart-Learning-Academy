#!/usr/bin/env python3
"""
Code Execution Store - Database operations for code snippets, execution history, versioning, and testing

Handles:
- Saving/loading code snippets
- Recording execution history
- Managing version history for snippets
- Creating and managing test cases
- Recording test results for auto-grading
- Educational error suggestions
- Debug session tracking
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


@dataclass
class SnippetVersion:
    """Represents a version of a code snippet for history tracking"""
    id: str
    snippet_id: str
    version_number: int
    code_content: str
    title: str
    description: Optional[str] = None
    created_by: int
    change_summary: Optional[str] = None
    created_at: datetime = None


@dataclass
class TestCase:
    """Represents a test case for auto-grading code snippets"""
    id: str
    snippet_id: str
    name: str
    input_data: str
    expected_output: str
    is_hidden: bool = False
    order_index: int = 0
    timeout_ms: int = 5000
    created_by: int
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class TestResult:
    """Represents the result of running a test case"""
    id: str
    test_case_id: str
    execution_id: str
    passed: bool
    actual_output: str
    execution_time_ms: int
    error_message: Optional[str] = None
    created_at: datetime = None


@dataclass
class ErrorKnowledge:
    """Represents educational error suggestions for common mistakes"""
    id: str
    error_pattern: str
    error_type: str
    title: str
    description: str
    suggestion: str
    examples: Optional[str] = None
    documentation_link: Optional[str] = None
    language: str = "jac"
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class DebugSession:
    """Represents a debugging session for step-through debugging"""
    id: str
    user_id: int
    snippet_id: str
    status: str  # 'active', 'paused', 'completed', 'terminated'
    current_line: Optional[int] = None
    breakpoints: Optional[str] = None  # JSON array stored as text
    variables: Optional[str] = None    # JSON object stored as text
    call_stack: Optional[str] = None   # JSON array stored as text
    created_at: datetime = None
    updated_at: datetime = None


def create_code_snippets_table(cursor):
    """Create code snippets and related tables including versioning and testing"""
    logger.info("Creating code snippets and related tables...")
    
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
    
    # Code snippets table - expanded with multi-language support
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
    
    # Execution history table - expanded with more status types
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.execution_history (
            id VARCHAR(64) PRIMARY KEY,
            snippet_id VARCHAR(64) REFERENCES {DB_SCHEMA}.code_snippets(id) ON DELETE SET NULL,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            code_content TEXT NOT NULL,
            status VARCHAR(30) NOT NULL CHECK (status IN ('success', 'error', 'timeout', 'memory_exceeded', 'output_exceeded')),
            output TEXT,
            error_message TEXT,
            execution_time_ms INTEGER DEFAULT 0,
            entry_point VARCHAR(100) DEFAULT 'init',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Snippet versions table for version history
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.snippet_versions (
            id VARCHAR(64) PRIMARY KEY,
            snippet_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.code_snippets(id) ON DELETE CASCADE,
            version_number INTEGER NOT NULL,
            code_content TEXT NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            created_by INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            change_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(snippet_id, version_number)
        )
    """)
    
    # Test cases table for auto-grading
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.test_cases (
            id VARCHAR(64) PRIMARY KEY,
            snippet_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.code_snippets(id) ON DELETE CASCADE,
            name VARCHAR(200) NOT NULL,
            input_data TEXT,
            expected_output TEXT NOT NULL,
            is_hidden BOOLEAN DEFAULT FALSE,
            order_index INTEGER DEFAULT 0,
            timeout_ms INTEGER DEFAULT 5000,
            created_by INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Test results table for recording test execution
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.test_results (
            id VARCHAR(64) PRIMARY KEY,
            test_case_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.test_cases(id) ON DELETE CASCADE,
            execution_id VARCHAR(64) REFERENCES {DB_SCHEMA}.execution_history(id) ON DELETE SET NULL,
            passed BOOLEAN NOT NULL,
            actual_output TEXT,
            execution_time_ms INTEGER DEFAULT 0,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Error knowledge base for educational suggestions
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.error_knowledge_base (
            id VARCHAR(64) PRIMARY KEY,
            error_pattern VARCHAR(500) NOT NULL,
            error_type VARCHAR(100) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            suggestion TEXT NOT NULL,
            examples TEXT,
            documentation_link VARCHAR(500),
            language VARCHAR(50) DEFAULT 'jac',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Debug sessions table for step-through debugging
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_SCHEMA}.debug_sessions (
            id VARCHAR(64) PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES {DB_SCHEMA}.users(id) ON DELETE CASCADE,
            snippet_id VARCHAR(64) NOT NULL REFERENCES {DB_SCHEMA}.code_snippets(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'terminated')),
            current_line INTEGER,
            breakpoints TEXT,
            variables TEXT,
            call_stack TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for performance optimization
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
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_snippet_versions_snippet 
        ON {DB_SCHEMA}.snippet_versions(snippet_id, version_number DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_test_cases_snippet 
        ON {DB_SCHEMA}.test_cases(snippet_id, order_index)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_test_results_case 
        ON {DB_SCHEMA}.test_results(test_case_id, created_at DESC)
    """)
    
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{DB_SCHEMA}_debug_sessions_user 
        ON {DB_SCHEMA}.debug_sessions(user_id, status)
    """)
    
    logger.info("✓ Code snippets and related tables created: code_folders, code_snippets, execution_history, snippet_versions, test_cases, test_results, error_knowledge_base, debug_sessions")


class CodeSnippetStore:
    """Database operations for code snippets, execution history, versioning, testing, and debugging"""
    
    def __init__(self):
        """Initialize the store with table names"""
        self.table_snippets = f"{DB_SCHEMA}.code_snippets"
        self.table_folders = f"{DB_SCHEMA}.code_folders"
        self.table_history = f"{DB_SCHEMA}.execution_history"
        self.table_versions = f"{DB_SCHEMA}.snippet_versions"
        self.table_test_cases = f"{DB_SCHEMA}.test_cases"
        self.table_test_results = f"{DB_SCHEMA}.test_results"
        self.table_error_knowledge = f"{DB_SCHEMA}.error_knowledge_base"
        self.table_debug_sessions = f"{DB_SCHEMA}.debug_sessions"
    
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
    # Version History Operations
    # =========================================================================
    
    def create_version(self, snippet_id: str, code_content: str, title: str,
                       created_by: int, description: str = None,
                       change_summary: str = None) -> str:
        """Create a new version of a snippet for history tracking"""
        version_id = f"ver_{uuid.uuid4().hex[:12]}"
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get the next version number
            cursor.execute(f"""
                SELECT COALESCE(MAX(version_number), 0) + 1 FROM {self.table_versions}
                WHERE snippet_id = %s
            """, (snippet_id,))
            version_number = cursor.fetchone()[0]
            
            cursor.execute(f"""
                INSERT INTO {self.table_versions}
                (id, snippet_id, version_number, code_content, title, description, created_by, change_summary)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (version_id, snippet_id, version_number, code_content, title, 
                  description, created_by, change_summary))
            
            conn.commit()
            logger.info(f"Created snippet version: {version_id} (v{version_number})")
            return version_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating version: {e}")
            raise
        finally:
            conn.close()
    
    def get_snippet_versions(self, snippet_id: str) -> List[Dict]:
        """Get all versions of a snippet"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {self.table_versions}
                WHERE snippet_id = %s
                ORDER BY version_number DESC
            """, (snippet_id,))
            
            return [self._row_to_version(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_snippet_version(self, version_id: str) -> Optional[Dict]:
        """Get a specific version by ID"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {self.table_versions}
                WHERE id = %s
            """, (version_id,))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_version(row)
            return None
            
        finally:
            conn.close()
    
    def create_snippet_version(self, snippet_id: str, version_number: int,
                               code_content: str, title: str,
                               created_by: int, description: str = None,
                               change_summary: str = None,
                               created_at: datetime = None) -> Dict:
        """Create a new version of a snippet with explicit version number"""
        version_id = f"ver_{uuid.uuid4().hex[:12]}"
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {self.table_versions}
                (id, snippet_id, version_number, code_content, title, description, created_by, change_summary, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (version_id, snippet_id, version_number, code_content, title, 
                  description, created_by, change_summary, created_at or datetime.now()))
            
            conn.commit()
            
            # Return the created version
            return self.get_snippet_version(version_id)
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating snippet version: {e}")
            raise
        finally:
            conn.close()
    
    def get_version(self, version_id: str) -> Optional[Dict]:
        """Get a specific version by ID"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {self.table_versions}
                WHERE id = %s
            """, (version_id,))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_version(row)
            return None
            
        finally:
            conn.close()
    
    def restore_version(self, version_id: str, user_id: int) -> bool:
        """Restore a snippet to a previous version"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get the version to restore
            cursor.execute(f"""
                SELECT * FROM {self.table_versions}
                WHERE id = %s
            """, (version_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            version = self._row_to_version(row)
            snippet_id = version["snippet_id"]
            
            # Create a new version with the restored content
            self.create_version(
                snippet_id=snippet_id,
                code_content=version["code_content"],
                title=version["title"],
                created_by=user_id,
                description=version.get("description"),
                change_summary=f"Restored from version {version['version_number']}"
            )
            
            # Update the current snippet content
            cursor.execute(f"""
                UPDATE {self.table_snippets}
                SET code_content = %s, title = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (version["code_content"], version["title"], snippet_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error restoring version: {e}")
            raise
        finally:
            conn.close()
    
    # =========================================================================
    # Test Case Operations
    # =========================================================================
    
    def create_test_case(self, snippet_id: str, name: str, expected_output: str,
                         input_data: str = None, is_hidden: bool = False,
                         order_index: int = 0, timeout_ms: int = 5000,
                         created_by: int = None) -> str:
        """Create a new test case for a snippet"""
        test_case_id = f"test_{uuid.uuid4().hex[:12]}"
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {self.table_test_cases}
                (id, snippet_id, name, input_data, expected_output, is_hidden, order_index, timeout_ms, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (test_case_id, snippet_id, name, input_data, expected_output, 
                  is_hidden, order_index, timeout_ms, created_by))
            
            conn.commit()
            logger.info(f"Created test case: {test_case_id}")
            return test_case_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating test case: {e}")
            raise
        finally:
            conn.close()
    
    def get_snippet_test_cases(self, snippet_id: str, include_hidden: bool = False) -> List[Dict]:
        """Get all test cases for a snippet"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            if include_hidden:
                cursor.execute(f"""
                    SELECT * FROM {self.table_test_cases}
                    WHERE snippet_id = %s
                    ORDER BY order_index ASC
                """, (snippet_id,))
            else:
                cursor.execute(f"""
                    SELECT * FROM {self.table_test_cases}
                    WHERE snippet_id = %s AND is_hidden = FALSE
                    ORDER BY order_index ASC
                """, (snippet_id,))
            
            return [self._row_to_test_case(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_test_cases(self, snippet_id: str, include_hidden: bool = True) -> List[Dict]:
        """Get all test cases for a snippet (alias for compatibility)"""
        return self.get_snippet_test_cases(snippet_id, include_hidden)
    
    def get_test_case(self, test_case_id: str) -> Optional[Dict]:
        """Get a specific test case by ID"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {self.table_test_cases}
                WHERE id = %s
            """, (test_case_id,))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_test_case(row)
            return None
            
        finally:
            conn.close()
    
    def update_test_case(self, test_case_id: str, name: str = None,
                         input_data: str = None, expected_output: str = None,
                         is_hidden: bool = None, order_index: int = None,
                         timeout_ms: int = None) -> bool:
        """Update a test case"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if input_data is not None:
                updates.append("input_data = %s")
                params.append(input_data)
            if expected_output is not None:
                updates.append("expected_output = %s")
                params.append(expected_output)
            if is_hidden is not None:
                updates.append("is_hidden = %s")
                params.append(is_hidden)
            if order_index is not None:
                updates.append("order_index = %s")
                params.append(order_index)
            if timeout_ms is not None:
                updates.append("timeout_ms = %s")
                params.append(timeout_ms)
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(test_case_id)
            
            cursor.execute(f"""
                UPDATE {self.table_test_cases}
                SET {', '.join(updates)}
                WHERE id = %s
            """, params)
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating test case: {e}")
            raise
        finally:
            conn.close()
    
    def delete_test_case(self, test_case_id: str) -> bool:
        """Delete a test case"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                DELETE FROM {self.table_test_cases}
                WHERE id = %s
            """, (test_case_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting test case: {e}")
            raise
        finally:
            conn.close()
    
    # =========================================================================
    # Test Result Operations
    # =========================================================================
    
    def record_test_result(self, test_case_id: str, execution_id: str,
                           passed: bool, actual_output: str,
                           execution_time_ms: int = 0,
                           error_message: str = None) -> str:
        """Record the result of a test case execution"""
        result_id = f"tres_{uuid.uuid4().hex[:12]}"
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {self.table_test_results}
                (id, test_case_id, execution_id, passed, actual_output, execution_time_ms, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (result_id, test_case_id, execution_id, passed, actual_output, 
                  execution_time_ms, error_message))
            
            conn.commit()
            return result_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error recording test result: {e}")
            raise
        finally:
            conn.close()
    
    def get_test_results_for_execution(self, execution_id: str) -> List[Dict]:
        """Get all test results for an execution"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {self.table_test_results}
                WHERE execution_id = %s
                ORDER BY created_at ASC
            """, (execution_id,))
            
            return [self._row_to_test_result(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_test_results_for_test_case(self, test_case_id: str, limit: int = 10) -> List[Dict]:
        """Get recent test results for a test case"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {self.table_test_results}
                WHERE test_case_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (test_case_id, limit))
            
            return [self._row_to_test_result(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_test_summary(self, snippet_id: str) -> Dict:
        """Get a summary of test results for all test cases of a snippet"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get the latest execution with test results
            cursor.execute(f"""
                SELECT tr.*, tc.name, tc.is_hidden
                FROM {self.table_test_results} tr
                JOIN {self.table_test_cases} tc ON tr.test_case_id = tc.id
                WHERE tc.snippet_id = %s
                ORDER BY tr.created_at DESC
            """, (snippet_id,))
            
            results = cursor.fetchall()
            
            if not results:
                return {"total": 0, "passed": 0, "failed": 0, "results": []}
            
            visible_results = [r for r in results if not r[11]]  # is_hidden at index 11
            
            passed_count = sum(1 for r in visible_results if r[4])  # passed at index 4
            failed_count = len(visible_results) - passed_count
            
            return {
                "total": len(visible_results),
                "passed": passed_count,
                "failed": failed_count,
                "pass_rate": (passed_count / len(visible_results) * 100) if visible_results else 0,
                "results": [self._row_to_test_result(r) for r in results[:10]]
            }
            
        finally:
            conn.close()
    
    # =========================================================================
    # Error Knowledge Base Operations
    # =========================================================================
    
    def get_error_suggestion(self, error_message: str, language: str = "jac") -> Optional[Dict]:
        """Find an educational suggestion for an error message"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Try exact match first, then partial matches
            cursor.execute(f"""
                SELECT * FROM {self.table_error_knowledge}
                WHERE error_pattern = %s AND (language = %s OR language = 'jac')
                LIMIT 1
            """, (error_message[:500], language))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_error_knowledge(row)
            
            # Try partial matching for common error patterns
            cursor.execute(f"""
                SELECT * FROM {self.table_error_knowledge}
                WHERE %s LIKE '%' || error_pattern || '%' AND (language = %s OR language = 'jac')
                ORDER BY LENGTH(error_pattern) DESC
                LIMIT 1
            """, (error_message[:1000], language))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_error_knowledge(row)
            
            return None
            
        finally:
            conn.close()
    
    def add_error_knowledge(self, error_pattern: str, error_type: str, title: str,
                            description: str, suggestion: str, examples: str = None,
                            documentation_link: str = None, language: str = "jac") -> str:
        """Add a new error knowledge entry"""
        knowledge_id = f"ekb_{uuid.uuid4().hex[:12]}"
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {self.table_error_knowledge}
                (id, error_pattern, error_type, title, description, suggestion, examples, documentation_link, language)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (knowledge_id, error_pattern, error_type, title, description, 
                  suggestion, examples, documentation_link, language))
            
            conn.commit()
            logger.info(f"Added error knowledge entry: {knowledge_id}")
            return knowledge_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error adding error knowledge: {e}")
            raise
        finally:
            conn.close()
    
    def get_all_error_knowledge(self, language: str = None) -> List[Dict]:
        """Get all error knowledge entries, optionally filtered by language"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            if language:
                cursor.execute(f"""
                    SELECT * FROM {self.table_error_knowledge}
                    WHERE language = %s OR language = 'jac'
                    ORDER BY error_type, title
                """, (language,))
            else:
                cursor.execute(f"""
                    SELECT * FROM {self.table_error_knowledge}
                    ORDER BY error_type, title
                """)
            
            return [self._row_to_error_knowledge(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    # =========================================================================
    # Debug Session Operations
    # =========================================================================
    
    def create_debug_session(self, user_id: int, snippet_id: str) -> str:
        """Create a new debug session"""
        session_id = f"dbg_{uuid.uuid4().hex[:12]}"
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {self.table_debug_sessions}
                (id, user_id, snippet_id, status, breakpoints, variables, call_stack)
                VALUES (%s, %s, %s, 'active', '[]', '{}', '[]')
            """, (session_id, user_id, snippet_id))
            
            conn.commit()
            logger.info(f"Created debug session: {session_id}")
            return session_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating debug session: {e}")
            raise
        finally:
            conn.close()
    
    def get_debug_session(self, session_id: str) -> Optional[Dict]:
        """Get a debug session by ID"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {self.table_debug_sessions}
                WHERE id = %s
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_debug_session(row)
            return None
            
        finally:
            conn.close()
    
    def get_active_debug_sessions(self, user_id: int) -> List[Dict]:
        """Get all active debug sessions for a user"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {self.table_debug_sessions}
                WHERE user_id = %s AND status IN ('active', 'paused')
                ORDER BY updated_at DESC
            """, (user_id,))
            
            return [self._row_to_debug_session(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_user_debug_sessions(self, user_id: int, include_completed: bool = False) -> List[Dict]:
        """Get all debug sessions for a user"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            if include_completed:
                cursor.execute(f"""
                    SELECT * FROM {self.table_debug_sessions}
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
            else:
                cursor.execute(f"""
                    SELECT * FROM {self.table_debug_sessions}
                    WHERE user_id = %s AND status IN ('active', 'paused')
                    ORDER BY created_at DESC
                """, (user_id,))
            
            return [self._row_to_debug_session(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def update_debug_session(self, session_id: str, status: str = None,
                             current_line: int = None, breakpoints: str = None,
                             variables: str = None, call_stack: str = None) -> bool:
        """Update a debug session"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if status is not None:
                updates.append("status = %s")
                params.append(status)
            if current_line is not None:
                updates.append("current_line = %s")
                params.append(current_line)
            if breakpoints is not None:
                updates.append("breakpoints = %s")
                params.append(breakpoints)
            if variables is not None:
                updates.append("variables = %s")
                params.append(variables)
            if call_stack is not None:
                updates.append("call_stack = %s")
                params.append(call_stack)
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(session_id)
            
            cursor.execute(f"""
                UPDATE {self.table_debug_sessions}
                SET {', '.join(updates)}
                WHERE id = %s
            """, params)
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating debug session: {e}")
            raise
        finally:
            conn.close()
    
    def terminate_debug_session(self, session_id: str) -> bool:
        """Terminate a debug session"""
        return self.update_debug_session(session_id, status="terminated")
    
    def add_breakpoint(self, session_id: str, line_number: int) -> Optional[Dict]:
        """Add a breakpoint to a debug session"""
        session = self.get_debug_session(session_id)
        if not session:
            return None
        
        import json
        breakpoints = json.loads(session.get("breakpoints", "[]"))
        
        if line_number not in breakpoints:
            breakpoints.append(line_number)
            breakpoints.sort()
        
        self.update_debug_session(
            session_id=session_id,
            breakpoints=json.dumps(breakpoints)
        )
        
        return self.get_debug_session(session_id)
    
    def remove_breakpoint(self, session_id: str, line_number: int) -> Optional[Dict]:
        """Remove a breakpoint from a debug session"""
        session = self.get_debug_session(session_id)
        if not session:
            return None
        
        import json
        breakpoints = json.loads(session.get("breakpoints", "[]"))
        
        if line_number in breakpoints:
            breakpoints.remove(line_number)
        
        self.update_debug_session(
            session_id=session_id,
            breakpoints=json.dumps(breakpoints)
        )
        
        return self.get_debug_session(session_id)
    
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
                cursor.execute(f"""
                    UPDATE {self.table_snippets}
                    SET folder_id = %s
                    WHERE folder_id = %s AND user_id = %s
                """, (move_contents_to, folder_id, user_id))
            
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
    
    def _row_to_version(self, row) -> Dict:
        """Convert database row to version dict"""
        return {
            "id": row[0],
            "snippet_id": row[1],
            "version_number": row[2],
            "code_content": row[3],
            "title": row[4],
            "description": row[5],
            "created_by": row[6],
            "change_summary": row[7],
            "created_at": row[8].isoformat() if row[8] else None
        }
    
    def _row_to_test_case(self, row) -> Dict:
        """Convert database row to test case dict"""
        return {
            "id": row[0],
            "snippet_id": row[1],
            "name": row[2],
            "input_data": row[3],
            "expected_output": row[4],
            "is_hidden": row[5],
            "order_index": row[6],
            "timeout_ms": row[7],
            "created_by": row[8],
            "created_at": row[9].isoformat() if row[9] else None,
            "updated_at": row[10].isoformat() if row[10] else None
        }
    
    def _row_to_test_result(self, row) -> Dict:
        """Convert database row to test result dict"""
        return {
            "id": row[0],
            "test_case_id": row[1],
            "execution_id": row[2],
            "passed": row[3],
            "actual_output": row[4],
            "execution_time_ms": row[5],
            "error_message": row[6],
            "created_at": row[7].isoformat() if row[7] else None
        }
    
    def _row_to_error_knowledge(self, row) -> Dict:
        """Convert database row to error knowledge dict"""
        return {
            "id": row[0],
            "error_pattern": row[1],
            "error_type": row[2],
            "title": row[3],
            "description": row[4],
            "suggestion": row[5],
            "examples": row[6],
            "documentation_link": row[7],
            "language": row[8],
            "created_at": row[9].isoformat() if row[9] else None,
            "updated_at": row[10].isoformat() if row[10] else None
        }
    
    def _row_to_debug_session(self, row) -> Dict:
        """Convert database row to debug session dict"""
        return {
            "id": row[0],
            "user_id": row[1],
            "snippet_id": row[2],
            "status": row[3],
            "current_line": row[4],
            "breakpoints": row[5],
            "variables": row[6],
            "call_stack": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
            "updated_at": row[9].isoformat() if row[9] else None
        }


# Singleton instance
_code_snippet_store = None

def get_code_snippet_store() -> CodeSnippetStore:
    """Get the code snippet store singleton"""
    global _code_snippet_store
    if _code_snippet_store is None:
        _code_snippet_store = CodeSnippetStore()
    return _code_snippet_store
