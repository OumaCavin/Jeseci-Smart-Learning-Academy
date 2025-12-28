"""
Event Consumer for Sync Engine

This module provides the event consumer that processes synchronization events
from Redis streams and applies changes to Neo4j. The consumer implements:
- Idempotent event processing
- Conflict detection
- Retry logic with exponential backoff
- Error handling and dead letter queue

Author: Jeseci Development Team
"""

import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager

import redis

from backend.sync_engine.config import get_redis_config, get_sync_config
from backend.sync_engine.events import SyncEvent, EventType
from backend.sync_engine.models import SyncEventLog, SyncEventStatus, SyncStatus
from backend.sync_engine.database import get_postgres_sync_manager, get_neo4j_sync_manager, get_redis_sync_manager

# Import centralized logging configuration
from logger_config import logger


class SyncEventConsumer:
    """
    Consumes and processes synchronization events from Redis streams.
    
    This class:
    1. Reads events from Redis stream consumer group
    2. Validates and processes events
    3. Updates Neo4j based on event data
    4. Updates event status in PostgreSQL
    5. Implements retry logic for failed events
    
    The consumer is designed to run as a long-running process, typically
    in a separate worker container or process.
    """
    
    def __init__(self, consumer_name: Optional[str] = None):
        self.redis_config = get_redis_config()
        self.sync_config = get_sync_config()
        
        # Consumer identification
        if consumer_name is None:
            import socket
            consumer_name = f"consumer-{socket.gethostname()}-{threading.current_thread().ident}"
        self.consumer_name = consumer_name
        
        # Managers
        self.redis_manager = get_redis_sync_manager()
        self.postgres_manager = get_postgres_sync_manager()
        self.neo4j_manager = get_neo4j_sync_manager()
        
        # State
        self.running = False
        self.redis_client = None
        self._processing_lock = threading.Lock()
        
        # Statistics
        self.events_processed = 0
        self.events_failed = 0
        self.events_skipped = 0
        self.start_time: Optional[datetime] = None
        
        # Event handlers (can be customized)
        self.event_handlers: Dict[EventType, Callable] = {
            EventType.CONCEPT_CREATED: self._handle_concept_created,
            EventType.CONCEPT_UPDATED: self._handle_concept_updated,
            EventType.CONCEPT_DELETED: self._handle_concept_deleted,
            EventType.LEARNING_PATH_CREATED: self._handle_learning_path_created,
            EventType.LEARNING_PATH_UPDATED: self._handle_learning_path_updated,
            EventType.LEARNING_PATH_DELETED: self._handle_learning_path_deleted,
            EventType.RELATIONSHIP_CREATED: self._handle_relationship_created,
            EventType.RELATIONSHIP_DELETED: self._handle_relationship_deleted,
        }
        
        self._initialize()
    
    def _initialize(self):
        """Initialize consumer connections"""
        self.redis_client = self.redis_manager.get_client()
        
        # Ensure stream and consumer group exist
        self.redis_manager.create_stream_with_group(
            self.redis_config.stream_name,
            self.redis_config.consumer_group
        )
        
        logger.info(f"SyncEventConsumer '{self.consumer_name}' initialized")
    
    def start(self):
        """Start consuming events from the stream"""
        if self.running:
            logger.warning("Consumer is already running")
            return
        
        self.running = True
        self.start_time = datetime.now(timezone.utc)
        logger.info(f"Consumer '{self.consumer_name}' starting...")
        
        try:
            self._consume_loop()
        except Exception as e:
            logger.error(f"Consumer loop error: {e}")
        finally:
            self.running = False
            logger.info(f"Consumer '{self.consumer_name}' stopped")
    
    def stop(self):
        """Stop consuming events"""
        logger.info(f"Consumer '{self.consumer_name}' stopping...")
        self.running = False
    
    def _consume_loop(self):
        """Main consumption loop"""
        while self.running:
            try:
                # Read events from stream
                events = self._read_events()
                
                if not events:
                    # No events, wait before next poll
                    time.sleep(1)
                    continue
                
                # Process each event
                for stream_id, data in events:
                    if not self.running:
                        break
                    
                    try:
                        self._process_event(stream_id, data)
                    except Exception as e:
                        logger.error(f"Error processing event {stream_id}: {e}")
                
            except Exception as e:
                logger.error(f"Consume loop error: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _read_events(self) -> list:
        """
        Read events from Redis stream.
        
        Returns:
            List of (stream_id, event_data) tuples
        """
        try:
            # Read with blocking for efficiency
            result = self.redis_client.xreadgroup(
                self.redis_config.consumer_group,
                self.consumer_name,
                {self.redis_config.stream_name: ">"},
                count=self.sync_config.prefetch_count,
                block=5000  # 5 second blocking
            )
            
            if not result:
                return []
            
            events = []
            for stream_name, stream_events in result:
                for event_data in stream_events:
                    stream_id = event_data[0]
                    data = event_data[1]
                    events.append((stream_id, data))
            
            return events
            
        except Exception as e:
            logger.error(f"Error reading from stream: {e}")
            return []
    
    def _process_event(self, stream_id: str, data: Dict[str, str]):
        """
        Process a single event from the stream.
        
        Args:
            stream_id: Redis stream message ID
            data: Event data from stream
        """
        with self._processing_lock:
            try:
                # Parse event
                event = self._parse_event(data)
                if not event:
                    logger.warning(f"Could not parse event: {data}")
                    return
                
                logger.debug(f"Processing event: {event.event_id} ({event.event_type.value})")
                
                # Update status to PROCESSING
                self._update_event_status(event.event_id, SyncEventStatus.PROCESSING, stream_id)
                
                # Check for conflicts (idempotency)
                if self._should_skip_event(event):
                    self._skip_event(event, "Conflict detected - event is stale")
                    self.events_skipped += 1
                    return
                
                # Get handler and process
                handler = self.event_handlers.get(event.event_type)
                if not handler:
                    logger.warning(f"No handler for event type: {event.event_type}")
                    self._skip_event(event, f"No handler for {event.event_type}")
                    self.events_skipped += 1
                    return
                
                # Process the event
                success = handler(event)
                
                if success:
                    # Mark as completed
                    self._complete_event(event.event_id, stream_id)
                    self.events_processed += 1
                    logger.info(f"Event {event.event_id} processed successfully")
                else:
                    # Handle failure
                    self._handle_event_failure(event, stream_id)
                    self.events_failed += 1
                    
            except Exception as e:
                logger.error(f"Error processing event {stream_id}: {e}")
                self._update_event_error(data.get("event_id", "unknown"), str(e))
                self.events_failed += 1
    
    def _parse_event(self, data: Dict[str, str]) -> Optional[SyncEvent]:
        """Parse event data from stream"""
        try:
            event_data = json.loads(data.get("data", "{}"))
            return SyncEvent.from_dict(event_data)
        except Exception as e:
            logger.error(f"Failed to parse event: {e}")
            return None
    
    def _should_skip_event(self, event: SyncEvent) -> bool:
        """
        Check if event should be skipped (conflict detection).
        
        Uses last-write-wins strategy with timestamp comparison.
        """
        if not self.sync_config.conflict_detection_enabled:
            return False
        
        # Check Neo4j for existing data with newer version
        if event.entity_type == "concept":
            version = self.neo4j_manager.get_node_version("Concept", "concept_id", event.entity_id)
        elif event.entity_type == "learning_path":
            version = self.neo4j_manager.get_node_version("LearningPath", "path_id", event.entity_id)
        else:
            return False
        
        if version and version > event.source_version:
            logger.info(f"Skipping stale event {event.event_id}: Neo4j version {version} > source version {event.source_version}")
            return True
        
        return False
    
    def _handle_concept_created(self, event: SyncEvent) -> bool:
        """Handle concept creation event"""
        payload = event.payload
        
        query = """
        MERGE (c:Concept {concept_id: $concept_id})
        SET c.name = $name,
            c.display_name = $display_name,
            c.category = $category,
            c.subcategory = $subcategory,
            c.domain = $domain,
            c.difficulty_level = $difficulty_level,
            c.description = $description,
            c.detailed_description = $detailed_description,
            c.complexity_score = $complexity_score,
            c.cognitive_load = $cognitive_load,
            c.key_terms = $key_terms,
            c.synonyms = $synonyms,
            c.created_at = datetime(),
            c.updated_at = datetime(),
            c.last_synced_at = datetime(),
            c.source_version = $source_version
        RETURN c
        """
        
        success = self.neo4j_manager.execute_write(query, {
            "concept_id": payload.get("concept_id", payload.get("name", "")),
            "name": payload.get("name", ""),
            "display_name": payload.get("display_name", ""),
            "category": payload.get("category", ""),
            "subcategory": payload.get("subcategory", ""),
            "domain": payload.get("domain", ""),
            "difficulty_level": payload.get("difficulty_level", ""),
            "description": payload.get("description", ""),
            "detailed_description": payload.get("detailed_description", ""),
            "complexity_score": payload.get("complexity_score", 0),
            "cognitive_load": payload.get("cognitive_load", 0),
            "key_terms": payload.get("key_terms", []),
            "synonyms": payload.get("synonyms", []),
            "source_version": event.source_version
        })
        
        if success:
            self._update_sync_status(event.entity_id, "concept", event.source_version)
        
        return success
    
    def _handle_concept_updated(self, event: SyncEvent) -> bool:
        """Handle concept update event"""
        # Same as create - MERGE will update existing
        return self._handle_concept_created(event)
    
    def _handle_concept_deleted(self, event: SyncEvent) -> bool:
        """Handle concept deletion event"""
        query = """
        MATCH (c:Concept {concept_id: $concept_id})
        DETACH DELETE c
        """
        
        success = self.neo4j_manager.execute_write(query, {
            "concept_id": event.entity_id
        })
        
        if success:
            self._update_sync_status(event.entity_id, "concept", event.source_version, is_deleted=True)
        
        return success
    
    def _handle_learning_path_created(self, event: SyncEvent) -> bool:
        """Handle learning path creation event"""
        payload = event.payload
        
        query = """
        MERGE (p:LearningPath {path_id: $path_id})
        SET p.name = $name,
            p.title = $title,
            p.description = $description,
            p.category = $category,
            p.difficulty_level = $difficulty_level,
            p.estimated_duration = $estimated_duration,
            p.target_audience = $target_audience,
            p.concept_count = $concept_count,
            p.created_at = datetime(),
            p.updated_at = datetime(),
            p.last_synced_at = datetime(),
            p.source_version = $source_version
        RETURN p
        """
        
        success = self.neo4j_manager.execute_write(query, {
            "path_id": payload.get("path_id", payload.get("name", "")),
            "name": payload.get("name", ""),
            "title": payload.get("title", ""),
            "description": payload.get("description", ""),
            "category": payload.get("category", ""),
            "difficulty_level": payload.get("difficulty_level", ""),
            "estimated_duration": payload.get("estimated_duration", 0),
            "target_audience": payload.get("target_audience", ""),
            "concept_count": len(payload.get("concepts", [])),
            "source_version": event.source_version
        })
        
        if success:
            # Also create relationships to concepts
            concepts = payload.get("concepts", [])
            for concept_name in concepts:
                self._create_path_concept_relationship(payload.get("path_id", ""), concept_name)
            
            self._update_sync_status(event.entity_id, "learning_path", event.source_version)
        
        return success
    
    def _handle_learning_path_updated(self, event: SyncEvent) -> bool:
        """Handle learning path update event"""
        # Same as create - MERGE will update existing
        return self._handle_learning_path_created(event)
    
    def _handle_learning_path_deleted(self, event: SyncEvent) -> bool:
        """Handle learning path deletion event"""
        query = """
        MATCH (p:LearningPath {path_id: $path_id})
        DETACH DELETE p
        """
        
        success = self.neo4j_manager.execute_write(query, {
            "path_id": event.entity_id
        })
        
        if success:
            self._update_sync_status(event.entity_id, "learning_path", event.source_version, is_deleted=True)
        
        return success
    
    def _handle_relationship_created(self, event: SyncEvent) -> bool:
        """Handle relationship creation event"""
        payload = event.payload
        
        source = payload.get("from", "")
        target = payload.get("to", "")
        rel_type = payload.get("type", "RELATED_TO")
        strength = payload.get("strength", 1)
        
        query = f"""
        MATCH (a:Concept {{name: $source}})
        MATCH (b:Concept {{name: $target}})
        MERGE (a)-[r:{rel_type} {{strength: $strength, created_at: datetime()}}]->(b)
        SET r.updated_at = datetime()
        RETURN a.name, type(r), b.name
        """
        
        success = self.neo4j_manager.execute_write(query, {
            "source": source,
            "target": target,
            "strength": strength
        })
        
        return success
    
    def _handle_relationship_deleted(self, event: SyncEvent) -> bool:
        """Handle relationship deletion event"""
        payload = event.payload
        
        source = payload.get("from", "")
        target = payload.get("to", "")
        rel_type = payload.get("type", "RELATED_TO")
        
        query = f"""
        MATCH (a:Concept {{name: $source}})-[r:{rel_type}]->(b:Concept {{name: $target}})
        DELETE r
        """
        
        success = self.neo4j_manager.execute_write(query, {
            "source": source,
            "target": target
        })
        
        return success
    
    def _create_path_concept_relationship(self, path_id: str, concept_name: str):
        """Create PathContains relationship between path and concept"""
        query = """
        MATCH (p:LearningPath {path_id: $path_id})
        MATCH (c:Concept {name: $concept_name})
        MERGE (p)-[r:PathContains {order_index: 0, is_required: true, created_at: datetime()}]->(c)
        RETURN p.name, c.name
        """
        
        self.neo4j_manager.execute_write(query, {
            "path_id": path_id,
            "concept_name": concept_name
        })
    
    def _update_event_status(self, event_id: str, status: SyncEventStatus, redis_message_id: str = None):
        """Update event status in database"""
        with self.postgres_manager.get_session() as session:
            event_log = session.query(SyncEventLog).filter(
                SyncEventLog.event_id == event_id
            ).first()
            
            if event_log:
                event_log.status = status
                if redis_message_id:
                    event_log.redis_message_id = redis_message_id
                session.flush()
    
    def _update_event_error(self, event_id: str, error_message: str):
        """Update event with error message"""
        with self.postgres_manager.get_session() as session:
            event_log = session.query(SyncEventLog).filter(
                SyncEventLog.event_id == event_id
            ).first()
            
            if event_log:
                event_log.mark_failed(error_message)
                session.flush()
    
    def _complete_event(self, event_id: str, redis_message_id: str):
        """Mark event as completed and acknowledge in Redis"""
        with self.postgres_manager.get_session() as session:
            event_log = session.query(SyncEventLog).filter(
                SyncEventLog.event_id == event_id
            ).first()
            
            if event_log:
                event_log.mark_completed()
                session.flush()
        
        # Acknowledge in Redis
        try:
            self.redis_client.xack(
                self.redis_config.stream_name,
                self.redis_config.consumer_group,
                redis_message_id
            )
        except Exception as e:
            logger.error(f"Failed to acknowledge message: {e}")
    
    def _skip_event(self, event: SyncEvent, reason: str):
        """Skip event due to conflict or other reason"""
        with self.postgres_manager.get_session() as session:
            event_log = session.query(SyncEventLog).filter(
                SyncEventLog.event_id == event.event_id
            ).first()
            
            if event_log:
                event_log.mark_skipped(reason)
                session.flush()
        
        logger.info(f"Event {event.event_id} skipped: {reason}")
    
    def _handle_event_failure(self, event: SyncEvent, stream_id: str):
        """Handle event processing failure"""
        with self.postgres_manager.get_session() as session:
            event_log = session.query(SyncEventLog).filter(
                SyncEventLog.event_id == event.event_id
            ).first()
            
            if event_log:
                if event_log.should_retry():
                    # Increment retry and requeue
                    event_log.increment_retry()
                    logger.warning(f"Event {event.event_id} failed, retry {event_log.retry_count}/{event_log.max_retries}")
                else:
                    # Mark as failed
                    event_log.mark_failed("Max retries exceeded")
                    logger.error(f"Event {event.event_id} failed permanently")
                
                session.flush()
        
        # Acknowledge to remove from queue (will be retried from DB)
        try:
            self.redis_client.xack(
                self.redis_config.stream_name,
                self.redis_config.consumer_group,
                stream_id
            )
        except Exception as e:
            logger.error(f"Failed to acknowledge failed message: {e}")
    
    def _update_sync_status(self, entity_id: str, entity_type: str, version: int, is_deleted: bool = False):
        """Update sync status after successful processing"""
        with self.postgres_manager.get_session() as session:
            status = session.query(SyncStatus).filter(
                SyncStatus.entity_id == entity_id,
                SyncStatus.entity_type == entity_type
            ).first()
            
            if not status:
                status = SyncStatus(
                    entity_id=entity_id,
                    entity_type=entity_type
                )
                session.add(status)
            
            if is_deleted:
                status.is_synced = True
                status.has_pending_changes = False
            else:
                status.update_after_sync(version)
            
            session.flush()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get consumer statistics"""
        return {
            "consumer_name": self.consumer_name,
            "running": self.running,
            "events_processed": self.events_processed,
            "events_failed": self.events_failed,
            "events_skipped": self.events_skipped,
            "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds() if self.start_time else 0
        }
    
    def close(self):
        """Close consumer connections"""
        self.stop()
        if self.redis_client:
            self.redis_client.close()
            self.redis_client = None
        logger.info(f"Consumer '{self.consumer_name}' closed")


def run_consumer(consumer_name: Optional[str] = None):
    """
    Convenience function to run a consumer.
    
    Args:
        consumer_name: Optional name for the consumer
    """
    consumer = SyncEventConsumer(consumer_name)
    
    import signal
    import sys
    
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        consumer.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    consumer.start()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync Event Consumer")
    parser.add_argument("--name", type=str, help="Consumer name")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    run_consumer(args.name)
