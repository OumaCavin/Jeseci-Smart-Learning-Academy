-- =============================================================================
-- Database Migration Script: Create Sync Engine Tables
-- =============================================================================
--
-- This SQL script creates the tables required for the event-driven synchronization
-- system that maintains eventual consistency between PostgreSQL and Neo4j databases.
--
-- Usage:
--     psql -h <host> -p <port> -U <user> -d <database> -f this_file.sql
--
-- Or from the backend directory:
--     python -c "
--     import os
--     os.environ['POSTGRES_HOST'] = 'localhost'
--     os.environ['POSTGRES_PORT'] = '5432'
--     os.environ['POSTGRES_DB'] = 'jeseci_learning_academy'
--     os.environ['POSTGRES_USER'] = 'jeseci_academy_user'
--     os.environ['POSTGRES_PASSWORD'] = 'jeseci_secure_password_2024'
--     
--     from sqlalchemy import create_engine, text
--     
--     engine = create_engine(
--         f\"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}\"
--         f\"@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}\"
--     )
--     
--     with open('migrations/001_create_sync_engine_tables.sql', 'r') as f:
--         sql = f.read()
--     
--     with engine.connect() as conn:
--         conn.execute(text(sql))
--         conn.commit()
--     
--     print('Migration applied successfully!')
--     "
--
-- Tables Created:
-- - sync_event_log: Main table for tracking synchronization events (outbox pattern)
-- - sync_status: Tracks current synchronization status for each entity
-- - sync_conflicts: Records detected conflicts between PostgreSQL and Neo4j
-- - reconciliation_runs: Records reconciliation job runs for auditing
--
-- Author: Cavin Otieno
-- Date: 2025-12-26
--
-- =============================================================================

-- =============================================================================
-- Step 0: Set schema search path
-- =============================================================================
-- Ensure all objects are created in the jeseci_academy schema
SET search_path TO jeseci_academy, public;

-- =============================================================================
-- Step 1: Create custom enum types
-- =============================================================================

-- Create sync_event_status_enum if it doesn't exist
DO $$ BEGIN
    CREATE TYPE sync_event_status_enum AS ENUM (
        'PENDING', 'PUBLISHED', 'PROCESSING', 
        'COMPLETED', 'FAILED', 'SKIPPED'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create conflict_resolution_status_enum if it doesn't exist
DO $$ BEGIN
    CREATE TYPE conflict_resolution_status_enum AS ENUM (
        'DETECTED', 'RESOLVED', 'MANUAL_REVIEW', 'IGNORED'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- =============================================================================
-- Step 2: Create sync_event_log table
-- =============================================================================

CREATE TABLE IF NOT EXISTS jeseci_academy.sync_event_log (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(64) NOT NULL UNIQUE,
    correlation_id VARCHAR(64) NOT NULL,
    
    -- Event details
    event_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    
    -- Event payload - contains the actual data to sync
    payload JSONB NOT NULL DEFAULT '{}',
    
    -- Source version for conflict detection
    source_version INTEGER NOT NULL DEFAULT 0,
    
    -- Processing status
    status sync_event_status_enum NOT NULL DEFAULT 'PENDING',
    
    -- Retry tracking
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    
    -- Error tracking
    error_message TEXT,
    error_trace TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Message queue metadata
    redis_message_id VARCHAR(100)
);

-- Create indexes for sync_event_log
CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_event_log_event_id 
    ON jeseci_academy.sync_event_log(event_id);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_event_log_correlation_id 
    ON jeseci_academy.sync_event_log(correlation_id);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_event_log_event_type 
    ON jeseci_academy.sync_event_log(event_type);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_event_log_entity 
    ON jeseci_academy.sync_event_log(entity_id, entity_type);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_event_log_status 
    ON jeseci_academy.sync_event_log(status);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_event_log_redis_message_id 
    ON jeseci_academy.sync_event_log(redis_message_id);

-- Index for finding events to retry
CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_event_log_retry 
    ON jeseci_academy.sync_event_log(status, retry_count) 
    WHERE status IN ('PENDING', 'PUBLISHED', 'FAILED');

-- Index for ordering by creation time
CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_event_log_created 
    ON jeseci_academy.sync_event_log(created_at DESC);

-- =============================================================================
-- Step 3: Create sync_status table
-- =============================================================================

CREATE TABLE IF NOT EXISTS jeseci_academy.sync_status (
    id SERIAL PRIMARY KEY,
    
    -- Entity identifiers
    entity_id VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    
    -- Sync status
    is_synced BOOLEAN NOT NULL DEFAULT FALSE,
    last_synced_at TIMESTAMP WITH TIME ZONE,
    last_synced_version INTEGER,
    
    -- Source data version
    source_version INTEGER NOT NULL DEFAULT 0,
    
    -- Neo4j data version (for conflict detection)
    neo4j_version INTEGER,
    neo4j_checksum VARCHAR(256),
    
    -- Status flags
    has_pending_changes BOOLEAN NOT NULL DEFAULT FALSE,
    has_conflict BOOLEAN NOT NULL DEFAULT FALSE,
    conflict_count INTEGER NOT NULL DEFAULT 0,
    
    -- Error tracking
    last_error TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Unique constraint
    CONSTRAINT uq_jeseci_academy_sync_status_entity 
        UNIQUE (entity_id, entity_type)
);

-- Create indexes for sync_status
CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_status_entity 
    ON jeseci_academy.sync_status(entity_id, entity_type);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_status_entity_type 
    ON jeseci_academy.sync_status(entity_type);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_status_synced 
    ON jeseci_academy.sync_status(is_synced);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_status_pending 
    ON jeseci_academy.sync_status(has_pending_changes);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_status_conflict 
    ON jeseci_academy.sync_status(has_conflict);

-- Index for finding entities that need syncing
CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_status_needs_sync 
    ON jeseci_academy.sync_status(has_pending_changes, is_synced) 
    WHERE has_pending_changes = TRUE;

-- =============================================================================
-- Step 4: Create sync_conflicts table
-- =============================================================================

CREATE TABLE IF NOT EXISTS jeseci_academy.sync_conflicts (
    id SERIAL PRIMARY KEY,
    
    -- Entity identifiers
    entity_id VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    
    -- Conflict details
    conflict_type VARCHAR(50) NOT NULL,
    source_version INTEGER NOT NULL,
    target_version INTEGER,
    
    -- Data comparison
    source_data JSONB NOT NULL,
    target_data JSONB,
    difference_summary TEXT,
    
    -- Resolution
    resolution_status conflict_resolution_status_enum NOT NULL DEFAULT 'DETECTED',
    resolution_method VARCHAR(50),
    resolved_by VARCHAR(100),
    resolution_notes TEXT,
    
    -- Related event (foreign key to sync_event_log)
    event_id VARCHAR(64),
    
    -- Timestamps
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for sync_conflicts
CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_conflicts_entity 
    ON jeseci_academy.sync_conflicts(entity_id, entity_type);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_conflicts_type 
    ON jeseci_academy.sync_conflicts(entity_type);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_conflicts_conflict_type 
    ON jeseci_academy.sync_conflicts(conflict_type);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_conflicts_status 
    ON jeseci_academy.sync_conflicts(resolution_status);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_conflicts_event 
    ON jeseci_academy.sync_conflicts(event_id);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_conflicts_detected 
    ON jeseci_academy.sync_conflicts(detected_at DESC);

-- Index for finding unresolved conflicts
CREATE INDEX IF NOT EXISTS ix_jeseci_academy_sync_conflicts_unresolved 
    ON jeseci_academy.sync_conflicts(resolution_status) 
    WHERE resolution_status IN ('DETECTED', 'MANUAL_REVIEW');

-- =============================================================================
-- Step 5: Create reconciliation_runs table
-- =============================================================================

CREATE TABLE IF NOT EXISTS jeseci_academy.reconciliation_runs (
    id SERIAL PRIMARY KEY,
    
    -- Run details
    run_id VARCHAR(64) NOT NULL UNIQUE,
    run_type VARCHAR(50) NOT NULL,  -- scheduled, manual, triggered
    
    -- Statistics
    entities_checked INTEGER NOT NULL DEFAULT 0,
    inconsistencies_found INTEGER NOT NULL DEFAULT 0,
    inconsistencies_repaired INTEGER NOT NULL DEFAULT 0,
    conflicts_detected INTEGER NOT NULL DEFAULT 0,
    conflicts_resolved INTEGER NOT NULL DEFAULT 0,
    failed_entities INTEGER NOT NULL DEFAULT 0,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
    error_message TEXT,
    
    -- Parameters used
    batch_size INTEGER NOT NULL DEFAULT 50,
    entities_included TEXT  -- JSON array
);

-- Create indexes for reconciliation_runs
CREATE INDEX IF NOT EXISTS ix_jeseci_academy_reconciliation_runs_run_id 
    ON jeseci_academy.reconciliation_runs(run_id);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_reconciliation_runs_type 
    ON jeseci_academy.reconciliation_runs(run_type);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_reconciliation_runs_status 
    ON jeseci_academy.reconciliation_runs(status);

CREATE INDEX IF NOT EXISTS ix_jeseci_academy_reconciliation_runs_started 
    ON jeseci_academy.reconciliation_runs(started_at DESC);

-- Index for finding recent runs
CREATE INDEX IF NOT EXISTS ix_jeseci_academy_reconciliation_runs_recent 
    ON jeseci_academy.reconciliation_runs(started_at DESC);

-- =============================================================================
-- Step 6: Add foreign key constraints
-- =============================================================================

-- Add foreign key from sync_conflicts to sync_event_log
ALTER TABLE jeseci_academy.sync_conflicts
    DROP CONSTRAINT IF EXISTS fk_sync_conflicts_event;

ALTER TABLE jeseci_academy.sync_conflicts
    ADD CONSTRAINT fk_sync_conflicts_event
    FOREIGN KEY (event_id)
    REFERENCES jeseci_academy.sync_event_log(event_id)
    ON DELETE SET NULL;

-- =============================================================================
-- Step 7: Create helper functions and triggers
-- =============================================================================

-- Function to update the updated_at timestamp automatically
CREATE OR REPLACE FUNCTION jeseci_academy.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to auto-update updated_at columns
DROP TRIGGER IF EXISTS update_sync_event_log_updated_at ON jeseci_academy.sync_event_log;
DROP TRIGGER IF EXISTS update_sync_status_updated_at ON jeseci_academy.sync_status;

CREATE TRIGGER update_sync_event_log_updated_at
    BEFORE UPDATE ON jeseci_academy.sync_event_log
    FOR EACH ROW
    EXECUTE FUNCTION jeseci_academy.update_updated_at_column();

CREATE TRIGGER update_sync_status_updated_at
    BEFORE UPDATE ON jeseci_academy.sync_status
    FOR EACH ROW
    EXECUTE FUNCTION jeseci_academy.update_updated_at_column();

-- =============================================================================
-- Verification Query
-- =============================================================================

-- Verify tables were created
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'jeseci_academy'
    AND table_name IN ('sync_event_log', 'sync_status', 'sync_conflicts', 'reconciliation_runs')
ORDER BY table_name, ordinal_position;

-- List all created tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'jeseci_academy' 
    AND table_name LIKE 'sync_%' OR table_name = 'reconciliation_runs'
ORDER BY table_name;
