"""
Event Publisher for Sync Engine

This module provides the event publisher that publishes synchronization events
to Redis streams. It implements the outbox pattern for reliable event delivery,
ensuring no events are lost even if publishing fails.

The publisher:
1. Writes events to the sync_event_log table (PostgreSQL)
2. Publishes events to Redis stream
3. Updates event status after successful publication

Author: Jeseci Development Team
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

import redis

from .config import get_redis_config, get_sync_config
from .events import SyncEvent, EventType
from .models import SyncEventLog, SyncEventStatus
from .database import get_postgres_sync_manager, get_redis_sync_manager

logger = logging.getLogger(__name__)


class SyncEventPublisher:
    """
    Publishes synchronization events to Redis streams.
    
    This class implements the reliable event publishing pattern:
    1. Create event in database (outbox)
    2. Publish to message queue
    3. Update status
    
    This ensures events are never lost even if publishing fails.
    """
    
    def __init__(self):
        self.redis_config = get_redis_config()
        self.sync_config = get_sync_config()
        self.redis_client = None
        self.postgres_manager = None
        self._initialize()
    
    def _initialize(self):
        """Initialize publisher connections"""
        redis_manager = get_redis_sync_manager()
        self.redis_client = redis_manager.get_client()
        self.postgres_manager = get_postgres_sync_manager()
        
        # Ensure stream and consumer group exist
        redis_manager.create_stream_with_group(
            self.redis_config.stream_name,
            self.redis_config.consumer_group
        )
        
        logger.info(f"SyncEventPublisher initialized with stream: {self.redis_config.stream_name}")
    
    @contextmanager
    def get_session(self):
        """Get database session"""
        with self.postgres_manager.get_session() as session:
            yield session
    
    def create_event(
        self,
        event_type: EventType,
        entity_id: str,
        entity_type: str,
        payload: Dict[str, Any],
        source_version: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> SyncEvent:
        """
        Create a new synchronization event.
        
        This method creates an event in the database (outbox pattern)
        and returns the event object. The event is not yet published
        to the message queue.
        
        Args:
            event_type: Type of event (create, update, delete)
            entity_id: ID of the entity being synchronized
            entity_type: Type of entity (concept, learning_path, relationship)
            payload: Event data to synchronize
            source_version: Version of source data for conflict detection
            correlation_id: ID for tracing related events
            
        Returns:
            SyncEvent object that was created
        """
        if source_version is None:
            source_version = int(datetime.utcnow().timestamp())
        
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        # Create event object
        event = SyncEvent(
            event_type=event_type,
            entity_id=entity_id,
            entity_type=entity_type,
            payload=payload,
            source_version=source_version,
            correlation_id=correlation_id,
            max_retries=self.sync_config.max_retries
        )
        
        # Save to database (outbox)
        with self.get_session() as session:
            event_log = SyncEventLog(
                event_id=event.event_id,
                correlation_id=event.correlation_id,
                event_type=event.event_type.value,
                entity_id=event.entity_id,
                entity_type=event.entity_type,
                payload=event.payload,
                source_version=event.source_version,
                status=SyncEventStatus.PENDING,
                max_retries=event.max_retries
            )
            session.add(event_log)
            session.flush()  # Get the ID without committing
        
        logger.debug(f"Created sync event: {event.event_id} ({event.event_type.value})")
        return event
    
    def publish_event(self, event: SyncEvent) -> bool:
        """
        Publish an event to Redis stream.
        
        This method publishes the event to the Redis stream and updates
        its status in the database. It implements retry logic for
        transient failures.
        
        Args:
            event: Event to publish
            
        Returns:
            True if published successfully, False otherwise
        """
        if self.redis_client is None:
            logger.error("Redis client not available")
            return False
        
        try:
            # Publish to Redis stream
            message_id = self.redis_client.xadd(
                self.redis_config.stream_name,
                event.get_redis_fields(),
                maxlen=10000,  # Limit stream size
                approximate=True
            )
            
            # Update status in database
            with self.get_session() as session:
                event_log = session.query(SyncEventLog).filter(
                    SyncEventLog.event_id == event.event_id
                ).first()
                
                if event_log:
                    event_log.mark_published(message_id)
                
                session.flush()
            
            logger.info(f"Published sync event: {event.event_id} -> Redis ({message_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_id}: {e}")
            self._update_event_error(event.event_id, str(e))
            return False
    
    def publish_concept(
        self,
        concept_data: Dict[str, Any],
        event_type: EventType = EventType.CONCEPT_CREATED
    ) -> bool:
        """
        Convenience method to publish a concept synchronization event.
        
        Args:
            concept_data: Concept data from PostgreSQL
            event_type: Type of event (create, update, delete)
            
        Returns:
            True if published successfully, False otherwise
        """
        entity_id = concept_data.get("concept_id", concept_data.get("name", ""))
        
        event = self.create_event(
            event_type=event_type,
            entity_id=entity_id,
            entity_type="concept",
            payload=concept_data
        )
        
        return self.publish_event(event)
    
    def publish_learning_path(
        self,
        path_data: Dict[str, Any],
        event_type: EventType = EventType.LEARNING_PATH_CREATED
    ) -> bool:
        """
        Convenience method to publish a learning path synchronization event.
        
        Args:
            path_data: Learning path data from PostgreSQL
            event_type: Type of event (create, update, delete)
            
        Returns:
            True if published successfully, False otherwise
        """
        entity_id = path_data.get("path_id", path_data.get("name", ""))
        
        event = self.create_event(
            event_type=event_type,
            entity_id=entity_id,
            entity_type="learning_path",
            payload=path_data
        )
        
        return self.publish_event(event)
    
    def publish_relationship(
        self,
        relationship_data: Dict[str, Any],
        event_type: EventType = EventType.RELATIONSHIP_CREATED
    ) -> bool:
        """
        Convenience method to publish a relationship synchronization event.
        
        Args:
            relationship_data: Relationship data (from, to, type)
            event_type: Type of event (create, delete)
            
        Returns:
            True if published successfully, False otherwise
        """
        entity_id = f"{relationship_data.get('from', '')}->{relationship_data.get('to', '')}"
        
        event = self.create_event(
            event_type=event_type,
            entity_id=entity_id,
            entity_type="relationship",
            payload=relationship_data
        )
        
        return self.publish_event(event)
    
    def _update_event_error(self, event_id: str, error_message: str):
        """Update event status with error message"""
        with self.get_session() as session:
            event_log = session.query(SyncEventLog).filter(
                SyncEventLog.event_id == event_id
            ).first()
            
            if event_log:
                event_log.mark_failed(error_message)
                session.flush()
    
    def retry_pending_events(self, limit: int = 100) -> int:
        """
        Retry events that are stuck in PENDING or PUBLISHED status.
        
        This method finds events that haven't been successfully processed
        and attempts to republish them.
        
        Args:
            limit: Maximum number of events to retry
            
        Returns:
            Number of events retried
        """
        with self.get_session() as session:
            # Find pending/published events
            stuck_events = session.query(SyncEventLog).filter(
                SyncEventLog.status.in_([
                    SyncEventStatus.PENDING,
                    SyncEventStatus.PUBLISHED
                ]),
                SyncEventLog.retry_count < SyncEventLog.max_retries
            ).limit(limit).all()
            
            retried = 0
            for event_log in stuck_events:
                try:
                    # Increment retry count
                    event_log.increment_retry()
                    
                    # Convert to event and republish
                    event = event_log.to_event()
                    if self.publish_event(event):
                        retried += 1
                        
                except Exception as e:
                    logger.error(f"Failed to retry event {event_log.event_id}: {e}")
            
            return retried
    
    def get_pending_events(self, limit: int = 100) -> List[SyncEventLog]:
        """
        Get pending events for processing.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of pending sync event logs
        """
        with self.get_session() as session:
            events = session.query(SyncEventLog).filter(
                SyncEventLog.status == SyncEventStatus.PENDING
            ).order_by(
                SyncEventLog.created_at.asc()
            ).limit(limit).all()
            
            return events
    
    def get_event_status(self, event_id: str) -> Optional[SyncEventLog]:
        """
        Get the status of an event.
        
        Args:
            event_id: ID of the event to check
            
        Returns:
            SyncEventLog if found, None otherwise
        """
        with self.get_session() as session:
            return session.query(SyncEventLog).filter(
                SyncEventLog.event_id == event_id
            ).first()
    
    def mark_event_completed(self, event_id: str):
        """Mark an event as completed"""
        with self.get_session() as session:
            event_log = session.query(SyncEventLog).filter(
                SyncEventLog.event_id == event_id
            ).first()
            
            if event_log:
                event_log.mark_completed()
                session.flush()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get publishing statistics.
        
        Returns:
            Dictionary with event counts by status
        """
        with self.get_session() as session:
            stats = {}
            for status in SyncEventStatus:
                count = session.query(SyncEventLog).filter(
                    SyncEventLog.status == status
                ).count()
                stats[status.value] = count
            
            return stats
    
    def close(self):
        """Close publisher connections"""
        if self.redis_client:
            self.redis_client.close()
            self.redis_client = None
        logger.info("SyncEventPublisher closed")


# Global publisher instance
_publisher_instance: Optional[SyncEventPublisher] = None


def get_sync_publisher() -> SyncEventPublisher:
    """Get the global sync event publisher instance"""
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = SyncEventPublisher()
    return _publisher_instance


def publish_concept_event(
    concept_data: Dict[str, Any],
    event_type: EventType = EventType.CONCEPT_CREATED
) -> bool:
    """
    Convenience function to publish a concept event.
    
    Args:
        concept_data: Concept data to synchronize
        event_type: Type of event
        
    Returns:
        True if published successfully
    """
    publisher = get_sync_publisher()
    return publisher.publish_concept(concept_data, event_type)


def publish_learning_path_event(
    path_data: Dict[str, Any],
    event_type: EventType = EventType.LEARNING_PATH_CREATED
) -> bool:
    """
    Convenience function to publish a learning path event.
    
    Args:
        path_data: Learning path data to synchronize
        event_type: Type of event
        
    Returns:
        True if published successfully
    """
    publisher = get_sync_publisher()
    return publisher.publish_learning_path(path_data, event_type)


def publish_relationship_event(
    relationship_data: Dict[str, Any],
    event_type: EventType = EventType.RELATIONSHIP_CREATED
) -> bool:
    """
    Convenience function to publish a relationship event.
    
    Args:
        relationship_data: Relationship data to synchronize
        event_type: Type of event
        
    Returns:
        True if published successfully
    """
    publisher = get_sync_publisher()
    return publisher.publish_relationship(relationship_data, event_type)
