#!/usr/bin/env python3
"""
Request Context Module

This module provides context access for Jaclang walkers.
It stores request context (like user_id from JWT tokens) that can be
accessed by walkers during execution.

Author: Cavin Otieno
"""

import threading
from typing import Dict, Any, Optional

# Thread-local storage for request context
_context_local = threading.local()

def set_context(context: Dict[str, Any]) -> None:
    """
    Set the request context for the current thread.
    This should be called before spawning walkers.
    
    Args:
        context: Dictionary containing request context (e.g., user_id, session info)
    """
    _context_local.context = context

def get_context() -> Dict[str, Any]:
    """
    Get the request context for the current thread.
    Returns an empty dict if no context has been set.
    
    Returns:
        Dictionary containing request context
    """
    return getattr(_context_local, 'context', {})

def get_user_id() -> Optional[str]:
    """
    Get the user_id from the current context.
    Returns None if no user_id is available.
    
    Returns:
        User ID string or None
    """
    context = get_context()
    return context.get('user_id')

def clear_context() -> None:
    """
    Clear the request context for the current thread.
    This should be called after request processing is complete.
    """
    if hasattr(_context_local, 'context'):
        del _context_local.context

def require_auth() -> str:
    """
    Get the user_id from context, raising an error if not authenticated.
    
    Returns:
        User ID string
        
    Raises:
        ValueError: If no user context is available
    """
    user_id = get_user_id()
    if not user_id:
        raise ValueError("Authentication required. No user context available.")
    return user_id

def get_user_id_safe() -> Optional[str]:
    """
    Get user_id from context safely.
    Returns None if context is not set instead of raising an error.
    This is the safe version for use in walkers that may be called
    without authentication context.
    
    Returns:
        User ID string or None
    """
    try:
        return get_user_id()
    except (AttributeError, TypeError):
        return None

# Convenience function for Jaclang walkers
def ctx() -> Dict[str, Any]:
    """
    Convenience function for Jaclang walkers to access request context.
    This function can be called from Jaclang code.
    Returns an empty dict if context is not set.
    
    Returns:
        Dictionary containing request context
    """
    try:
        return get_context()
    except (AttributeError, TypeError):
        return {}
