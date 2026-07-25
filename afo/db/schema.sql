-- =========================================================================
-- Database Schema Placeholder
-- Target: orchestrator/db/schema.sql
-- =========================================================================

-- Drop tables if they exist for clean migrations
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS decisions;

-- Decisions Table
CREATE TABLE IF NOT EXISTS decisions (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) NOT NULL UNIQUE,
    payload JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs Table (For agent tracking and verification)
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    decision_id INT REFERENCES decisions(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX idx_decisions_status ON decisions(status);
CREATE INDEX idx_audit_logs_decision_id ON audit_logs(decision_id);