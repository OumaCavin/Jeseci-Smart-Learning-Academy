"""
SQLAlchemy Models for Sync Tracking

This module defines the database models used for tracking synchronization
events and their processing status. These models are stored in PostgreSQL
and provide an audit trail and outbox pattern for reliable event processing.

Models:
- SyncEventLog: Main table for tracking synchronization events
- SyncStatus: Current sync status for each entity
- SyncConflict:记录 detected conflicts between databases
- ReconciliationRun:记录 reconciliation job runs

Author: Jeseci Development Team
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Text, DateTime, Boolean, 
    ForeignKey, Index, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum

from backend.config.database import Base


class SyncEventStatus(str, enum.Enum):
    """
    Status of a synchronization event.
    
    PENDING: Event created but not yet published to message queue
    PUBLISHED: Event published to message queue, awaiting processing
    PROCESSING: Event is currently being processed by consumer
    COMPLETED: Event successfully processed
    FAILED: Event processing failed permanently
    SKIPPED: Event was skipped (e.g., due to conflict)
    """
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ConflictResolutionStatus(str, enum.Enum):
    """
    Status of conflict resolution.
    
    DETECTED: Conflict detected but not yet resolved
    RESOLVED: Conflict successfully resolved
    MANUAL_REVIEW: Conflict requires manual intervention
    IGNORED: Conflict was intentionally ignored
    """
    DETECTED = "DETECTED"
    RESOLVED = "RESOLVED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    IGNORED = "IGNORED"


class SyncEventLog(Base):
    """
    Main table for tracking synchronization events.
    
    This table implements the outbox pattern for reliable event publishing.
    Events are written here first, then published to the message queue.
    This ensures no events are lost even if publishing fails.
    
    The table also serves as an audit log for debugging synchronization issues.
    """
    __tablename__ = "sync_event_log"
    __table_args__ = {"schema": "jeseci_academy"}
    
    # Primary identifiers
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Event payload - contains the actual data to sync
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    
    # Source version for conflict detection
    source_version: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Processing status
    status: Mapped[str] = mapped_column(
        SQLEnum(SyncEventStatus, name="sync_event_status_enum", create_type=False),
        nullable=False,
        default=SyncEventStatus.PENDING,
        index=True
    )
    
    # Retry tracking
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Message queue metadata
    redis_message_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Relationships
    conflicts: Mapped[List["SyncConflict"]] = relationship(
        "SyncConflict", back_populates="event", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<SyncEventLog(event_id={self.event_id}, type={self.event_type}, status={self.status})>"
    
    def to_event(self) -> "SyncEvent":
        """Convert database record to SyncEvent"""
        from .events import SyncEvent, EventType
        
        event_type = self.event_type
        if isinstance(event_type, str):
            event_type = EventType(event_type)
        
        return SyncEvent(
            event_id=self.event_id,
            correlation_id=self.correlation_id,
            event_type=event_type,
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            payload=self.payload,
            source_version=self.source_version,
            retry_count=self.retry_count,
            max_retries=self.max_retries,
            error_message=self.error_message,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat()
        )
    
    def mark_published(self, redis_message_id: str):
        """Mark event as published to message queue"""
        self.status = SyncEventStatus.PUBLISHED
        self.published_at = datetime.now(timezone.utc)
        self.redis_message_id = redis_message_id
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_processing(self):
        """Mark event as currently being processed"""
        self.status = SyncEventStatus.PROCESSING
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_completed(self):
        """Mark event as successfully completed"""
        self.status = SyncEventStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.error_message = None
    
    def mark_failed(self, error_message: str, error_trace: Optional[str] = None):
        """Mark event as failed"""
        self.status = SyncEventStatus.FAILED
        self.error_message = error_message
        self.error_trace = error_trace
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_skipped(self, reason: str):
        """Mark event as skipped (e.g., due to conflict)"""
        self.status = SyncEventStatus.SKIPPED
        self.error_message = reason
        self.updated_at = datetime.now(timezone.utc)
    
    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        self.updated_at = datetime.now(timezone.utc)
        if self.retry_count >= self.max_retries:
            self.status = SyncEventStatus.FAILED
    
    def should_retry(self) -> bool:
        """Check if event should be retried"""
        return self.retry_count < self.max_retries and self.status in [
            SyncEventStatus.PENDING,
            SyncEventStatus.PUBLISHED,
            SyncEventStatus.FAILED
        ]


class SyncStatus(Base):
    """
    Tracks current synchronization status for each entity.
    
    This table provides a quick view of which entities are in sync
    and which have pending changes. It's updated after each
    successful synchronization event.
    """
    __tablename__ = "sync_status"
    __table_args__ = {"schema": "jeseci_academy"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Entity identifiers
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Sync status
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_synced_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Source data version
    source_version: Mapped[int] = mapped_column(Integer, default=0)
    
    # Neo4j data version (for conflict detection)
    neo4j_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    neo4j_checksum: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    
    # Status flags
    has_pending_changes: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    has_conflict: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    conflict_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Error tracking
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )
    
    # Unique constraint
    __table_args__ = (
        {"schema": "jeseci_academy"},
        Index("ix_jeseci_academy_sync_status_entity", "entity_id", "entity_type", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<SyncStatus(entity_id={self.entity_id}, type={self.entity_type}, synced={self.is_synced})>"
    
    def update_after_sync(self, version: int, checksum: Optional[str] = None):
        """Update status after successful synchronization"""
        self.is_synced = True
        self.last_synced_at = datetime.now(timezone.utc)
        self.last_synced_version = version
        self.source_version = version
        self.neo4j_version = version
        self.neo4j_checksum = checksum
        self.has_pending_changes = False
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_pending(self, source_version: int):
        """Mark entity as having pending changes"""
        self.has_pending_changes = True
        self.source_version = source_version
        self.is_synced = False
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_conflict(self, error: str):
        """Mark entity as having a conflict"""
        self.has_conflict = True
        self.conflict_count += 1
        self.last_error = error
        self.updated_at = datetime.now(timezone.utc)
    
    def resolve_conflict(self):
        """Mark conflict as resolved"""
        self.has_conflict = False
        self.last_error = None
        self.updated_at = datetime.now(timezone.utc)


class SyncConflict(Base):
    """
    Records detected conflicts between PostgreSQL and Neo4j.
    
    This table is used for tracking and resolving conflicts that
    occur during synchronization. Conflicts are detected when
    the same entity has been modified in both databases.
    """
    __tablename__ = "sync_conflicts"
    __table_args__ = {"schema": "jeseci_academy"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Entity identifiers
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Conflict details
    conflict_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_version: Mapped[int] = mapped_column(Integer, nullable=False)
    target_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Data comparison
    source_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    target_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    difference_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Resolution
    resolution_status: Mapped[str] = mapped_column(
        SQLEnum(ConflictResolutionStatus, name="conflict_resolution_status_enum", create_type=False),
        nullable=False,
        default=ConflictResolutionStatus.DETECTED
    )
    resolution_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Related event
    event_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("jeseci_academy.sync_event_log.event_id"), nullable=True)
    
    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    event: Mapped[Optional["SyncEventLog"]] = relationship("SyncEventLog", back_populates="conflicts")
    
    def __repr__(self) -> str:
        return f"<SyncConflict(entity_id={self.entity_id}, type={self.conflict_type}, status={self.resolution_status})>"
    
    def mark_resolved(self, method: str, resolved_by: str = "system", notes: Optional[str] = None):
        """Mark conflict as resolved"""
        self.resolution_status = ConflictResolutionStatus.RESOLVED
        self.resolution_method = method
        self.resolved_by = resolved_by
        self.resolution_notes = notes
        self.resolved_at = datetime.now(timezone.utc)
    
    def mark_for_manual_review(self, notes: Optional[str] = None):
        """Mark conflict as requiring manual intervention"""
        self.resolution_status = ConflictResolutionStatus.MANUAL_REVIEW
        self.resolution_notes = notes


class ReconciliationRun(Base):
    """
    Records reconciliation job runs for auditing and debugging.
    
    This table tracks when reconciliation runs, how many entities
    were checked, and what issues were found and repaired.
    """
    __tablename__ = "reconciliation_runs"
    __table_args__ = {"schema": "jeseci_academy"}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Run details
    run_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    run_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # scheduled, manual, triggered
    
    # Statistics
    entities_checked: Mapped[int] = mapped_column(Integer, default=0)
    inconsistencies_found: Mapped[int] = mapped_column(Integer, default=0)
    inconsistencies_repaired: Mapped[int] = mapped_column(Integer, default=0)
    conflicts_detected: Mapped[int] = mapped_column(Integer, default=0)
    conflicts_resolved: Mapped[int] = mapped_column(Integer, default=0)
    failed_entities: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="RUNNING", index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Parameters used
    batch_size: Mapped[int] = mapped_column(Integer, default=50)
    entities_included: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    def __repr__(self) -> str:
        return f"<ReconciliationRun(run_id={self.run_id}, type={self.run_type}, status={self.status})>"
    
    def start(self):
        """Mark run as started"""
        self.status = "RUNNING"
        self.started_at = datetime.now(timezone.utc)
    
    def complete(self):
        """Mark run as completed"""
        self.status = "COMPLETED"
        self.completed_at = datetime.now(timezone.utc)
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.duration_seconds = duration
    
    def fail(self, error: str):
        """Mark run as failed"""
        self.status = "FAILED"
        self.error_message = error
        self.completed_at = datetime.now(timezone.utc)
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.duration_seconds = duration
    
    def add_stats(self, **kwargs):
        """Add statistics to run"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                current_value = getattr(self, key)
                if isinstance(current_value, int):
                    setattr(self, key, current_value + value)
                else:
                    setattr(self, key, value)


def create_sync_tables(engine):
    """Create all sync-related tables in the database"""
    from sqlalchemy import text
    from ..config.database import get_postgres_engine
    
    # Create enum types if they don't exist
    with engine.connect() as conn:
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE sync_event_status_enum AS ENUM ('PENDING', 'PUBLISHED', 'PROCESSING', 'COMPLETED', 'FAILED', 'SKIPPED');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE conflict_resolution_status_enum AS ENUM ('DETECTED', 'RESOLVED', 'MANUAL_REVIEW', 'IGNORED');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(engine)
