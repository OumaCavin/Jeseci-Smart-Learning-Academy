#!/usr/bin/env python3
"""
Unit Tests for Sync Engine

This module provides comprehensive unit tests for the event-driven
synchronization system, covering:
- Event types and models
- Publisher functionality
- Consumer processing
- Reconciliation jobs
- Conflict detection and resolution

Author: Jeseci Development Team
"""

import json
import os
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, Mock
from typing import Dict, Any

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.sync_engine.events import (
    EventType, 
    SyncEvent, 
    EventBatch,
    create_concept_event,
    create_learning_path_event,
    create_relationship_event
)
from backend.sync_engine.config import (
    RedisConfig, 
    SyncConfig, 
    DatabaseConfig,
    get_redis_config,
    get_sync_config,
    validate_config
)
from backend.sync_engine.models import (
    SyncEventStatus,
    ConflictResolutionStatus,
    SyncEventLog,
    SyncStatus,
    SyncConflict
)
from backend.sync_engine.conflict_resolution import (
    ConflictType,
    ResolutionStrategy,
    ConflictInfo,
    ConflictDetector,
    ConflictResolver
)


class TestEventType(unittest.TestCase):
    """Tests for EventType enumeration"""
    
    def test_create_events(self):
        """Test identification of creation events"""
        self.assertTrue(EventType.is_create_event(EventType.CONCEPT_CREATED))
        self.assertTrue(EventType.is_create_event(EventType.LEARNING_PATH_CREATED))
        self.assertFalse(EventType.is_create_event(EventType.CONCEPT_UPDATED))
        self.assertFalse(EventType.is_create_event(EventType.CONCEPT_DELETED))
    
    def test_update_events(self):
        """Test identification of update events"""
        self.assertTrue(EventType.is_update_event(EventType.CONCEPT_UPDATED))
        self.assertTrue(EventType.is_update_event(EventType.LEARNING_PATH_UPDATED))
        self.assertFalse(EventType.is_update_event(EventType.CONCEPT_CREATED))
    
    def test_delete_events(self):
        """Test identification of delete events"""
        self.assertTrue(EventType.is_delete_event(EventType.CONCEPT_DELETED))
        self.assertTrue(EventType.is_delete_event(EventType.LEARNING_PATH_DELETED))
        self.assertFalse(EventType.is_delete_event(EventType.CONCEPT_CREATED))
    
    def test_relationship_events(self):
        """Test identification of relationship events"""
        self.assertTrue(EventType.is_relationship_event(EventType.RELATIONSHIP_CREATED))
        self.assertTrue(EventType.is_relationship_event(EventType.RELATIONSHIP_DELETED))
        self.assertFalse(EventType.is_relationship_event(EventType.CONCEPT_CREATED))
    
    def test_entity_type(self):
        """Test entity type extraction"""
        self.assertEqual(EventType.get_entity_type(EventType.CONCEPT_CREATED), "concept")
        self.assertEqual(EventType.get_entity_type(EventType.LEARNING_PATH_UPDATED), "learning_path")
        self.assertEqual(EventType.get_entity_type(EventType.RELATIONSHIP_CREATED), "relationship")


class TestSyncEvent(unittest.TestCase):
    """Tests for SyncEvent model"""
    
    def test_create_event(self):
        """Test creating a basic sync event"""
        event = SyncEvent(
            event_type=EventType.CONCEPT_CREATED,
            entity_id="test-concept-1",
            entity_type="concept",
            payload={"name": "Test Concept", "category": "Test"}
        )
        
        self.assertIsNotNone(event.event_id)
        self.assertIsNotNone(event.correlation_id)
        self.assertEqual(event.event_type, EventType.CONCEPT_CREATED)
        self.assertEqual(event.entity_id, "test-concept-1")
        self.assertEqual(event.entity_type, "concept")
        self.assertEqual(event.payload["name"], "Test Concept")
        self.assertEqual(event.retry_count, 0)
        self.assertEqual(event.max_retries, 3)
    
    def test_to_dict(self):
        """Test converting event to dictionary"""
        event = SyncEvent(
            event_type=EventType.CONCEPT_UPDATED,
            entity_id="test-concept-2",
            entity_type="concept",
            payload={"name": "Updated Concept"}
        )
        
        data = event.to_dict()
        
        self.assertEqual(data["event_type"], "CONCEPT_UPDATED")
        self.assertEqual(data["entity_id"], "test-concept-2")
        self.assertEqual(data["entity_type"], "concept")
        self.assertEqual(data["payload"]["name"], "Updated Concept")
    
    def test_to_json(self):
        """Test converting event to JSON"""
        event = SyncEvent(
            event_type=EventType.LEARNING_PATH_CREATED,
            entity_id="test-path-1",
            entity_type="learning_path",
            payload={"title": "Test Path"}
        )
        
        json_str = event.to_json()
        data = json.loads(json_str)
        
        self.assertEqual(data["event_type"], "LEARNING_PATH_CREATED")
        self.assertEqual(data["entity_id"], "test-path-1")
    
    def test_from_dict(self):
        """Test creating event from dictionary"""
        data = {
            "event_id": "test-id-123",
            "correlation_id": "corr-123",
            "event_type": "CONCEPT_DELETED",
            "entity_id": "concept-123",
            "entity_type": "concept",
            "timestamp": 1234567890,
            "payload": {"name": "Deleted Concept"},
            "source_version": 1234567890,
            "retry_count": 1,
            "max_retries": 5
        }
        
        event = SyncEvent.from_dict(data)
        
        self.assertEqual(event.event_id, "test-id-123")
        self.assertEqual(event.event_type, EventType.CONCEPT_DELETED)
        self.assertEqual(event.entity_id, "concept-123")
        self.assertEqual(event.retry_count, 1)
        self.assertEqual(event.max_retries, 5)
    
    def test_from_json(self):
        """Test creating event from JSON string"""
        json_str = '{"event_id": "json-id", "event_type": "LEARNING_PATH_UPDATED", "entity_id": "path-1"}'
        
        event = SyncEvent.from_json(json_str)
        
        self.assertEqual(event.event_id, "json-id")
        self.assertEqual(event.event_type, EventType.LEARNING_PATH_UPDATED)
        self.assertEqual(event.entity_id, "path-1")
    
    def test_should_retry(self):
        """Test retry decision logic"""
        event = SyncEvent(
            event_type=EventType.CONCEPT_CREATED,
            entity_id="test",
            entity_type="concept"
        )
        
        # Initial state should allow retry
        self.assertTrue(event.should_retry())
        
        # After max retries, should not retry
        event.retry_count = event.max_retries
        self.assertFalse(event.should_retry())
    
    def test_increment_retry(self):
        """Test retry increment"""
        event = SyncEvent(
            event_type=EventType.CONCEPT_CREATED,
            entity_id="test",
            entity_type="concept"
        )
        
        event.increment_retry("Test error")
        
        self.assertEqual(event.retry_count, 1)
        self.assertEqual(event.error_message, "Test error")
        self.assertIsNotNone(event.updated_at)
    
    def test_mark_completed(self):
        """Test marking event as completed"""
        event = SyncEvent(
            event_type=EventType.CONCEPT_CREATED,
            entity_id="test",
            entity_type="concept"
        )
        
        event.mark_completed()
        
        self.assertIsNone(event.error_message)
        self.assertIsNotNone(event.updated_at)
    
    def test_mark_failed(self):
        """Test marking event as failed"""
        event = SyncEvent(
            event_type=EventType.CONCEPT_CREATED,
            entity_id="test",
            entity_type="concept"
        )
        
        event.mark_failed("Permanent error")
        
        self.assertEqual(event.status, SyncEventStatus.FAILED)
        self.assertEqual(event.error_message, "Permanent error")
    
    def test_get_redis_fields(self):
        """Test Redis fields generation"""
        event = SyncEvent(
            event_type=EventType.RELATIONSHIP_CREATED,
            entity_id="from->to",
            entity_type="relationship",
            payload={"from": "A", "to": "B", "type": "RELATED_TO"}
        )
        
        fields = event.get_redis_fields()
        
        self.assertEqual(fields["event_id"], event.event_id)
        self.assertEqual(fields["event_type"], "RELATIONSHIP_CREATED")
        self.assertEqual(fields["entity_id"], "from->to")
        self.assertIn("data", fields)
    
    def test_factory_methods(self):
        """Test factory methods for creating events"""
        # Concept event
        concept_data = {"concept_id": "c1", "name": "Concept 1", "category": "Cat1"}
        event = create_concept_event(concept_data, EventType.CONCEPT_CREATED)
        self.assertEqual(event.entity_type, "concept")
        self.assertEqual(event.entity_id, "c1")
        self.assertEqual(event.event_type, EventType.CONCEPT_CREATED)
        
        # Learning path event
        path_data = {"path_id": "p1", "name": "Path 1", "title": "Path Title"}
        event = create_learning_path_event(path_data, EventType.LEARNING_PATH_UPDATED)
        self.assertEqual(event.entity_type, "learning_path")
        self.assertEqual(event.entity_id, "p1")
        self.assertEqual(event.event_type, EventType.LEARNING_PATH_UPDATED)
        
        # Relationship event
        rel_data = {"from": "concept_a", "to": "concept_b", "type": "PREREQUISITE"}
        event = create_relationship_event(rel_data, EventType.RELATIONSHIP_CREATED)
        self.assertEqual(event.entity_type, "relationship")
        self.assertEqual(event.entity_id, "concept_a->concept_b")


class TestEventBatch(unittest.TestCase):
    """Tests for EventBatch"""
    
    def test_add_event(self):
        """Test adding events to batch"""
        batch = EventBatch()
        event = SyncEvent(
            event_type=EventType.CONCEPT_CREATED,
            entity_id="test",
            entity_type="concept"
        )
        
        batch.add_event(event)
        
        self.assertEqual(batch.size(), 1)
        self.assertFalse(batch.is_empty())
    
    def test_clear_batch(self):
        """Test clearing batch"""
        batch = EventBatch()
        batch.add_event(SyncEvent(event_type=EventType.CONCEPT_CREATED, entity_id="1", entity_type="concept"))
        batch.add_event(SyncEvent(event_type=EventType.CONCEPT_UPDATED, entity_id="2", entity_type="concept"))
        
        batch.clear()
        
        self.assertEqual(batch.size(), 0)
        self.assertTrue(batch.is_empty())
    
    def test_filter_by_type(self):
        """Test filtering events by type"""
        batch = EventBatch()
        batch.add_event(SyncEvent(event_type=EventType.CONCEPT_CREATED, entity_id="1", entity_type="concept"))
        batch.add_event(SyncEvent(event_type=EventType.CONCEPT_UPDATED, entity_id="2", entity_type="concept"))
        batch.add_event(SyncEvent(event_type=EventType.CONCEPT_DELETED, entity_id="3", entity_type="concept"))
        
        created_events = batch.get_events_by_type(EventType.CONCEPT_CREATED)
        self.assertEqual(len(created_events), 1)
        self.assertEqual(created_events[0].entity_id, "1")


class TestConfig(unittest.TestCase):
    """Tests for configuration classes"""
    
    def test_redis_config_defaults(self):
        """Test RedisConfig default values"""
        config = RedisConfig()
        
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 6379)
        self.assertEqual(config.stream_name, "jeseci:sync:stream")
        self.assertEqual(config.consumer_group, "jeseci:sync:consumers")
        self.assertEqual(config.max_connections, 10)
    
    def test_redis_config_to_url(self):
        """Test Redis URL generation"""
        config = RedisConfig(host="redis.example.com", port=6380, password="secret")
        url = config.to_url()
        
        self.assertIn("redis://", url)
        self.assertIn("redis.example.com", url)
        self.assertIn("6380", url)
    
    def test_sync_config_defaults(self):
        """Test SyncConfig default values"""
        config = SyncConfig()
        
        self.assertEqual(config.batch_size, 10)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.reconciliation_interval_seconds, 300)
        self.assertTrue(config.conflict_detection_enabled)
        self.assertTrue(config.auto_repair_enabled)
    
    def test_database_config(self):
        """Test DatabaseConfig"""
        config = DatabaseConfig()
        
        self.assertEqual(config.postgres_host, "localhost")
        self.assertEqual(config.postgres_port, 5432)
        self.assertEqual(config.postgres_schema, "jeseci_academy")
        self.assertEqual(config.neo4j_uri, "bolt://localhost:7687")
    
    def test_database_url_generation(self):
        """Test PostgreSQL URL generation"""
        config = DatabaseConfig(
            postgres_host="pg.example.com",
            postgres_port=5433,
            postgres_user="user",
            postgres_password="pass",
            postgres_db="mydb"
        )
        
        url = config.to_postgres_url()
        
        self.assertIn("user:pass", url)
        self.assertIn("pg.example.com", url)
        self.assertIn("5433", url)
        self.assertIn("mydb", url)
    
    @patch.dict(os.environ, {"REDIS_HOST": "test-host", "REDIS_PORT": "6380"})
    def test_environment_variables(self):
        """Test loading configuration from environment"""
        config = get_redis_config()
        
        self.assertEqual(config.host, "test-host")
        self.assertEqual(config.port, 6380)


class TestSyncEventLog(unittest.TestCase):
    """Tests for SyncEventLog model"""
    
    def test_to_event(self):
        """Test converting database record to SyncEvent"""
        event_log = SyncEventLog(
            event_id="test-123",
            correlation_id="corr-456",
            event_type="CONCEPT_CREATED",
            entity_id="concept-1",
            entity_type="concept",
            payload={"name": "Test"},
            source_version=1234567890
        )
        
        event = event_log.to_event()
        
        self.assertEqual(event.event_id, "test-123")
        self.assertEqual(event.event_type, EventType.CONCEPT_CREATED)
        self.assertEqual(event.entity_id, "concept-1")
        self.assertEqual(event.payload["name"], "Test")
    
    def test_status_transitions(self):
        """Test status transition methods"""
        event_log = SyncEventLog(
            event_id="test",
            event_type="CONCEPT_CREATED",
            entity_id="test",
            entity_type="concept",
            payload={},
            source_version=1
        )
        
        # Initial state
        self.assertEqual(event_log.status, SyncEventStatus.PENDING)
        
        # Mark published
        event_log.mark_published("redis-msg-1")
        self.assertEqual(event_log.status, SyncEventStatus.PUBLISHED)
        self.assertEqual(event_log.redis_message_id, "redis-msg-1")
        self.assertIsNotNone(event_log.published_at)
        
        # Mark processing
        event_log.mark_processing()
        self.assertEqual(event_log.status, SyncEventStatus.PROCESSING)
        
        # Mark completed
        event_log.mark_completed()
        self.assertEqual(event_log.status, SyncEventStatus.COMPLETED)
        self.assertIsNone(event_log.error_message)
        self.assertIsNotNone(event_log.completed_at)
    
    def test_failure_handling(self):
        """Test failure handling"""
        event_log = SyncEventLog(
            event_id="test",
            event_type="CONCEPT_CREATED",
            entity_id="test",
            entity_type="concept",
            payload={},
            source_version=1
        )
        
        event_log.mark_failed("Connection error", "Full traceback here")
        
        self.assertEqual(event_log.status, SyncEventStatus.FAILED)
        self.assertEqual(event_log.error_message, "Connection error")
        self.assertEqual(event_log.error_trace, "Full traceback here")
    
    def test_skip_event(self):
        """Test skipping events"""
        event_log = SyncEventLog(
            event_id="test",
            event_type="CONCEPT_CREATED",
            entity_id="test",
            entity_type="concept",
            payload={},
            source_version=1
        )
        
        event_log.mark_skipped("Stale event")
        
        self.assertEqual(event_log.status, SyncEventStatus.SKIPPED)
        self.assertEqual(event_log.error_message, "Stale event")
    
    def test_retry_logic(self):
        """Test retry counting"""
        event_log = SyncEventLog(
            event_id="test",
            event_type="CONCEPT_CREATED",
            entity_id="test",
            entity_type="concept",
            payload={},
            source_version=1,
            max_retries=3
        )
        
        # Initial state
        self.assertTrue(event_log.should_retry())
        
        # Increment retries
        for i in range(3):
            event_log.increment_retry()
            self.assertEqual(event_log.retry_count, i + 1)
        
        # Should not retry after max
        self.assertFalse(event_log.should_retry())
        self.assertEqual(event_log.status, SyncEventStatus.FAILED)


class TestSyncStatus(unittest.TestCase):
    """Tests for SyncStatus model"""
    
    def test_update_after_sync(self):
        """Test updating status after successful sync"""
        status = SyncStatus(
            entity_id="concept-1",
            entity_type="concept"
        )
        
        status.update_after_sync(1234567890, "checksum123")
        
        self.assertTrue(status.is_synced)
        self.assertIsNotNone(status.last_synced_at)
        self.assertEqual(status.last_synced_version, 1234567890)
        self.assertEqual(status.source_version, 1234567890)
        self.assertEqual(status.neo4j_version, 1234567890)
        self.assertEqual(status.neo4j_checksum, "checksum123")
        self.assertFalse(status.has_pending_changes)
    
    def test_mark_pending(self):
        """Test marking entity as having pending changes"""
        status = SyncStatus(
            entity_id="concept-1",
            entity_type="concept"
        )
        
        status.mark_pending(1234567891)
        
        self.assertTrue(status.has_pending_changes)
        self.assertEqual(status.source_version, 1234567891)
        self.assertFalse(status.is_synced)
    
    def test_conflict_handling(self):
        """Test conflict marking and resolution"""
        status = SyncStatus(
            entity_id="concept-1",
            entity_type="concept"
        )
        
        # Mark conflict
        status.mark_conflict("Version mismatch")
        
        self.assertTrue(status.has_conflict)
        self.assertEqual(status.conflict_count, 1)
        self.assertEqual(status.last_error, "Version mismatch")
        
        # Resolve conflict
        status.resolve_conflict()
        
        self.assertFalse(status.has_conflict)
        self.assertIsNone(status.last_error)


class TestConflictInfo(unittest.TestCase):
    """Tests for ConflictInfo"""
    
    def test_create_conflict_info(self):
        """Test creating ConflictInfo"""
        conflict = ConflictInfo(
            entity_id="concept-1",
            entity_type="concept",
            conflict_type=ConflictType.VERSION_MISMATCH,
            source_data={"name": "Source Name"},
            target_data={"name": "Target Name"},
            source_version=100,
            target_version=200,
            source_updated_at=datetime.now(timezone.utc),
            target_updated_at=datetime.now(timezone.utc)
        )
        
        self.assertEqual(conflict.entity_id, "concept-1")
        self.assertEqual(conflict.conflict_type, ConflictType.VERSION_MISMATCH)
        self.assertEqual(conflict.source_version, 100)
        self.assertEqual(conflict.target_version, 200)
    
    def test_to_dict_and_json(self):
        """Test serialization"""
        conflict = ConflictInfo(
            entity_id="concept-1",
            entity_type="concept",
            conflict_type=ConflictType.DATA_DIVERGENCE,
            source_data={"name": "A"},
            target_data={"name": "B"},
            source_version=100,
            target_version=200,
            source_updated_at=datetime.now(timezone.utc),
            target_updated_at=datetime.now(timezone.utc),
            differences={"name": {"source": "A", "target": "B"}}
        )
        
        data = conflict.to_dict()
        self.assertEqual(data["entity_id"], "concept-1")
        self.assertEqual(data["conflict_type"], "DATA_DIVERGENCE")
        self.assertIn("differences", data)
        
        json_str = conflict.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["entity_id"], "concept-1")


class TestConflictDetector(unittest.TestCase):
    """Tests for ConflictDetector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = ConflictDetector()
    
    @patch('backend.sync_engine.conflict_resolution.get_postgres_sync_manager')
    @patch('backend.sync_engine.conflict_resolution.get_neo4j_sync_manager')
    def test_detect_conflicts_no_conflict(self, mock_neo4j, mock_pg):
        """Test conflict detection when no conflict exists"""
        mock_pg_manager = MagicMock()
        mock_neo4j_manager = MagicMock()
        
        mock_pg_manager.execute_query.return_value = [{"name": "Test", "updated_at": datetime.now(timezone.utc)}]
        mock_neo4j_manager.get_node.return_value = {"name": "Test", "updated_at": datetime.now(timezone.utc), "source_version": 1}
        
        mock_pg.return_value = mock_pg_manager
        mock_neo4j.return_value = mock_neo4j_manager
        
        # Create detector with mocked managers
        detector = ConflictDetector()
        detector.postgres_manager = mock_pg_manager
        detector.neo4j_manager = mock_neo4j_manager
        
        # Mock last_synced_at to be recent
        mock_neo4j_manager.get_node.return_value = {
            "name": "Test",
            "updated_at": datetime.now(timezone.utc),
            "last_synced_at": datetime.now(timezone.utc)
        }
        
        conflict = detector.detect_conflicts("concept", "concept-1")
        
        # Should not detect conflict when versions are same
        self.assertIsNone(conflict)
    
    @patch('backend.sync_engine.conflict_resolution.get_postgres_sync_manager')
    @patch('backend.sync_engine.conflict_resolution.get_neo4j_sync_manager')
    def test_detect_conflicts_missing_entity(self, mock_neo4j, mock_pg):
        """Test conflict detection when entity only exists in one database"""
        mock_pg_manager = MagicMock()
        mock_neo4j_manager = MagicMock()
        
        # Entity exists in PostgreSQL but not Neo4j
        mock_pg_manager.execute_query.return_value = [{"name": "Test"}]
        mock_neo4j_manager.get_node.return_value = None
        
        mock_pg.return_value = mock_pg_manager
        mock_neo4j.return_value = mock_neo4j_manager
        
        detector = ConflictDetector()
        detector.postgres_manager = mock_pg_manager
        detector.neo4j_manager = mock_neo4j_manager
        
        conflict = detector.detect_conflicts("concept", "concept-1")
        
        # Missing in Neo4j is not a conflict (will be synced)
        self.assertIsNone(conflict)


class TestConflictResolver(unittest.TestCase):
    """Tests for ConflictResolver"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = ConflictResolver()
    
    def test_default_strategy_for_version_conflict(self):
        """Test that version conflicts use LAST_WRITE_WINS by default"""
        strategy = self.resolver._get_default_strategy(ConflictType.VERSION_MISMATCH)
        self.assertEqual(strategy, ResolutionStrategy.LAST_WRITE_WINS)
    
    def test_default_strategy_for_data_divergence(self):
        """Test that data divergence uses MERGE by default"""
        strategy = self.resolver._get_default_strategy(ConflictType.DATA_DIVERGENCE)
        self.assertEqual(strategy, ResolutionStrategy.MERGE)
    
    def test_default_strategy_for_unknown(self):
        """Test that unknown conflict types use MANUAL_REVIEW"""
        strategy = self.resolver._get_default_strategy(ConflictType.SCHEMA_MISMATCH)
        self.assertEqual(strategy, ResolutionStrategy.MANUAL_REVIEW)


class TestIntegration(unittest.TestCase):
    """Integration tests for the sync engine"""
    
    def test_event_serialization_roundtrip(self):
        """Test that events can be serialized and deserialized"""
        original_event = SyncEvent(
            event_type=EventType.CONCEPT_CREATED,
            entity_id="test-entity",
            entity_type="concept",
            payload={
                "concept_id": "test-entity",
                "name": "Test Concept",
                "category": "Test Category",
                "difficulty_level": "beginner",
                "description": "A test concept for unit testing",
                "complexity_score": 5.0,
                "cognitive_load": 5.5,
                "key_terms": ["test", "unit", "testing"],
                "synonyms": ["test concept", "sample"]
            },
            source_version=1234567890,
            correlation_id="test-correlation-123"
        )
        
        # Serialize
        json_str = original_event.to_json()
        
        # Deserialize
        restored_event = SyncEvent.from_json(json_str)
        
        # Verify all fields match
        self.assertEqual(original_event.event_id, restored_event.event_id)
        self.assertEqual(original_event.event_type, restored_event.event_type)
        self.assertEqual(original_event.entity_id, restored_event.entity_id)
        self.assertEqual(original_event.entity_type, restored_event.entity_type)
        self.assertEqual(original_event.payload["name"], restored_event.payload["name"])
        self.assertEqual(original_event.payload["complexity_score"], restored_event.payload["complexity_score"])
        self.assertEqual(original_event.source_version, restored_event.source_version)
        self.assertEqual(original_event.correlation_id, restored_event.correlation_id)
    
    def test_batch_processing(self):
        """Test batch event processing"""
        batch = EventBatch()
        
        # Create multiple events
        for i in range(5):
            batch.add_event(SyncEvent(
                event_type=EventType.CONCEPT_CREATED,
                entity_id=f"concept-{i}",
                entity_type="concept",
                payload={"name": f"Concept {i}"}
            ))
        
        # Verify batch
        self.assertEqual(batch.size(), 5)
        self.assertFalse(batch.is_empty())
        
        # Filter by event type
        concept_events = batch.get_events_by_entity("concept")
        self.assertEqual(len(concept_events), 5)
        
        # Clear batch
        batch.clear()
        self.assertEqual(batch.size(), 0)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEventType))
    suite.addTests(loader.loadTestsFromTestCase(TestSyncEvent))
    suite.addTests(loader.loadTestsFromTestCase(TestEventBatch))
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestSyncEventLog))
    suite.addTests(loader.loadTestsFromTestCase(TestSyncStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictResolver))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
