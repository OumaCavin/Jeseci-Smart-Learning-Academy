"""
Reconciliation Job for Sync Engine

This module provides a background reconciliation job that periodically
compares PostgreSQL and Neo4j to detect and repair inconsistencies.

The reconciliation job:
1. Finds stuck events that haven't been processed
2. Compares entity data between databases
3. Detects drift and conflicts
4. Triggers repair events for inconsistent entities
5. Generates reports on reconciliation status

Author: Jeseci Development Team
"""

import hashlib
import json
import logging
import random
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
import hashlib

from .config import get_sync_config, get_database_config
from .events import SyncEvent, EventType
from .models import (
    SyncEventLog, SyncEventStatus, 
    SyncStatus, SyncConflict, 
    ReconciliationRun, ConflictResolutionStatus
)
from .publisher import get_sync_publisher
from .database import (
    get_postgres_sync_manager, 
    get_neo4j_sync_manager
)

logger = logging.getLogger(__name__)


class ReconciliationJob:
    """
    Background job for reconciling PostgreSQL and Neo4j data.
    
    This job runs periodically and:
    1. Republishes stuck events that failed to sync
    2. Compares entity data between databases
    3. Detects and repairs inconsistencies
    4. Generates reconciliation reports
    
    The job is designed to run as a background thread within
    the main application or as a standalone process.
    """
    
    def __init__(self):
        self.sync_config = get_sync_config()
        self.db_config = get_database_config()
        
        # Managers
        self.postgres_manager = get_postgres_sync_manager()
        self.neo4j_manager = get_neo4j_sync_manager()
        self.publisher = get_sync_publisher()
        
        # State
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_run: Optional[datetime] = None
        self.current_run: Optional[ReconciliationRun] = None
        
        # Statistics
        self.total_runs = 0
        self.total_repairs = 0
        self.total_conflicts_detected = 0
    
    def start(self):
        """Start the reconciliation job in a background thread"""
        if self.running:
            logger.warning("Reconciliation job is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Reconciliation job started")
    
    def stop(self):
        """Stop the reconciliation job"""
        logger.info("Reconciliation job stopping...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("Reconciliation job stopped")
    
    def _run_loop(self):
        """Main reconciliation loop"""
        while self.running:
            try:
                # Wait for next reconciliation interval
                time.sleep(self.sync_config.reconciliation_interval_seconds)
                
                if not self.running:
                    break
                
                # Run reconciliation
                self.run_reconciliation()
                
            except Exception as e:
                logger.error(f"Reconciliation loop error: {e}")
                time.sleep(60)  # Wait before retrying
    
    def run_reconciliation(self, run_type: str = "scheduled") -> Dict[str, Any]:
        """
        Run a full reconciliation cycle.
        
        Args:
            run_type: Type of run (scheduled, manual, triggered)
            
        Returns:
            Dictionary with reconciliation results
        """
        run_id = str(uuid.uuid4())
        logger.info(f"Starting reconciliation run {run_id} ({run_type})")
        
        # Create run record
        self.current_run = ReconciliationRun(
            run_id=run_id,
            run_type=run_type,
            status="RUNNING",
            batch_size=self.sync_config.reconciliation_batch_size
        )
        
        with self.postgres_manager.get_session() as session:
            session.add(self.current_run)
            session.flush()
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Step 1: Process stuck events
            stuck_count = self._process_stuck_events()
            self.current_run.add_stats(entities_checked=stuck_count)
            logger.info(f"Processed {stuck_count} stuck events")
            
            # Step 2: Check for data drift
            drift_results = self._check_data_drift()
            self.current_run.add_stats(
                inconsistencies_found=drift_results["inconsistencies"],
                inconsistencies_repaired=drift_results["repaired"]
            )
            logger.info(f"Found {drift_results['inconsistencies']} inconsistencies, repaired {drift_results['repaired']}")
            
            # Step 3: Detect conflicts
            conflict_count = self._detect_conflicts()
            self.current_run.add_stats(conflicts_detected=conflict_count)
            logger.info(f"Detected {conflict_count} conflicts")
            
            # Complete successfully
            self.current_run.complete()
            self.total_runs += 1
            self.total_repairs += drift_results["repaired"]
            self.total_conflicts_detected += conflict_count
            
            result = {
                "run_id": run_id,
                "status": "COMPLETED",
                "duration_seconds": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "stuck_events_processed": stuck_count,
                "inconsistencies_found": drift_results["inconsistencies"],
                "inconsistencies_repaired": drift_results["repaired"],
                "conflicts_detected": conflict_count
            }
            
            logger.info(f"Reconciliation run {run_id} completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Reconciliation run {run_id} failed: {e}")
            self.current_run.fail(str(e))
            
            return {
                "run_id": run_id,
                "status": "FAILED",
                "error": str(e),
                "duration_seconds": (datetime.now(timezone.utc) - start_time).total_seconds()
            }
        
        finally:
            self.last_run = datetime.now(timezone.utc)
    
    def _process_stuck_events(self) -> int:
        """
        Process events that are stuck in PENDING or PUBLISHED status.
        
        These events may have failed to publish or may have been lost.
        This method republishes them to ensure they are processed.
        
        Returns:
            Number of events processed
        """
        with self.postgres_manager.get_session() as session:
            # Find stuck events
            threshold = datetime.now(timezone.utc)
            threshold = threshold.replace(
                second=threshold.second - (self.sync_config.stale_event_threshold_minutes * 60)
            )
            
            stuck_events = session.query(SyncEventLog).filter(
                SyncEventLog.status.in_([
                    SyncEventStatus.PENDING,
                    SyncEventStatus.PUBLISHED
                ]),
                SyncEventLog.updated_at < threshold,
                SyncEventLog.retry_count < SyncEventLog.max_retries
            ).limit(self.sync_config.reconciliation_batch_size).all()
            
            processed = 0
            for event_log in stuck_events:
                try:
                    event = event_log.to_event()
                    
                    # Reset status for retry
                    event_log.status = SyncEventStatus.PENDING
                    event_log.retry_count = 0
                    
                    # Publish to Redis
                    if self._publish_event(event):
                        processed += 1
                        logger.debug(f"Republished stuck event: {event.event_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to process stuck event {event_log.event_id}: {e}")
            
            session.flush()
            return processed
    
    def _check_data_drift(self) -> Dict[str, int]:
        """
        Check for data drift between PostgreSQL and Neo4j.
        
        This method:
        1. Selects recently modified entities from PostgreSQL
        2. Compares their data with Neo4j
        3. Repairs any inconsistencies
        
        Returns:
            Dictionary with counts of inconsistencies and repairs
        """
        inconsistencies = 0
        repaired = 0
        
        # Check concepts
        concept_results = self._check_entity_drift("concepts", "Concept", "concept_id")
        inconsistencies += concept_results["inconsistencies"]
        repaired += concept_results["repaired"]
        
        # Check learning paths
        path_results = self._check_entity_drift("learning_paths", "LearningPath", "path_id")
        inconsistencies += path_results["inconsistencies"]
        repaired += path_results["repaired"]
        
        return {
            "inconsistencies": inconsistencies,
            "repaired": repaired
        }
    
    def _check_entity_drift(
        self, 
        pg_table: str, 
        neo4j_label: str,
        id_field: str
    ) -> Dict[str, int]:
        """
        Check for drift in a specific entity type.
        
        Args:
            pg_table: PostgreSQL table name
            neo4j_label: Neo4j node label
            id_field: Field name for ID
            
        Returns:
            Dictionary with counts
        """
        inconsistencies = 0
        repaired = 0
        
        schema = self.db_config.postgres_schema
        
        # Get recently modified entities from PostgreSQL
        query = f"""
        SELECT {id_field}, updated_at
        FROM {schema}.{pg_table}
        ORDER BY updated_at DESC
        LIMIT %s
        """
        
        pg_entities = self.postgres_manager.execute_query(
            query, 
            (self.sync_config.reconciliation_batch_size,)
        )
        
        for entity in pg_entities:
            entity_id = entity.get(id_field)
            
            # Get from Neo4j
            neo4j_node = self.neo4j_manager.get_node(
                neo4j_label, 
                id_field.replace("_", ""),  # Remove underscore for Neo4j property
                entity_id
            )
            
            if neo4j_node:
                # Compare versions
                pg_version = int(entity.get("updated_at", 0).timestamp()) if hasattr(entity.get("updated_at"), 'timestamp') else 0
                neo4j_version = neo4j_node.get("source_version", 0)
                
                if pg_version > neo4j_version:
                    # Drift detected - repair
                    inconsistencies += 1
                    
                    if self.sync_config.auto_repair_enabled:
                        if self._repair_entity(entity_id, pg_table, neo4j_label, id_field):
                            repaired += 1
                            logger.info(f"Repaired drift for {entity_id}")
            else:
                # Missing in Neo4j - repair
                inconsistencies += 1
                
                if self.sync_config.auto_repair_enabled:
                    if self._repair_entity(entity_id, pg_table, neo4j_label, id_field):
                        repaired += 1
                        logger.info(f"Repaired missing entity {entity_id}")
        
        return {
            "inconsistencies": inconsistencies,
            "repaired": repaired
        }
    
    def _repair_entity(
        self, 
        entity_id: str, 
        pg_table: str, 
        neo4j_label: str,
        id_field: str
    ) -> bool:
        """
        Repair a single entity by triggering a sync event.
        
        Args:
            entity_id: ID of entity to repair
            pg_table: PostgreSQL table name
            neo4j_label: Neo4j node label
            id_field: Field name for ID
            
        Returns:
            True if repair was triggered successfully
        """
        schema = self.db_config.postgres_schema
        
        # Get full entity data
        query = f"""
        SELECT * FROM {schema}.{pg_table}
        WHERE {id_field} = %s
        """
        
        entities = self.postgres_manager.execute_query(query, (entity_id,))
        
        if not entities:
            return False
        
        entity_data = entities[0]
        
        # Convert datetime to serializable format
        for key, value in entity_data.items():
            if hasattr(value, 'isoformat'):
                entity_data[key] = value.isoformat()
        
        # Determine event type
        if neo4j_label == "Concept":
            event_type = EventType.CONCEPT_UPDATED
        elif neo4j_label == "LearningPath":
            event_type = EventType.LEARNING_PATH_UPDATED
        else:
            event_type = EventType.CONCEPT_UPDATED
        
        # Publish repair event
        return self.publisher.publish_event(
            SyncEvent(
                event_type=event_type,
                entity_id=entity_id,
                entity_type=neo4j_label.lower(),
                payload=entity_data,
                source_version=int(datetime.utcnow().timestamp()),
                correlation_id=f"reconciliation-{uuid.uuid4()}"
            )
        )
    
    def _detect_conflicts(self) -> int:
        """
        Detect conflicts between PostgreSQL and Neo4j.
        
        Conflicts occur when the same entity has been modified in both
        databases independently. This method detects such conflicts
        and creates conflict records.
        
        Returns:
            Number of conflicts detected
        """
        conflicts_detected = 0
        
        with self.postgres_manager.get_session() as session:
            # Check entities with conflicts flag
            entities_with_conflicts = session.query(SyncStatus).filter(
                SyncStatus.has_conflict == True
            ).limit(self.sync_config.reconciliation_batch_size).all()
            
            for status in entities_with_conflicts:
                # Get data from both databases
                pg_data = self._get_entity_from_pg(status.entity_type, status.entity_id)
                neo4j_data = self._get_entity_from_neo4j(status.entity_type, status.entity_id)
                
                if pg_data and neo4j_data:
                    # Check for actual conflict
                    if self._is_conflict(pg_data, neo4j_data):
                        # Record conflict
                        conflict = SyncConflict(
                            entity_id=status.entity_id,
                            entity_type=status.entity_type,
                            conflict_type="VERSION_MISMATCH",
                            source_version=pg_data.get("updated_at", 0),
                            target_version=neo4j_data.get("updated_at", 0),
                            source_data=pg_data,
                            target_data=neo4j_data,
                            difference_summary=self._summarize_differences(pg_data, neo4j_data)
                        )
                        session.add(conflict)
                        
                        status.mark_conflict("Version mismatch detected during reconciliation")
                        conflicts_detected += 1
            
            session.flush()
        
        return conflicts_detected
    
    def _get_entity_from_pg(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity data from PostgreSQL"""
        table_map = {
            "concept": "concepts",
            "learning_path": "learning_paths"
        }
        
        table = table_map.get(entity_type)
        if not table:
            return None
        
        schema = self.db_config.postgres_schema
        id_field = "concept_id" if entity_type == "concept" else "path_id"
        
        query = f"""
        SELECT * FROM {schema}.{table}
        WHERE {id_field} = %s
        """
        
        results = self.postgres_manager.execute_query(query, (entity_id,))
        return results[0] if results else None
    
    def _get_entity_from_neo4j(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity data from Neo4j"""
        label_map = {
            "concept": "Concept",
            "learning_path": "LearningPath"
        }
        
        label = label_map.get(entity_type)
        if not label:
            return None
        
        property_name = "concept_id" if entity_type == "concept" else "path_id"
        
        return self.neo4j_manager.get_node(label, property_name, entity_id)
    
    def _is_conflict(self, pg_data: Dict[str, Any], neo4j_data: Dict[str, Any]) -> bool:
        """
        Check if two entity versions represent a conflict.
        
        A conflict exists if both versions have been modified after the
        last synchronization timestamp.
        """
        # Get last sync time from Neo4j
        last_sync = neo4j_data.get("last_synced_at")
        if not last_sync:
            return False
        
        # Convert to timestamp
        if hasattr(last_sync, 'timestamp'):
            last_sync_ts = last_sync.timestamp()
        else:
            last_sync_ts = 0
        
        # Check if PostgreSQL version is newer
        pg_updated = pg_data.get("updated_at")
        if pg_updated:
            if hasattr(pg_updated, 'timestamp'):
                pg_ts = pg_updated.timestamp()
            else:
                pg_ts = 0
        else:
            pg_ts = 0
        
        # Check if Neo4j version is newer (modified after last sync)
        neo4j_updated = neo4j_data.get("updated_at")
        if neo4j_updated:
            if hasattr(neo4j_updated, 'timestamp'):
                neo4j_ts = neo4j_updated.timestamp()
            else:
                neo4j_ts = 0
        else:
            neo4j_ts = 0
        
        # Conflict if both were modified after last sync
        return pg_ts > last_sync_ts and neo4j_ts > last_sync_ts
    
    def _summarize_differences(self, pg_data: Dict[str, Any], neo4j_data: Dict[str, Any]) -> str:
        """Summarize differences between two entity versions"""
        differences = []
        
        for key in set(pg_data.keys()) | set(neo4j_data.keys()):
            pg_val = pg_data.get(key)
            neo4j_val = neo4j_data.get(key)
            
            # Normalize for comparison
            if pg_val and hasattr(pg_val, 'isoformat'):
                pg_val = pg_val.isoformat()
            if neo4j_val and hasattr(neo4j_val, 'isoformat'):
                neo4j_val = neo4j_val.isoformat()
            
            if pg_val != neo4j_val:
                differences.append(f"{key}: PG={pg_val} vs Neo4j={neo4j_val}")
        
        return "; ".join(differences[:5]) if differences else "No significant differences"
    
    def _publish_event(self, event: SyncEvent) -> bool:
        """Publish an event (internal helper)"""
        try:
            return self.publisher.publish_event(event)
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_id}: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get reconciliation job status"""
        return {
            "running": self.running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "total_runs": self.total_runs,
            "total_repairs": self.total_repairs,
            "total_conflicts_detected": self.total_conflicts_detected,
            "config": {
                "interval_seconds": self.sync_config.reconciliation_interval_seconds,
                "batch_size": self.sync_config.reconciliation_batch_size,
                "auto_repair": self.sync_config.auto_repair_enabled
            }
        }
    
    def get_recent_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent reconciliation run history"""
        with self.postgres_manager.get_session() as session:
            runs = session.query(ReconciliationRun).order_by(
                ReconciliationRun.started_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    "run_id": run.run_id,
                    "run_type": run.run_type,
                    "status": run.status,
                    "started_at": run.started_at.isoformat() if run.started_at else None,
                    "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                    "entities_checked": run.entities_checked,
                    "inconsistencies_found": run.inconsistencies_found,
                    "inconsistencies_repaired": run.inconsistencies_repaired,
                    "conflicts_detected": run.conflicts_detected,
                    "duration_seconds": run.duration_seconds
                }
                for run in runs
            ]


def run_reconciliation_job():
    """
    Convenience function to run reconciliation as a standalone job.
    """
    import signal
    import sys
    
    job = ReconciliationJob()
    
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        job.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the job
    job.start()
    
    # Keep running
    while True:
        time.sleep(60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync Reconciliation Job")
    parser.add_argument("--run-once", action="store_true", help="Run reconciliation once and exit")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    job = ReconciliationJob()
    
    if args.run_once:
        result = job.run_reconciliation(run_type="manual")
        print(f"Reconciliation result: {result}")
    else:
        run_reconciliation_job()
