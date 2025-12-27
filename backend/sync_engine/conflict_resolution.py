"""
Conflict Detection and Resolution for Sync Engine

This module provides conflict detection and resolution mechanisms for
handling inconsistencies between PostgreSQL and Neo4j databases.

Conflict Resolution Strategies:
- LAST_WRITE_WINS: Use the most recent version
- SOURCE_WINS: Always use PostgreSQL as source of truth
- MANUAL_REVIEW: Flag for manual intervention
- MERGE: Attempt to merge conflicting changes

Author: Cavin Otieno
"""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

from backend.sync_engine.config import get_sync_config
from backend.sync_engine.database import get_postgres_sync_manager, get_neo4j_sync_manager
from backend.sync_engine.models import SyncConflict, SyncStatus, ConflictResolutionStatus

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    """Types of conflicts that can occur during synchronization"""
    VERSION_MISMATCH = "VERSION_MISMATCH"
    DATA_DIVERGENCE = "DATA_DIVERGENCE"
    DELETION_CONFLICT = "DELETION_CONFLICT"
    RELATIONSHIP_CONFLICT = "RELATIONSHIP_CONFLICT"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"


class ResolutionStrategy(str, Enum):
    """Strategies for resolving conflicts"""
    LAST_WRITE_WINS = "LAST_WRITE_WINS"
    SOURCE_WINS = "SOURCE_WINS"
    TARGET_WINS = "TARGET_WINS"
    MERGE = "MERGE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    IGNORE = "IGNORE"


@dataclass
class ConflictInfo:
    """Information about a detected conflict"""
    entity_id: str
    entity_type: str
    conflict_type: ConflictType
    source_data: Dict[str, Any]
    target_data: Dict[str, Any]
    source_version: int
    target_version: int
    source_updated_at: datetime
    target_updated_at: datetime
    differences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "conflict_type": self.conflict_type.value,
            "source_version": self.source_version,
            "target_version": self.target_version,
            "differences": self.differences
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)


class ConflictDetector:
    """
    Detects conflicts between PostgreSQL and Neo4j data.
    
    This class compares entity data between the two databases
    and identifies conflicts based on various criteria.
    """
    
    def __init__(self):
        self.postgres_manager = get_postgres_sync_manager()
        self.neo4j_manager = get_neo4j_sync_manager()
    
    def detect_conflicts(
        self, 
        entity_type: str, 
        entity_id: str
    ) -> Optional[ConflictInfo]:
        """
        Detect conflicts for a specific entity.
        
        Args:
            entity_type: Type of entity (concept, learning_path)
            entity_id: ID of the entity
            
        Returns:
            ConflictInfo if conflict detected, None otherwise
        """
        # Get data from both databases
        source_data = self._get_source_data(entity_type, entity_id)
        target_data = self._get_target_data(entity_type, entity_id)
        
        if not source_data and not target_data:
            return None
        
        if not source_data:
            # Exists only in Neo4j - not a conflict
            return None
        
        if not target_data:
            # Exists only in PostgreSQL - not a conflict, will be synced
            return None
        
        # Check for conflicts
        conflict = self._check_version_conflict(entity_type, source_data, target_data)
        if conflict:
            return conflict
        
        conflict = self._check_data_divergence(entity_type, source_data, target_data)
        if conflict:
            return conflict
        
        return None
    
    def _get_source_data(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity data from PostgreSQL (source)"""
        table_map = {
            "concept": "concepts",
            "learning_path": "learning_paths"
        }
        
        table = table_map.get(entity_type)
        if not table:
            return None
        
        # Get schema from configuration
        from backend.sync_engine.config import get_sync_config
        config = get_sync_config()
        schema = config.postgres_schema
        id_field = "concept_id" if entity_type == "concept" else "path_id"
        
        query = f"""
        SELECT * FROM {schema}.{table}
        WHERE {id_field} = %s
        """
        
        results = self.postgres_manager.execute_query(query, (entity_id,))
        if results:
            data = results[0]
            # Convert datetime fields
            for key, value in data.items():
                if hasattr(value, 'isoformat'):
                    data[key] = value.isoformat()
            return data
        
        return None
    
    def _get_target_data(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity data from Neo4j (target)"""
        label_map = {
            "concept": "Concept",
            "learning_path": "LearningPath"
        }
        
        label = label_map.get(entity_type)
        if not label:
            return None
        
        property_name = "concept_id" if entity_type == "concept" else "path_id"
        node = self.neo4j_manager.get_node(label, property_name, entity_id)
        
        if node:
            # Convert Neo4j types to serializable
            for key, value in node.items():
                if hasattr(value, 'isoformat'):
                    node[key] = value.isoformat()
                elif hasattr(value, 'timestamp'):
                    node[key] = value.timestamp()
            return node
        
        return None
    
    def _check_version_conflict(
        self, 
        entity_type: str,
        source_data: Dict[str, Any], 
        target_data: Dict[str, Any]
    ) -> Optional[ConflictInfo]:
        """
        Check for version conflicts.
        
        A version conflict occurs when both databases have been modified
        independently after the last synchronization.
        """
        # Get last sync time from Neo4j
        last_sync = target_data.get("last_synced_at")
        if last_sync:
            if hasattr(last_sync, 'timestamp'):
                last_sync_ts = last_sync
            else:
                last_sync_ts = datetime.fromisoformat(str(last_sync))
        else:
            last_sync_ts = datetime.min
        
        # Get update times
        source_updated = source_data.get("updated_at")
        target_updated = target_data.get("updated_at")
        
        if hasattr(source_updated, 'timestamp'):
            source_updated_ts = source_updated
        elif source_updated:
            source_updated_ts = datetime.fromisoformat(str(source_updated))
        else:
            source_updated_ts = datetime.min
        
        if hasattr(target_updated, 'timestamp'):
            target_updated_ts = target_updated
        elif target_updated:
            target_updated_ts = datetime.fromisoformat(str(target_updated))
        else:
            target_updated_ts = datetime.min
        
        # Check if both were modified after last sync
        if source_updated_ts > last_sync_ts and target_updated_ts > last_sync_ts:
            # Conflict detected
            return ConflictInfo(
                entity_id=source_data.get("concept_id") or source_data.get("path_id") or "",
                entity_type=entity_type,
                conflict_type=ConflictType.VERSION_MISMATCH,
                source_data=source_data,
                target_data=target_data,
                source_version=int(source_updated_ts.timestamp()),
                target_version=int(target_updated_ts.timestamp()),
                source_updated_at=source_updated_ts,
                target_updated_at=target_updated_ts
            )
        
        return None
    
    def _check_data_divergence(
        self,
        entity_type: str,
        source_data: Dict[str, Any],
        target_data: Dict[str, Any]
    ) -> Optional[ConflictInfo]:
        """
        Check for data divergence (content differences).
        
        Data divergence occurs when the same entity exists in both databases
        but has different content in key fields.
        """
        # Compare key fields
        key_fields = ["name", "display_name", "description", "category"]
        differences = {}
        
        for field in key_fields:
            source_val = source_data.get(field)
            target_val = target_data.get(field)
            
            # Normalize for comparison
            if source_val and hasattr(source_val, 'isoformat'):
                source_val = source_val.isoformat()
            if target_val and hasattr(target_val, 'isoformat'):
                target_val = target_val.isoformat()
            
            if source_val != target_val:
                differences[field] = {
                    "source": source_val,
                    "target": target_val
                }
        
        if differences:
            source_updated = source_data.get("updated_at", datetime.min)
            target_updated = target_data.get("updated_at", datetime.min)
            
            if hasattr(source_updated, 'timestamp'):
                source_version = int(source_updated.timestamp())
            elif source_updated:
                source_version = int(datetime.fromisoformat(str(source_updated)).timestamp())
            else:
                source_version = 0
            
            if hasattr(target_updated, 'timestamp'):
                target_version = int(target_updated.timestamp())
            elif target_updated:
                target_version = int(datetime.fromisoformat(str(target_updated)).timestamp())
            else:
                target_version = 0
            
            return ConflictInfo(
                entity_id=source_data.get("concept_id") or source_data.get("path_id") or "",
                entity_type=entity_type,
                conflict_type=ConflictType.DATA_DIVERGENCE,
                source_data=source_data,
                target_data=target_data,
                source_version=source_version,
                target_version=target_version,
                source_updated_at=source_updated if isinstance(source_updated, datetime) else datetime.min,
                target_updated_at=target_updated if isinstance(target_updated, datetime) else datetime.min,
                differences=differences
            )
        
        return None
    
    def batch_detect_conflicts(
        self,
        entity_type: str,
        entity_ids: List[str]
    ) -> List[ConflictInfo]:
        """
        Detect conflicts for multiple entities.
        
        Args:
            entity_type: Type of entities
            entity_ids: List of entity IDs to check
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        for entity_id in entity_ids:
            conflict = self.detect_conflicts(entity_type, entity_id)
            if conflict:
                conflicts.append(conflict)
        
        return conflicts


class ConflictResolver:
    """
    Resolves conflicts between PostgreSQL and Neo4j data.
    
    This class implements various resolution strategies and applies
    them to resolve detected conflicts.
    """
    
    def __init__(self):
        self.sync_config = get_sync_config()
        self.postgres_manager = get_postgres_sync_manager()
        self.neo4j_manager = get_neo4j_sync_manager()
        self.detector = ConflictDetector()
    
    def resolve_conflict(
        self,
        conflict: ConflictInfo,
        strategy: ResolutionStrategy = None,
        resolved_by: str = "system"
    ) -> bool:
        """
        Resolve a detected conflict using the specified strategy.
        
        Args:
            conflict: Conflict information
            strategy: Resolution strategy to use
            resolved_by: Identifier for who/what resolved the conflict
            
        Returns:
            True if resolved successfully, False otherwise
        """
        if strategy is None:
            strategy = self._get_default_strategy(conflict.conflict_type)
        
        logger.info(f"Resolving conflict for {conflict.entity_id} using {strategy.value}")
        
        try:
            if strategy == ResolutionStrategy.LAST_WRITE_WINS:
                return self._resolve_last_write_wins(conflict, resolved_by)
            elif strategy == ResolutionStrategy.SOURCE_WINS:
                return self._resolve_source_wins(conflict, resolved_by)
            elif strategy == ResolutionStrategy.TARGET_WINS:
                return self._resolve_target_wins(conflict, resolved_by)
            elif strategy == ResolutionStrategy.MERGE:
                return self._resolve_merge(conflict, resolved_by)
            elif strategy == ResolutionStrategy.MANUAL_REVIEW:
                return self._mark_for_manual_review(conflict)
            elif strategy == ResolutionStrategy.IGNORE:
                return self._ignore_conflict(conflict)
            else:
                logger.error(f"Unknown resolution strategy: {strategy}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to resolve conflict {conflict.entity_id}: {e}")
            return False
    
    def _get_default_strategy(self, conflict_type: ConflictType) -> ResolutionStrategy:
        """Get default resolution strategy for conflict type"""
        if conflict_type == ConflictType.VERSION_MISMATCH:
            return ResolutionStrategy.LAST_WRITE_WINS
        elif conflict_type == ConflictType.DATA_DIVERGENCE:
            return ResolutionStrategy.MERGE
        else:
            return ResolutionStrategy.MANUAL_REVIEW
    
    def _resolve_last_write_wins(
        self,
        conflict: ConflictInfo,
        resolved_by: str
    ) -> bool:
        """Resolve using last-write-wins strategy"""
        # Determine which is newer
        if conflict.source_updated_at >= conflict.target_updated_at:
            # Source is newer, sync to Neo4j
            return self._sync_to_neo4j(conflict.source_data, conflict.entity_type, resolved_by)
        else:
            # Target is newer, sync to PostgreSQL
            return self._sync_to_postgres(conflict.target_data, conflict.entity_type, resolved_by)
    
    def _resolve_source_wins(
        self,
        conflict: ConflictInfo,
        resolved_by: str
    ) -> bool:
        """Resolve by always using PostgreSQL as source of truth"""
        return self._sync_to_neo4j(conflict.source_data, conflict.entity_type, resolved_by)
    
    def _resolve_target_wins(
        self,
        conflict: ConflictInfo,
        resolved_by: str
    ) -> bool:
        """Resolve by always using Neo4j as source of truth"""
        return self._sync_to_postgres(conflict.target_data, conflict.entity_type, resolved_by)
    
    def _resolve_merge(
        self,
        conflict: ConflictInfo,
        resolved_by: str
    ) -> bool:
        """Resolve by merging changes from both sources"""
        # For now, use last-write-wins for simplicity
        # A more sophisticated implementation would merge field by field
        return self._resolve_last_write_wins(conflict, resolved_by)
    
    def _mark_for_manual_review(self, conflict: ConflictInfo) -> bool:
        """Mark conflict for manual review"""
        logger.info(f"Marking conflict {conflict.entity_id} for manual review")
        return True  # Conflict is already marked in the database
    
    def _ignore_conflict(self, conflict: ConflictInfo) -> bool:
        """Ignore the conflict"""
        logger.info(f"Ignoring conflict {conflict.entity_id}")
        return True
    
    def _sync_to_neo4j(
        self,
        data: Dict[str, Any],
        entity_type: str,
        resolved_by: str
    ) -> bool:
        """Sync data from PostgreSQL to Neo4j"""
        if entity_type == "concept":
            return self._sync_concept_to_neo4j(data, resolved_by)
        elif entity_type == "learning_path":
            return self._sync_learning_path_to_neo4j(data, resolved_by)
        return False
    
    def _sync_to_postgres(
        self,
        data: Dict[str, Any],
        entity_type: str,
        resolved_by: str
    ) -> bool:
        """Sync data from Neo4j to PostgreSQL"""
        # This would require reverse sync capability
        logger.warning("Sync to PostgreSQL not yet implemented")
        return False
    
    def _sync_concept_to_neo4j(
        self,
        data: Dict[str, Any],
        resolved_by: str
    ) -> bool:
        """Sync a concept to Neo4j"""
        query = """
        MERGE (c:Concept {concept_id: $concept_id})
        SET c = $data,
            c.resolved_by = $resolved_by,
            c.resolved_at = datetime(),
            c.updated_at = datetime()
        """
        
        # Prepare data for Neo4j
        neo4j_data = {
            "concept_id": data.get("concept_id", ""),
            "name": data.get("name", ""),
            "display_name": data.get("display_name", ""),
            "category": data.get("category", ""),
            "subcategory": data.get("subcategory", ""),
            "domain": data.get("domain", ""),
            "difficulty_level": data.get("difficulty_level", ""),
            "description": data.get("description", ""),
            "detailed_description": data.get("detailed_description", ""),
            "source_version": data.get("updated_at", 0)
        }
        
        success = self.neo4j_manager.execute_write(query, {
            "concept_id": neo4j_data["concept_id"],
            "data": neo4j_data,
            "resolved_by": resolved_by
        })
        
        if success:
            self._update_sync_status(data.get("concept_id", ""), "concept", True)
        
        return success
    
    def _sync_learning_path_to_neo4j(
        self,
        data: Dict[str, Any],
        resolved_by: str
    ) -> bool:
        """Sync a learning path to Neo4j"""
        query = """
        MERGE (p:LearningPath {path_id: $path_id})
        SET p = $data,
            p.resolved_by = $resolved_by,
            p.resolved_at = datetime(),
            p.updated_at = datetime()
        """
        
        # Prepare data for Neo4j
        neo4j_data = {
            "path_id": data.get("path_id", ""),
            "name": data.get("name", ""),
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "category": data.get("category", ""),
            "difficulty_level": data.get("difficulty_level", ""),
            "source_version": data.get("updated_at", 0)
        }
        
        success = self.neo4j_manager.execute_write(query, {
            "path_id": neo4j_data["path_id"],
            "data": neo4j_data,
            "resolved_by": resolved_by
        })
        
        if success:
            self._update_sync_status(data.get("path_id", ""), "learning_path", True)
        
        return success
    
    def _update_sync_status(
        self,
        entity_id: str,
        entity_type: str,
        conflict_resolved: bool
    ):
        """Update sync status after conflict resolution"""
        with self.postgres_manager.get_session() as session:
            status = session.query(SyncStatus).filter(
                SyncStatus.entity_id == entity_id,
                SyncStatus.entity_type == entity_type
            ).first()
            
            if status:
                if conflict_resolved:
                    status.resolve_conflict()
                status.is_synced = True
                status.last_synced_at = datetime.now(timezone.utc)
                session.flush()
    
    def auto_resolve_conflicts(
        self,
        conflicts: List[ConflictInfo],
        strategy: ResolutionStrategy = None
    ) -> Dict[str, int]:
        """
        Automatically resolve a list of conflicts.
        
        Args:
            conflicts: List of conflicts to resolve
            strategy: Resolution strategy to use
            
        Returns:
            Dictionary with resolution results
        """
        results = {
            "resolved": 0,
            "failed": 0,
            "manual_review": 0,
            "ignored": 0
        }
        
        for conflict in conflicts:
            success = self.resolve_conflict(conflict, strategy)
            
            if success:
                if strategy == ResolutionStrategy.MANUAL_REVIEW:
                    results["manual_review"] += 1
                elif strategy == ResolutionStrategy.IGNORE:
                    results["ignored"] += 1
                else:
                    results["resolved"] += 1
            else:
                results["failed"] += 1
        
        return results


def get_conflict_detector() -> ConflictDetector:
    """Get a ConflictDetector instance"""
    return ConflictDetector()


def get_conflict_resolver() -> ConflictResolver:
    """Get a ConflictResolver instance"""
    return ConflictResolver()


def detect_and_resolve_conflicts(
    entity_type: str,
    entity_id: str,
    strategy: ResolutionStrategy = None
) -> Dict[str, Any]:
    """
    Convenience function to detect and resolve a conflict.
    
    Args:
        entity_type: Type of entity
        entity_id: ID of entity
        strategy: Resolution strategy
        
    Returns:
        Dictionary with detection and resolution results
    """
    detector = get_conflict_detector()
    resolver = get_conflict_resolver()
    
    # Detect conflict
    conflict = detector.detect_conflicts(entity_type, entity_id)
    
    if not conflict:
        return {
            "detected": False,
            "message": "No conflict detected"
        }
    
    # Resolve conflict
    success = resolver.resolve_conflict(conflict, strategy)
    
    return {
        "detected": True,
        "conflict_type": conflict.conflict_type.value,
        "resolved": success,
        "strategy": strategy.value if strategy else resolver._get_default_strategy(conflict.conflict_type).value
    }
