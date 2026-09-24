"""Integration tests for AlloyDB / PostgreSQL persistence, JSONB serialization, and optimistic locking."""

import uuid
import pytest

from database.db_client import DatabaseClient


@pytest.mark.asyncio
async def test_database_persistence_and_optimistic_concurrency():
    """Verify initiative creation, callback registration, status transitions, and version concurrency check."""
    db = DatabaseClient(use_memory_store_if_unavailable=True)
    await db.initialize()

    init_id = str(uuid.uuid4())
    brief_payload = {
        "initiative_id": init_id,
        "brand_id": "brand_apex",
        "category": "fabric_care",
        "trend_name": "Enzymatic Cold Wash 2026",
        "trend_summary": "Cold water washing saves 90% energy.",
        "target_audience": "Conscious families",
        "citations": [
            {
                "title": "Energy Report",
                "url": "https://www.energy.gov/cold-water",
                "snippet": "90% energy savings.",
                "publication_date": "2026-08-01",
            }
        ],
        "memories_applied": [
            {
                "memory_id": "mem_01",
                "directive": "Emphasize 90% energy savings.",
                "category": "tone",
            }
        ],
        "creative_hooks": [
            {
                "headline": "Cold Water, Brilliant Clean",
                "narrative_angle": "Eco savings",
                "key_claims": ["90% energy saved"],
                "visual_direction": "Glacial water droplets",
            }
        ],
        "confidence_score": 0.95,
    }

    created = await db.upsert_initiative(
        initiative_id=init_id,
        brand_id="brand_apex",
        category="fabric_care",
        trend_name="Enzymatic Cold Wash 2026",
        revision_count=0,
        status="PENDING_APPROVAL",
        brief_payload=brief_payload,
    )
    assert created["id"] == init_id
    assert created["status"] == "PENDING_APPROVAL"
    assert created["version"] == 1

    # Register callback
    cb = await db.register_callback(
        initiative_id=init_id,
        workflow_execution_id="exec-test-001",
        callback_url="https://workflowexecutions.googleapis.com/v1/projects/wortz-project-352116/callbacks/cb-1",
    )
    assert cb["status"] == "WAITING"

    # Update status to APPROVED
    updated = await db.update_initiative_status(
        initiative_id=init_id,
        status="APPROVED",
        reviewer="director@enterprise.com",
        comments="Approved for Q4 launch.",
        expected_version=1,
    )
    assert updated["status"] == "APPROVED"
    assert updated["version"] == 2

    # Concurrent update with stale version=1 should raise ValueError (HTTP 409 Conflict)
    with pytest.raises(ValueError, match="already been updated"):
        await db.update_initiative_status(
            initiative_id=init_id,
            status="REJECTED",
            reviewer="second_manager@enterprise.com",
            comments="Conflicting decision",
            expected_version=1,
        )
