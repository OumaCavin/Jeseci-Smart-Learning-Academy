#!/usr/bin/env python3
"""
Event-Driven Sync Engine for Jeseci Smart Learning Academy

This module provides event-driven synchronization between PostgreSQL and Neo4j
using Redis as the message queue. It ensures eventual consistency while
maintaining loose coupling between databases.

The system implements:
- Event publishing when content changes in PostgreSQL
- Asynchronous consumers that update Neo4j based on events
- Sync status tracking for audit and debugging
- Conflict detection and resolution
- Background reconciliation to repair inconsistencies

Author: Jeseci Development Team
License: MIT License
"""

import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

__version__ = "1.0.0"
__author__ = "Jeseci Development Team"

from .config import get_redis_config, get_sync_config
from .events import (
    EventType,
    SyncEvent,
    create_concept_event,
    create_learning_path_event,
    create_relationship_event
)
from .publisher import SyncEventPublisher
from .consumer import SyncEventConsumer
from .reconciliation import ReconciliationJob

__all__ = [
    'EventType',
    'SyncEvent',
    'SyncEventPublisher',
    'SyncEventConsumer',
    'ReconciliationJob',
    'get_redis_config',
    'get_sync_config',
    'create_concept_event',
    'create_learning_path_event',
    'create_relationship_event'
]
