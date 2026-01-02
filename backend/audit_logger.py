#!/usr/bin/env python3
"""
Audit Logger - Comprehensive audit logging for all database operations

This module provides functions to log all database changes (CREATE, UPDATE, DELETE)
to the audit_log table without overwriting. Each action is recorded as a separate row.

Usage:
    from audit_logger import log_create, log_update, log_delete
    
    # Log a create operation
    log_create(
        table_name="users",
        record_id="user_123",
        new_values={"username": "john", "email": "john@example.com"},
        performed_by="admin_user",
        request_id="req_456"
    )
    
    # Log an update operation (captures what changed)
    log_update(
        table_name="users",
        record_id="user_123",
        old_values={"username": "john", "email": "john@example.com"},
        new_values={"username": "john_doe", "email": "john@example.com"},
        performed_by="admin_user"
    )
    
    # Log a delete operation
    log_delete(
        table_name="users",
        record_id="user_123",
        old_values={"username": "john", "email": "john@example.com"},
        performed_by="admin_user"
    )
"""

import os
import sys
import uuid
import json
import datetime
import logging
from typing import Optional, Dict, Any, List

# Set up logging
logger = logging.getLogger(__name__)

# Import database utilities
sys.path.insert(0, os.path.dirname(__file__))
from database import get_postgres_manager

# Table name mappings for cleaner display
TABLE_DISPLAY_NAMES = {
    "jeseci_academy.users": "Users",
    "jeseci_academy.user_profile": "User Profile",
    "jeseci_academy.courses": "Courses",
    "jeseci_academy.learning_paths": "Learning Paths",
    "jeseci_academy.quizzes": "Quizzes",
    "jeseci_academy.concepts": "Concepts",
    "jeseci_academy.lessons": "Lessons",
    "jeseci_academy.user_learning_preferences": "User Learning Preferences",
    "jeseci_academy.quiz_attempts": "Quiz Attempts",
    "jeseci_academy.user_concept_progress": "User Concept Progress",
    "jeseci_academy.user_learning_paths": "User Learning Paths",
    "jeseci_academy.achievements": "Achievements",
    "jeseci_academy.user_achievements": "User Achievements",
    "jeseci_academy.badges": "Badges",
    "jeseci_academy.user_badges": "User Badges",
}

# Tables that should have audit logging
AUDITED_TABLES = [
    "users",
    "user_profile",
    "courses",
    "learning_paths",
    "quizzes",
    "concepts",
    "lessons",
    "user_learning_preferences",
    "quiz_attempts",
    "user_concept_progress",
    "user_learning_paths",
    "achievements",
    "user_achievements",
    "badges",
    "user_badges",
]


def generate_audit_id() -> str:
    """Generate a unique audit ID"""
    return f"audit_{uuid.uuid4().hex[:32]}"


def get_current_timestamp() -> datetime.datetime:
    """Get current timestamp"""
    return datetime.datetime.now()


def should_audit_table(table_name: str) -> bool:
    """Check if a table should be audited"""
    # Extract just the table name from full path
    short_name = table_name.split(".")[-1] if "." in table_name else table_name
    return short_name.lower() in [t.lower() for t in AUDITED_TABLES]


def get_changed_fields(old_values: Dict[str, Any], new_values: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Identify which fields changed between old and new values"""
    changed = {}
    
    if old_values is None:
        old_values = {}
    if new_values is None:
        new_values = {}
    
    # Check all keys in new_values
    for key in new_values.keys():
        old_val = old_values.get(key)
        new_val = new_values.get(key)
        
        # Handle None vs empty string, None vs 0, etc.
        old_str = str(old_val) if old_val is not None else None
        new_str = str(new_val) if new_val is not None else None
        
        if old_str != new_str:
            changed[key] = {
                "old": old_val,
                "new": new_val
            }
    
    # Also check for keys that were removed
    for key in old_values.keys():
        if key not in new_values:
            changed[key] = {
                "old": old_values.get(key),
                "new": None
            }
    
    return changed


def log_action(
    table_name: str,
    record_id: str,
    action_type: str,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    performed_by: Optional[str] = None,
    performed_by_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
    session_id: Optional[str] = None,
    application_source: str = "admin_panel",
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Log a database action to the audit_log table
    
    Args:
        table_name: Name of the table that was modified
        record_id: Primary key value of the record that was modified
        action_type: Type of action - CREATE, UPDATE, or DELETE
        old_values: Values before the change (for UPDATE/DELETE)
        new_values: Values after the change (for CREATE/UPDATE)
        performed_by: Username of the user who performed the action
        performed_by_id: User ID of the user who performed the action
        ip_address: IP address of the request (for security)
        user_agent: User agent string from the request
        request_id: Optional request ID for tracing
        session_id: Optional session ID
        application_source: Source of the action (admin_panel, api, system, etc.)
        additional_context: Any additional context information
    
    Returns:
        Dict with success status and audit_id
    """
    # Check if we should audit this table
    if not should_audit_table(table_name):
        return {"success": True, "skipped": True, "reason": "Table not audited"}
    
    pg_manager = get_postgres_manager()
    
    # Generate audit ID and timestamp
    audit_id = generate_audit_id()
    created_at = get_current_timestamp()
    
    # Calculate changed fields for UPDATE operations
    changed_fields = None
    if action_type.upper() == "UPDATE" and old_values and new_values:
        changed_fields = get_changed_fields(old_values, new_values)
        # Only log UPDATE if something actually changed
        if not changed_fields:
            return {"success": True, "skipped": True, "reason": "No fields changed"}
    
    # Prepare values for JSON storage
    old_values_json = json.dumps(old_values) if old_values else None
    new_values_json = json.dumps(new_values) if new_values else None
    changed_fields_json = json.dumps(changed_fields) if changed_fields else None
    additional_context_json = json.dumps(additional_context) if additional_context else None
    
    insert_query = f"""
    INSERT INTO {pg_manager.schema}.audit_log (
        audit_id,
        table_name,
        record_id,
        action_type,
        old_values,
        new_values,
        changed_fields,
        performed_by,
        performed_by_id,
        ip_address,
        user_agent,
        request_id,
        session_id,
        application_source,
        additional_context,
        created_at
    ) VALUES (
        %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s
    )
    """
    
    try:
        result = pg_manager.execute_query(
            insert_query,
            (
                audit_id,
                table_name,
                record_id,
                action_type.upper(),
                old_values_json,
                new_values_json,
                changed_fields_json,
                performed_by,
                performed_by_id,
                ip_address,
                user_agent,
                request_id,
                session_id,
                application_source,
                additional_context_json,
                created_at
            ),
            fetch=False
        )
        
        logger.info(f"Audit log created: {action_type} on {table_name}.{record_id} by {performed_by}")
        
        return {
            "success": True,
            "audit_id": audit_id,
            "action": action_type.upper(),
            "table": table_name,
            "record_id": record_id,
            "performed_by": performed_by,
            "created_at": created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        # Don't fail the main operation if audit logging fails
        return {
            "success": False,
            "error": str(e),
            "audit_id": audit_id
        }


def log_create(
    table_name: str,
    record_id: str,
    new_values: Dict[str, Any],
    performed_by: Optional[str] = None,
    performed_by_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Log a CREATE operation"""
    return log_action(
        table_name=table_name,
        record_id=record_id,
        action_type="CREATE",
        old_values=None,
        new_values=new_values,
        performed_by=performed_by,
        performed_by_id=performed_by_id,
        **kwargs
    )


def log_update(
    table_name: str,
    record_id: str,
    old_values: Dict[str, Any],
    new_values: Dict[str, Any],
    performed_by: Optional[str] = None,
    performed_by_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Log an UPDATE operation - only logs if fields actually changed"""
    return log_action(
        table_name=table_name,
        record_id=record_id,
        action_type="UPDATE",
        old_values=old_values,
        new_values=new_values,
        performed_by=performed_by,
        performed_by_id=performed_by_id,
        **kwargs
    )


def log_delete(
    table_name: str,
    record_id: str,
    old_values: Dict[str, Any],
    performed_by: Optional[str] = None,
    performed_by_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Log a DELETE operation"""
    return log_action(
        table_name=table_name,
        record_id=record_id,
        action_type="DELETE",
        old_values=old_values,
        new_values=None,
        performed_by=performed_by,
        performed_by_id=performed_by_id,
        **kwargs
    )


def get_audit_history(
    table_name: str,
    record_id: str,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get the complete audit history for a specific record
    
    Args:
        table_name: Name of the table
        record_id: Primary key value of the record
        limit: Maximum number of records to return
    
    Returns:
        List of audit log entries ordered by creation time (newest first)
    """
    pg_manager = get_postgres_manager()
    
    query = f"""
    SELECT 
        audit_id,
        table_name,
        record_id,
        action_type,
        old_values,
        new_values,
        changed_fields,
        performed_by,
        performed_by_id,
        ip_address,
        created_at,
        application_source
    FROM {pg_manager.schema}.audit_log
    WHERE table_name = %s AND record_id = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    
    try:
        result = pg_manager.execute_query(query, (table_name, record_id, limit))
        
        history = []
        for row in result or []:
            history.append({
                "audit_id": row.get('audit_id'),
                "action": row.get('action_type'),
                "performed_by": row.get('performed_by'),
                "performed_by_id": row.get('performed_by_id'),
                "ip_address": str(row.get('ip_address')) if row.get('ip_address') else None,
                "old_values": row.get('old_values'),
                "new_values": row.get('new_values'),
                "changed_fields": row.get('changed_fields'),
                "application_source": row.get('application_source'),
                "timestamp": row.get('created_at').isoformat() if row.get('created_at') else None
            })
        
        return history
        
    except Exception as e:
        logger.error(f"Failed to get audit history: {e}")
        return []


def get_user_activity_log(
    performed_by: str,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get all audit entries for a specific user
    
    Args:
        performed_by: Username to filter by
        limit: Maximum number of records to return
    
    Returns:
        List of audit log entries
    """
    pg_manager = get_postgres_manager()
    
    query = f"""
    SELECT 
        audit_id,
        table_name,
        record_id,
        action_type,
        changed_fields,
        performed_by,
        ip_address,
        created_at,
        application_source
    FROM {pg_manager.schema}.audit_log
    WHERE performed_by = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    
    try:
        result = pg_manager.execute_query(query, (performed_by, limit))
        
        activity = []
        for row in result or []:
            activity.append({
                "audit_id": row.get('audit_id'),
                "table": row.get('table_name'),
                "record_id": row.get('record_id'),
                "action": row.get('action_type'),
                "changed_fields": row.get('changed_fields'),
                "ip_address": str(row.get('ip_address')) if row.get('ip_address') else None,
                "source": row.get('application_source'),
                "timestamp": row.get('created_at').isoformat() if row.get('created_at') else None
            })
        
        return activity
        
    except Exception as e:
        logger.error(f"Failed to get user activity log: {e}")
        return []


def get_table_activity_summary(
    table_name: str,
    days: int = 7
) -> Dict[str, Any]:
    """Get activity summary for a table over the last N days
    
    Args:
        table_name: Name of the table
        days: Number of days to look back
    
    Returns:
        Dict with action counts and recent activity
    """
    pg_manager = get_postgres_manager()
    
    query = f"""
    SELECT 
        action_type,
        COUNT(*) as count,
        COUNT(DISTINCT performed_by) as unique_users
    FROM {pg_manager.schema}.audit_log
    WHERE table_name = %s AND created_at >= NOW() - INTERVAL '%s days'
    GROUP BY action_type
    """
    
    try:
        result = pg_manager.execute_query(query, (table_name, days))
        
        summary = {
            "table": table_name,
            "period_days": days,
            "actions": {},
            "total_operations": 0,
            "unique_users": 0
        }
        
        total_ops = 0
        unique_users = set()
        
        for row in result or []:
            action = row.get('action_type')
            count = row.get('count')
            users = row.get('unique_users')
            
            summary["actions"][action] = {
                "count": count,
                "unique_users": users
            }
            
            total_ops += count
            if users:
                unique_users.add(users)
        
        summary["total_operations"] = total_ops
        summary["unique_users"] = len(unique_users) if unique_users else 0
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get table activity summary: {e}")
        return {"error": str(e)}


def search_audit_logs(
    table_name: Optional[str] = None,
    action_type: Optional[str] = None,
    performed_by: Optional[str] = None,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """Search audit logs with various filters
    
    Args:
        table_name: Filter by table name
        action_type: Filter by action type (CREATE, UPDATE, DELETE)
        performed_by: Filter by user who performed the action
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Maximum records to return
        offset: Offset for pagination
    
    Returns:
        Dict with results and pagination info
    """
    pg_manager = get_postgres_manager()
    
    conditions = []
    params = []
    
    if table_name:
        conditions.append("table_name = %s")
        params.append(table_name)
    
    if action_type:
        conditions.append("action_type = %s")
        params.append(action_type.upper())
    
    if performed_by:
        conditions.append("performed_by ILIKE %s")
        params.append(f"%{performed_by}%")
    
    if start_date:
        conditions.append("created_at >= %s")
        params.append(start_date)
    
    if end_date:
        conditions.append("created_at <= %s")
        params.append(end_date)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Count total records
    count_query = f"SELECT COUNT(*) as total FROM {pg_manager.schema}.audit_log WHERE {where_clause}"
    
    # Get records
    query = f"""
    SELECT 
        audit_id,
        table_name,
        record_id,
        action_type,
        changed_fields,
        performed_by,
        performed_by_id,
        ip_address,
        created_at,
        application_source
    FROM {pg_manager.schema}.audit_log
    WHERE {where_clause}
    ORDER BY created_at DESC
    LIMIT %s OFFSET %s
    """
    
    params.extend([limit, offset])
    
    try:
        # Get total count
        count_result = pg_manager.execute_query(count_query, params[:-2])
        total = count_result[0].get('total') if count_result else 0
        
        # Get records
        result = pg_manager.execute_query(query, params)
        
        logs = []
        for row in result or []:
            logs.append({
                "audit_id": row.get('audit_id'),
                "table": row.get('table_name'),
                "record_id": row.get('record_id'),
                "action": row.get('action_type'),
                "changed_fields": row.get('changed_fields'),
                "performed_by": row.get('performed_by'),
                "performed_by_id": row.get('performed_by_id'),
                "ip_address": str(row.get('ip_address')) if row.get('ip_address') else None,
                "source": row.get('application_source'),
                "timestamp": row.get('created_at').isoformat() if row.get('created_at') else None
            })
        
        return {
            "success": True,
            "logs": logs,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
        
    except Exception as e:
        logger.error(f"Failed to search audit logs: {e}")
        return {"success": False, "error": str(e), "logs": [], "total": 0}


# Convenience function for soft delete operations
def log_soft_delete(
    table_name: str,
    record_id: str,
    old_values: Dict[str, Any],
    performed_by: str,
    reason: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Log a soft delete operation (UPDATE with is_deleted=true)
    
    This is a specialized log for soft deletes that captures the deletion
    context including the reason if provided.
    """
    # Create new values with is_deleted=true
    new_values = old_values.copy()
    new_values['is_deleted'] = True
    
    # Add deletion context to additional_context
    context = kwargs.get('additional_context', {}) or {}
    context['deletion_reason'] = reason
    context['is_soft_delete'] = True
    kwargs['additional_context'] = context
    
    return log_action(
        table_name=table_name,
        record_id=record_id,
        action_type="SOFT_DELETE",
        old_values=old_values,
        new_values=new_values,
        performed_by=performed_by,
        **kwargs
    )


# Convenience function for restore operations
def log_restore(
    table_name: str,
    record_id: str,
    old_values: Dict[str, Any],
    performed_by: str,
    **kwargs
) -> Dict[str, Any]:
    """Log a restore operation (UPDATE with is_deleted=false)"""
    # Create new values with is_deleted=false
    new_values = old_values.copy()
    new_values['is_deleted'] = False
    
    # Add restore context
    context = kwargs.get('additional_context', {}) or {}
    context['is_restore'] = True
    kwargs['additional_context'] = context
    
    return log_action(
        table_name=table_name,
        record_id=record_id,
        action_type="RESTORE",
        old_values=old_values,
        new_values=new_values,
        performed_by=performed_by,
        **kwargs
    )
