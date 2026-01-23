-- Migration: Create authentication, code execution, and security tables
-- Run this in PostgreSQL to add support for email verification, password reset, and advanced code execution features

-- =============================================================================
-- Email Verification Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS jeseci_academy.email_verifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES jeseci_academy.users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    token_type VARCHAR(20) DEFAULT 'email_verification',
    expires_at TIMESTAMP WITH TIME ZONE,
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ev_user_id ON jeseci_academy.email_verifications(user_id);
CREATE INDEX IF NOT EXISTS idx_ev_token ON jeseci_academy.email_verifications(token);
CREATE INDEX IF NOT EXISTS idx_ev_expires_at ON jeseci_academy.email_verifications(expires_at);

-- =============================================================================
-- Password Reset Table
-- =============================================================================
CREATE TABLE IF NOT EXISTS jeseci_academy.password_resets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES jeseci_academy.users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pr_user_id ON jeseci_academy.password_resets(user_id);
CREATE INDEX IF NOT EXISTS idx_pr_token ON jeseci_academy.password_resets(token);
CREATE INDEX IF NOT EXISTS idx_pr_expires_at ON jeseci_academy.password_resets(expires_at);

-- =============================================================================
-- Code Snippets Tables (if not already created)
-- =============================================================================
CREATE TABLE IF NOT EXISTS jeseci_academy.code_folders (
    id VARCHAR(64) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES jeseci_academy.users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    parent_folder_id VARCHAR(64) REFERENCES jeseci_academy.code_folders(id) ON DELETE SET NULL,
    color VARCHAR(20) DEFAULT '#3b82f6',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS jeseci_academy.code_snippets (
    id VARCHAR(64) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES jeseci_academy.users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    code_content TEXT NOT NULL,
    language VARCHAR(50) DEFAULT 'jac',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    folder_id VARCHAR(64) REFERENCES jeseci_academy.code_folders(id) ON DELETE SET NULL,
    execution_count INTEGER DEFAULT 0,
    last_executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS jeseci_academy.execution_history (
    id VARCHAR(64) PRIMARY KEY,
    snippet_id VARCHAR(64) REFERENCES jeseci_academy.code_snippets(id) ON DELETE SET NULL,
    user_id INTEGER NOT NULL REFERENCES jeseci_academy.users(id) ON DELETE CASCADE,
    code_content TEXT NOT NULL,
    status VARCHAR(30) NOT NULL CHECK (status IN ('success', 'error', 'timeout', 'memory_exceeded', 'output_exceeded')),
    output TEXT,
    error_message TEXT,
    execution_time_ms INTEGER DEFAULT 0,
    entry_point VARCHAR(100) DEFAULT 'init',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jeseci_academy.snippet_versions (
    id VARCHAR(64) PRIMARY KEY,
    snippet_id VARCHAR(64) NOT NULL REFERENCES jeseci_academy.code_snippets(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    code_content TEXT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL REFERENCES jeseci_academy.users(id) ON DELETE CASCADE,
    change_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snippet_id, version_number)
);

CREATE TABLE IF NOT EXISTS jeseci_academy.test_cases (
    id VARCHAR(64) PRIMARY KEY,
    snippet_id VARCHAR(64) NOT NULL REFERENCES jeseci_academy.code_snippets(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    input_data TEXT,
    expected_output TEXT NOT NULL,
    is_hidden BOOLEAN DEFAULT FALSE,
    order_index INTEGER DEFAULT 0,
    timeout_ms INTEGER DEFAULT 5000,
    created_by INTEGER NOT NULL REFERENCES jeseci_academy.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS jeseci_academy.test_results (
    id VARCHAR(64) PRIMARY KEY,
    test_case_id VARCHAR(64) NOT NULL REFERENCES jeseci_academy.test_cases(id) ON DELETE CASCADE,
    execution_id VARCHAR(64) REFERENCES jeseci_academy.execution_history(id) ON DELETE SET NULL,
    passed BOOLEAN NOT NULL,
    actual_output TEXT,
    execution_time_ms INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jeseci_academy.error_knowledge_base (
    id VARCHAR(64) PRIMARY KEY,
    error_pattern VARCHAR(500) NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    suggestion TEXT NOT NULL,
    examples TEXT,
    documentation_link VARCHAR(500),
    language VARCHAR(50) DEFAULT 'jac',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jeseci_academy.debug_sessions (
    id VARCHAR(64) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES jeseci_academy.users(id) ON DELETE CASCADE,
    snippet_id VARCHAR(64) NOT NULL REFERENCES jeseci_academy.code_snippets(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'terminated')),
    current_line INTEGER,
    breakpoints TEXT,
    variables TEXT,
    call_stack TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- Indexes for Performance
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_code_snippets_user ON jeseci_academy.code_snippets(user_id);
CREATE INDEX IF NOT EXISTS idx_code_snippets_folder ON jeseci_academy.code_snippets(folder_id);
CREATE INDEX IF NOT EXISTS idx_execution_history_user ON jeseci_academy.execution_history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_execution_history_snippet ON jeseci_academy.execution_history(snippet_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_snippet_versions_snippet ON jeseci_academy.snippet_versions(snippet_id, version_number DESC);
CREATE INDEX IF NOT EXISTS idx_test_cases_snippet ON jeseci_academy.test_cases(snippet_id, order_index);
CREATE INDEX IF NOT EXISTS idx_test_results_case ON jeseci_academy.test_results(test_case_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_debug_sessions_user ON jeseci_academy.debug_sessions(user_id, status);

-- =============================================================================
-- Sample Error Knowledge Entries
-- =============================================================================
INSERT INTO jeseci_academy.error_knowledge_base (id, error_pattern, error_type, title, description, suggestion, examples, language)
VALUES
    ('ekb_syntax_error', 'SyntaxError', 'Syntax', 'Syntax Error', 'Your code has a syntax error that prevents it from running.', 'Check your code for missing parentheses, brackets, or semicolons. Make sure all blocks are properly closed.', 'Make sure to close all parentheses and use proper indentation.', 'jac')
ON CONFLICT (id) DO NOTHING;

INSERT INTO jeseci_academy.error_knowledge_base (id, error_pattern, error_type, title, description, suggestion, examples, language)
VALUES
    ('ekb_name_error', 'NameError', 'Runtime', 'Undefined Variable', 'You are trying to use a variable that has not been defined.', 'Make sure you have defined the variable before using it. Check for typos in variable names.', 'If you use "x" make sure it was defined as "x = 5"', 'jac')
ON CONFLICT (id) DO NOTHING;

INSERT INTO jeseci_academy.error_knowledge_base (id, error_pattern, error_type, title, description, suggestion, examples, language)
VALUES
    ('ekb_type_error', 'TypeError', 'Type', 'Type Mismatch', 'You are trying to perform an operation on incompatible types.', 'Check the types of your variables. You may need to convert strings to numbers or use type-appropriate operations.', 'You cannot add a string and a number directly.', 'jac')
ON CONFLICT (id) DO NOTHING;
