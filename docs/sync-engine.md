# Sync Engine Documentation

This document provides a comprehensive guide to the event-driven synchronization system that maintains eventual consistency between PostgreSQL and Neo4j databases in the Jeseci Smart Learning Academy project.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Database Migration](#database-migration)
4. [Event Publisher](#event-publisher)
5. [Event Consumer](#event-consumer)
6. [Reconciliation Job](#reconciliation-job)
7. [Conflict Resolution](#conflict-resolution)
8. [Event Types](#event-types)
9. [Configuration](#configuration)
10. [Quick Start](#quick-start)

---

## Overview

The Sync Engine is an event-driven data synchronization system that ensures data consistency between two different databases:

- **PostgreSQL**: Primary database for transactional data (users, content, progress)
- **Neo4j**: Graph database for relationships and knowledge graph traversal

The system uses the **Outbox Pattern** with Redis as a message queue to provide reliable, eventual consistency without tight coupling between the databases.

### Key Features

- **Event-Driven Architecture**: Changes publish events instead of directly modifying both databases
- **Outbox Pattern**: Events are written to a local table first, then published to the message queue
- **Retry Mechanism**: Failed events can be retried with exponential backoff
- **Conflict Detection**: Identifies when the same entity is modified in both databases
- **Reconciliation Job**: Periodically compares databases and repairs inconsistencies

---

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   Application       │     │   Message Queue     │     │   Consumer          │
│   (Content Create)  │────▶│   (Redis)           │────▶│   (Event Handler)   │
│                     │     │                     │     │                     │
│  1. Write to DB     │     │  3. Publish Event   │     │  4. Process Event   │
│  2. Write to Outbox │     │                     │     │  5. Update Neo4j    │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
         │                                                   │
         │                                                   │
         └───────────────────┬─────────────────────────────────┘
                             │
                     ┌───────▼───────┐
                     │   Database    │
                     │   (PostgreSQL)│
                     │               │
                     │  - Content    │
                     │  - Users      │
                     │  - Sync Events│
                     └───────────────┘
```

### Components

| Component | File | Purpose |
|-----------|------|---------|
| Event Publisher | `sync_engine/publisher.py` | Publishes sync events to Redis |
| Event Consumer | `sync_engine/consumer.py` | Processes events from Redis |
| Reconciliation | `sync_engine/reconciliation.py` | Compares and repairs inconsistencies |
| Conflict Resolution | `sync_engine/conflict_resolution.py` | Detects and resolves conflicts |
| Event Definitions | `sync_engine/events.py` | Event type definitions |
| Database Models | `sync_engine/models.py` | ORM models for sync tables |
| Configuration | `sync_engine/config.py` | Configuration management |

---

## Database Migration

Before using the sync engine, you must create the required tables in PostgreSQL.

### SQL Migration Script

**File:** `backend/migrations/001_create_sync_engine_tables.sql`

**Usage:**

```bash
# Using psql directly
psql -h localhost -p 5432 -U jeseci_academy_user -d jeseci_learning_academy \
    -f backend/migrations/001_create_sync_engine_tables.sql

# Using Docker
docker exec -i <container_name> psql -U jeseci_academy_user -d jeseci_learning_academy \
    < backend/migrations/001_create_sync_engine_tables.sql
```

### Python Migration Script

**File:** `backend/migrations/001_create_sync_engine_tables.py`

**Usage:**

```bash
cd backend
python migrations/001_create_sync_engine_tables.py
```

### Tables Created

| Table | Purpose |
|-------|---------|
| `sync_event_log` | Tracks synchronization events (outbox pattern) |
| `sync_status` | Current sync status for each entity |
| `sync_conflicts` | Records detected conflicts between databases |
| `reconciliation_runs` | Records reconciliation job runs for auditing |

---

## Event Publisher

**File:** `backend/sync_engine/publisher.py`

Publishes sync events when content is created or updated.

### Usage

```python
from sync_engine.publisher import get_sync_publisher

# Get publisher instance
publisher = get_sync_publisher()

# Publish content creation event
publisher.publish_content_created(
    entity_id="concept-123",
    entity_type="concept",
    payload={
        "title": "Introduction to Python",
        "content": "Python is a versatile programming language...",
        "author_id": "user-456"
    },
    correlation_id="user-session-789"
)

# Publish content update event
publisher.publish_content_updated(
    entity_id="concept-123",
    entity_type="concept",
    payload={"title": "Updated Python Guide"},
    source_version=2
)

# Publish content deletion event
publisher.publish_content_deleted(
    entity_id="concept-123",
    entity_type="concept",
    source_version=3
)
```

### Integration Example

Add to your content creation endpoints:

```python
from sync_engine.publisher import get_sync_publisher

def create_concept(concept_data):
    # 1. Save to PostgreSQL
    concept = save_concept_to_db(concept_data)
    
    # 2. Publish sync event
    publisher = get_sync_publisher()
    publisher.publish_content_created(
        entity_id=concept.id,
        entity_type="concept",
        payload=concept_data,
        correlation_id=get_correlation_id()
    )
    
    return concept
```

---

## Event Consumer

**File:** `backend/sync_engine/consumer.py`

Processes sync events from Redis and updates Neo4j.

### Usage

```python
from sync_engine.consumer import run_consumer

# Run the consumer (blocking)
run_consumer()

# Run with custom settings
run_consumer(
    batch_size=10,      # Process 10 events at a time
    poll_interval=5     # Poll Redis every 5 seconds
)
```

### Run as Background Service

```bash
# Using systemd (Linux)
# Create /etc/systemd/system/sync-consumer.service

[Unit]
Description=Sync Engine Consumer
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/python -c "from sync_engine.consumer import run_consumer; run_consumer()"
Restart=always

[Install]
WantedBy=multi-user.target

# Then run:
sudo systemctl enable sync-consumer
sudo systemctl start sync-consumer
```

### Using Supervisor

```ini
# /etc/supervisor/conf.d/sync-consumer.conf
[program:sync-consumer]
command=/path/to/venv/bin/python -c "from sync_engine.consumer import run_consumer; run_consumer()"
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/sync-consumer.err.log
stdout_logfile=/var/log/sync-consumer.out.log
```

---

## Reconciliation Job

**File:** `backend/sync_engine/reconciliation.py`

Periodically compares PostgreSQL and Neo4j data to find and repair inconsistencies.

### Usage

```python
from sync_engine.reconciliation import ReconciliationJob

# Create job instance
job = ReconciliationJob()

# Run full reconciliation for all entity types
job.run_full_reconciliation()

# Run for specific entity types only
job.run_full_reconciliation(entity_types=["concept", "learning_path"])

# Run for specific entities
job.run_full_reconciliation(
    entity_ids=["concept-123", "path-456"],
    entity_types=["concept"]
)

# Run with custom batch size
job.run_full_reconciliation(batch_size=100)
```

### Schedule as Cron Job

```bash
# Run reconciliation every hour
0 * * * * cd /path/to/project && python -c "
from sync_engine.reconciliation import ReconciliationJob
ReconciliationJob().run_full_reconciliation()
" >> /var/log/reconciliation.log 2>&1

# Run reconciliation every night at 2 AM
0 2 * * * cd /path/to/project && python -c "
from sync_engine.reconciliation import ReconciliationJob
ReconciliationJob().run_full_reconciliation()
" >> /var/log/reconciliation-nightly.log 2>&1
```

### Command Line Interface

Create a CLI script:

```python
#!/usr/bin/env python
# reconcile.py
import sys
from sync_engine.reconciliation import ReconciliationJob

if __name__ == "__main__":
    entity_types = sys.argv[1:] if len(sys.argv) > 1 else None
    batch_size = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 50
    
    job = ReconciliationJob()
    job.run_full_reconciliation(
        entity_types=entity_types,
        batch_size=batch_size
    )
```

```bash
# Usage
python reconcile.py                    # All entities
python reconcile.py concept            # Specific type
python reconcile.py concept path       # Multiple types
python reconcile.py concept 100        # Custom batch size
```

---

## Conflict Resolution

**File:** `backend/sync_engine/conflict_resolution.py`

Detects and resolves conflicts when the same entity is modified in both databases.

### Usage

```python
from sync_engine.conflict_resolution import ConflictResolver, ResolutionStrategy

# Create resolver with strategy
resolver = ConflictResolver(strategy=ResolutionStrategy.LAST_WRITE_WINS)

# Check for conflicts
if resolver.has_conflict(entity_id="concept-123", entity_type="concept"):
    print("Conflict detected!")

# Get conflict details
conflict = resolver.get_conflict(entity_id="concept-123", entity_type="concept")
if conflict:
    print(f"Source version: {conflict.source_version}")
    print(f"Target version: {conflict.target_version}")
    print(f"Source data: {conflict.source_data}")
    print(f"Target data: {conflict.target_data}")

# Resolve conflict using strategy
resolved = resolver.resolve_conflict(
    entity_id="concept-123",
    entity_type="concept",
    method=ResolutionStrategy.SOURCE_WINS  # Use PostgreSQL as source of truth
)

# Manual resolution with notes
resolved = resolver.resolve_conflict(
    entity_id="concept-123",
    entity_type="concept",
    method=ResolutionStrategy.MANUAL_REVIEW,
    resolved_by="admin-user",
    resolution_notes="Merged both changes manually"
)
```

### Resolution Strategies

| Strategy | Description |
|----------|-------------|
| `LAST_WRITE_WINS` | Use the version with the higher source_version |
| `SOURCE_WINS` | Always use PostgreSQL as the source of truth |
| `TARGET_WINS` | Always use Neo4j as the source of truth |
| `MANUAL_REVIEW` | Flag for manual intervention |
| `MERGE` | Attempt to merge conflicting changes |

---

## Event Types

**File:** `backend/sync_engine/events.py`

### Available Event Types

```python
from sync_engine.events import EventType

# Content events
EventType.CONTENT_CREATED
EventType.CONTENT_UPDATED
EventType.CONTENT_DELETED

# Relationship events
EventType.RELATIONSHIP_CREATED
EventType.RELATIONSHIP_DELETED

# User events
EventType.USER_CREATED
EventType.USER_UPDATED
EventType.USER_DELETED
```

### Event Structure

```python
from sync_engine.events import SyncEvent, EventType

# Create event
event = SyncEvent(
    event_id="evt-789",              # Unique event ID
    correlation_id="corr-123",        # For tracing related events
    event_type=EventType.CONTENT_CREATED,
    entity_id="concept-123",          # Entity identifier
    entity_type="concept",            # Entity type
    payload={"title": "New Concept"}, # Event data
    source_version=1                  # Version for conflict detection
)

# Convert to dict for serialization
event_dict = event.to_dict()

# Restore from dict
restored_event = SyncEvent.from_dict(event_dict)
```

---

## Configuration

### Environment Variables

Add to `backend/config/.env`:

```bash
# Redis (Message Queue)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1
REDIS_PASSWORD=

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jeseci_learning_academy
POSTGRES_USER=jeseci_academy_user
POSTGRES_PASSWORD=jeseci_secure_password_2024
POSTGRES_SCHEMA=jeseci_academy

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_secure_password_2024
NEO4J_DATABASE=neo4j

# Sync Engine Settings
SYNC_BATCH_SIZE=50
SYNC_RETRY_MAX=3
SYNC_POLL_INTERVAL=5
```

### Configuration File

**File:** `backend/sync_engine/config.py`

```python
from sync_engine.config import get_sync_config, SyncConfig

# Get configuration
config = get_sync_config()

# Access settings
print(f"PostgreSQL: {config.postgres_host}:{config.postgres_port}/{config.postgres_db}")
print(f"Neo4j: {config.neo4j_uri}")
print(f"Redis: {config.redis_host}:{config.redis_port}")
print(f"Batch size: {config.batch_size}")
print(f"Max retries: {config.max_retries}")
```

---

## Quick Start

### Step 1: Run Database Migration

```bash
cd backend
python migrations/001_create_sync_engine_tables.py
```

### Step 2: Configure Environment

Ensure `backend/config/.env` has all required variables:

```bash
# Check or create .env file
cat backend/config/.env
```

### Step 3: Start the Consumer

```bash
# Terminal 1: Start the event consumer
cd backend
python -c "from sync_engine.consumer import run_consumer; run_consumer()"
```

### Step 4: Integrate with Your Application

```python
# In your content creation/update code
from sync_engine.publisher import get_sync_publisher

def create_content(content_data):
    # 1. Save to PostgreSQL (your existing code)
    content = save_to_database(content_data)
    
    # 2. Publish sync event
    publisher = get_sync_publisher()
    publisher.publish_content_created(
        entity_id=content.id,
        entity_type="concept",
        payload=content_data,
        correlation_id=get_current_user_id()
    )
    
    return content

def update_content(content_id, updates):
    # 1. Get current version
    current = get_from_database(content_id)
    
    # 2. Update in PostgreSQL
    updated = update_in_database(content_id, updates)
    
    # 3. Publish sync event
    publisher = get_sync_publisher()
    publisher.publish_content_updated(
        entity_id=content_id,
        entity_type="concept",
        payload=updates,
        source_version=current.version + 1
    )
    
    return updated
```

### Step 5: Run Periodic Reconciliation

```bash
# Add to crontab for hourly reconciliation
crontab -e

# Add this line:
0 * * * * cd /path/to/project && python -c "
from sync_engine.reconciliation import ReconciliationJob
ReconciliationJob().run_full_reconciliation()
" >> /var/log/reconciliation.log 2>&1
```

---

## Monitoring

### Check Sync Status

```python
from sync_engine.database import get_postgres_sync_manager
from sqlalchemy.orm import Session
from sync_engine.models import SyncStatus

# Get sync status for all entities
manager = get_postgres_sync_manager()
with manager.get_session() as session:
    pending = session.query(SyncStatus).filter(
        SyncStatus.has_pending_changes == True
    ).all()
    
    conflicts = session.query(SyncStatus).filter(
        SyncStatus.has_conflict == True
    ).all()
    
    print(f"Pending syncs: {len(pending)}")
    print(f"Conflicts: {len(conflicts)}")
```

### View Event Log

```sql
-- Check pending events
SELECT * FROM jeseci_academy.sync_event_log
WHERE status = 'PENDING'
ORDER BY created_at DESC;

-- Check failed events
SELECT * FROM jeseci_academy.sync_event_log
WHERE status = 'FAILED'
ORDER BY updated_at DESC
LIMIT 10;

-- Check event processing time
SELECT 
    event_type,
    COUNT(*) as total,
    AVG(EXTRACT(EPOCH FROM (completed_at - published_at))) as avg_processing_seconds
FROM jeseci_academy.sync_event_log
WHERE status = 'COMPLETED'
GROUP BY event_type;
```

---

## Troubleshooting

### Consumer Not Processing Events

1. Check Redis connection:
   ```python
   from sync_engine.config import get_sync_config
   config = get_sync_config()
   print(f"Redis: {config.redis_host}:{config.redis_port}")
   ```

2. Check for pending events:
   ```sql
   SELECT COUNT(*) FROM jeseci_academy.sync_event_log
   WHERE status = 'PENDING';
   ```

3. Check consumer logs for errors.

### Conflicts Not Being Detected

1. Ensure `source_version` is being incremented on updates
2. Check that Neo4j data has version information
3. Verify conflict detection is enabled in configuration

### Reconciliation Finding Too Many Inconsistencies

1. Run reconciliation during low-traffic hours
2. Use batch processing with smaller batch sizes
3. Check for data that should be entity-specific

---

## File Structure

```
backend/
├── sync_engine/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connections
│   ├── events.py           # Event type definitions
│   ├── models.py           # SQLAlchemy ORM models
│   ├── publisher.py        # Event publishing
│   ├── consumer.py         # Event consumption
│   ├── reconciliation.py   # Reconciliation jobs
│   └── conflict_resolution.py  # Conflict handling
├── migrations/
│   ├── 001_create_sync_engine_tables.py
│   └── 001_create_sync_engine_tables.sql
└── config/
    └── .env                # Environment variables
```

---

## Author

**Cavin Otieno**

---

## License

MIT License
