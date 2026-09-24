-- Enable UUID extension (PRD Section 4.2)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table 1: Initiatives and Assets System of Record
CREATE TABLE IF NOT EXISTS initiative_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL,
    trend_name VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING_APPROVAL',
    -- Status values: 'DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'REVISION_REQUESTED', 'REJECTED', 'ESCALATED_MANUAL_REVIEW', 'BLOCKED_SAFETY_POLICY', 'EXPIRED_PENDING_RETRIGGER'
    version INT NOT NULL DEFAULT 1,
    revision_count INT NOT NULL DEFAULT 0,
    brief_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table 2: Workflow Orchestration & Callback State
CREATE TABLE IF NOT EXISTS workflow_callbacks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    initiative_id UUID NOT NULL REFERENCES initiative_assets(id) ON DELETE CASCADE,
    workflow_execution_id VARCHAR(255) NOT NULL,
    callback_url TEXT NOT NULL,
    callback_token VARCHAR(255),
    expires_at TIMESTAMPTZ,
    status VARCHAR(32) NOT NULL DEFAULT 'WAITING',
    -- Status values: 'WAITING', 'RECEIVED', 'EXPIRED'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table 3: Review Audit Trail
CREATE TABLE IF NOT EXISTS initiative_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    initiative_id UUID NOT NULL REFERENCES initiative_assets(id) ON DELETE CASCADE,
    reviewer_email VARCHAR(255) NOT NULL,
    action VARCHAR(32) NOT NULL,
    -- Action values: 'APPROVED', 'REVISION_REQUESTED', 'REJECTED'
    comments TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table 4: Memory Bank Sync Log (Continuous Learning)
CREATE TABLE IF NOT EXISTS memory_sync_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    initiative_id UUID NOT NULL REFERENCES initiative_assets(id) ON DELETE CASCADE,
    brand_id VARCHAR(64) NOT NULL,
    feedback_text TEXT NOT NULL,
    distilled_rule TEXT NOT NULL,
    memory_bank_record_id VARCHAR(255),
    synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for high-throughput queries
CREATE INDEX IF NOT EXISTS idx_initiative_status ON initiative_assets(status);
CREATE INDEX IF NOT EXISTS idx_initiative_brand ON initiative_assets(brand_id);
CREATE INDEX IF NOT EXISTS idx_workflow_initiative ON workflow_callbacks(initiative_id);
CREATE INDEX IF NOT EXISTS idx_workflow_status ON workflow_callbacks(status);
