"""
Event Types and Models for Sync Engine

This module defines all event types used in the synchronization system.
Events represent changes to content in the source database (PostgreSQL)
that need to be propagated to the target database (Neo4j).

Event Types:
- Concept Events: CREATED, UPDATED, DELETED
- Learning Path Events: CREATED, UPDATED, DELETED
- Relationship Events: CREATED, DELETED

Each event contains:
- Event metadata (ID, type, timestamp, correlation ID)
- Entity data (the actual content being synchronized)
- Retry metadata for error handling

Author: Jeseci Development Team
"""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
import json


class EventType(str, Enum):
    """
    Enumeration of all event types in the synchronization system.
    
    Each event type corresponds to a specific operation that needs
    to be propagated from PostgreSQL to Neo4j.
    """
    
    # Concept events
    CONCEPT_CREATED = "CONCEPT_CREATED"
    CONCEPT_UPDATED = "CONCEPT_UPDATED"
    CONCEPT_DELETED = "CONCEPT_DELETED"
    
    # Learning path events
    LEARNING_PATH_CREATED = "LEARNING_PATH_CREATED"
    LEARNING_PATH_UPDATED = "LEARNING_PATH_UPDATED"
    LEARNING_PATH_DELETED = "LEARNING_PATH_DELETED"
    
    # Relationship events
    RELATIONSHIP_CREATED = "RELATIONSHIP_CREATED"
    RELATIONSHIP_DELETED = "RELATIONSHIP_DELETED"
    
    @classmethod
    def is_create_event(cls, event_type: "EventType") -> bool:
        """Check if event is a creation event"""
        return event_type in [
            cls.CONCEPT_CREATED,
            cls.LEARNING_PATH_CREATED
        ]
    
    @classmethod
    def is_update_event(cls, event_type: "EventType") -> bool:
        """Check if event is an update event"""
        return event_type in [
            cls.CONCEPT_UPDATED,
            cls.LEARNING_PATH_UPDATED
        ]
    
    @classmethod
    def is_delete_event(cls, event_type: "EventType") -> bool:
        """Check if event is a deletion event"""
        return event_type in [
            cls.CONCEPT_DELETED,
            cls.LEARNING_PATH_DELETED,
            cls.RELATIONSHIP_DELETED
        ]
    
    @classmethod
    def is_relationship_event(cls, event_type: "EventType") -> bool:
        """Check if event is a relationship event"""
        return event_type in [
            cls.RELATIONSHIP_CREATED,
            cls.RELATIONSHIP_DELETED
        ]
    
    @classmethod
    def get_entity_type(cls, event_type: "EventType") -> str:
        """Get the entity type for an event"""
        if event_type in [cls.CONCEPT_CREATED, cls.CONCEPT_UPDATED, cls.CONCEPT_DELETED]:
            return "concept"
        elif event_type in [cls.LEARNING_PATH_CREATED, cls.LEARNING_PATH_UPDATED, cls.LEARNING_PATH_DELETED]:
            return "learning_path"
        elif event_type in [cls.RELATIONSHIP_CREATED, cls.RELATIONSHIP_DELETED]:
            return "relationship"
        return "unknown"


@dataclass
class SyncEvent:
    """
    Represents a synchronization event.
    
    This is the core data structure used throughout the sync engine.
    Events are created when data changes in PostgreSQL and are
    published to Redis for asynchronous processing.
    
    Attributes:
        event_id: Unique identifier for this event (UUID)
        correlation_id: ID for tracing related events across services
        event_type: Type of event (creation, update, deletion)
        entity_id: ID of the entity being synchronized
        entity_type: Type of entity (concept, learning_path, relationship)
        timestamp: Unix timestamp when event was created
        payload: Event data (serialized entity data)
        source_version: Version/timestamp of source data for conflict detection
        retry_count: Number of processing attempts
        max_retries: Maximum allowed retry attempts
        error_message: Error message if processing failed
        created_at: Human-readable creation timestamp
        updated_at: Human-readable last update timestamp
    """
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.CONCEPT_CREATED
    entity_id: str = ""
    entity_type: str = "concept"
    timestamp: int = field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    payload: Dict[str, Any] = field(default_factory=dict)
    source_version: int = field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        """Validate and set defaults after initialization"""
        if not self.entity_id and self.payload:
            self.entity_id = self.payload.get("concept_id") or self.payload.get("path_id") or self.payload.get("name", "")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "correlation_id": self.correlation_id,
            "event_type": self.event_type.value if isinstance(self.event_type, EventType) else self.event_type,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "source_version": self.source_version,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncEvent":
        """Create event from dictionary"""
        event_type = data.get("event_type", "CONCEPT_CREATED")
        if isinstance(event_type, str):
            event_type = EventType(event_type)
        
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
            event_type=event_type,
            entity_id=data.get("entity_id", ""),
            entity_type=data.get("entity_type", "concept"),
            timestamp=data.get("timestamp", int(datetime.utcnow().timestamp())),
            payload=data.get("payload", {}),
            source_version=data.get("source_version", int(datetime.utcnow().timestamp())),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            error_message=data.get("error_message"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat())
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "SyncEvent":
        """Create event from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def should_retry(self) -> bool:
        """Check if event should be retried"""
        return self.retry_count < self.max_retries
    
    def increment_retry(self, error_message: str):
        """Increment retry count and set error message"""
        self.retry_count += 1
        self.error_message = error_message
        self.updated_at = datetime.utcnow().isoformat()
    
    def mark_completed(self):
        """Mark event as successfully processed"""
        self.error_message = None
        self.updated_at = datetime.utcnow().isoformat()
    
    def mark_failed(self, error_message: str):
        """Mark event as permanently failed"""
        self.error_message = error_message
        self.updated_at = datetime.utcnow().isoformat()
    
    def get_redis_fields(self) -> Dict[str, str]:
        """Get fields for Redis stream entry"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value if isinstance(self.event_type, EventType) else self.event_type,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "data": self.to_json()
        }
    
    @staticmethod
    def create_concept_event(concept_data: Dict[str, Any], event_type: EventType = EventType.CONCEPT_CREATED) -> "SyncEvent":
        """
        Factory method to create a concept synchronization event.
        
        Args:
            concept_data: Concept data from PostgreSQL
            event_type: Type of event (created, updated, deleted)
            
        Returns:
            SyncEvent configured for concept synchronization
        """
        entity_id = concept_data.get("concept_id", concept_data.get("name", ""))
        
        return SyncEvent(
            event_type=event_type,
            entity_id=entity_id,
            entity_type="concept",
            payload=concept_data,
            source_version=int(datetime.utcnow().timestamp())
        )
    
    @staticmethod
    def create_learning_path_event(path_data: Dict[str, Any], event_type: EventType = EventType.LEARNING_PATH_CREATED) -> "SyncEvent":
        """
        Factory method to create a learning path synchronization event.
        
        Args:
            path_data: Learning path data from PostgreSQL
            event_type: Type of event (created, updated, deleted)
            
        Returns:
            SyncEvent configured for learning path synchronization
        """
        entity_id = path_data.get("path_id", path_data.get("name", ""))
        
        return SyncEvent(
            event_type=event_type,
            entity_id=entity_id,
            entity_type="learning_path",
            payload=path_data,
            source_version=int(datetime.utcnow().timestamp())
        )
    
    @staticmethod
    def create_relationship_event(
        relationship_data: Dict[str, Any], 
        event_type: EventType = EventType.RELATIONSHIP_CREATED
    ) -> "SyncEvent":
        """
        Factory method to create a relationship synchronization event.
        
        Args:
            relationship_data: Relationship data (source, target, type)
            event_type: Type of event (created, deleted)
            
        Returns:
            SyncEvent configured for relationship synchronization
        """
        entity_id = f"{relationship_data.get('from', '')}->{relationship_data.get('to', '')}"
        
        return SyncEvent(
            event_type=event_type,
            entity_id=entity_id,
            entity_type="relationship",
            payload=relationship_data,
            source_version=int(datetime.utcnow().timestamp())
        )


@dataclass
class EventBatch:
    """
    Represents a batch of events for processing.
    
    Batches are used to improve processing efficiency by handling
    multiple events together rather than one at a time.
    """
    
    events: list[SyncEvent] = field(default_factory=list)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def add_event(self, event: SyncEvent):
        """Add event to batch"""
        self.events.append(event)
    
    def is_empty(self) -> bool:
        """Check if batch is empty"""
        return len(self.events) == 0
    
    def size(self) -> int:
        """Get number of events in batch"""
        return len(self.events)
    
    def clear(self):
        """Clear all events from batch"""
        self.events.clear()
    
    def get_events_by_type(self, event_type: EventType) -> list[SyncEvent]:
        """Get all events of a specific type"""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_events_by_entity(self, entity_type: str) -> list[SyncEvent]:
        """Get all events for a specific entity type"""
        return [e for e in self.events if e.entity_type == entity_type]
