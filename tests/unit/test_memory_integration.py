"""Unit tests for Vertex AI Memory Bank retrieval, cold-start fallback, recency resolution, and feedback distillation."""

import pytest

from services.trend_agent.tools.memory_tool import MemoryBankClient


@pytest.mark.asyncio
async def test_memory_retrieval_for_existing_brand():
    """Verify MemoryBankClient retrieves brand-specific rules for brand_apex."""
    client = MemoryBankClient()
    memories = await client.retrieve_brand_memories("brand_apex", "fabric_care")
    assert len(memories) >= 3
    directives_text = " ".join(m["directive"].lower() for m in memories)
    assert "90%" in directives_text or "cold" in directives_text
    assert "silk" in directives_text or "guilt" in directives_text


@pytest.mark.asyncio
async def test_memory_cold_start_brand_fallback():
    """Verify brand with zero prior memories triggers baseline enterprise defaults (PRD Section 12)."""
    client = MemoryBankClient()
    result = await client.retrieve_brand_memories_with_metadata("brand_new_unseen_2026", "personal_care")
    assert result["is_cold_start"] is True
    assert result["memories_applied"] == []
    assert "professional" in result["baseline_instruction"].lower()


@pytest.mark.asyncio
async def test_contradictory_memory_recency_resolution():
    """Verify contradictory memories resolve strictly in favor of newer timestamp (PRD Section 12)."""
    client = MemoryBankClient()
    raw_memories = [
        {
            "memory_id": "mem_old_2024",
            "directive": "Emphasize heavy botanical floral scent profiles in all hooks.",
            "category": "hook",
            "topic": "scent_policy",
            "created_at": "2024-05-10T00:00:00Z",
        },
        {
            "memory_id": "mem_new_2026",
            "directive": "Emphasize 100% fragrance-free hypoallergenic formulations; avoid floral scent claims.",
            "category": "hook",
            "topic": "scent_policy",
            "created_at": "2026-08-20T00:00:00Z",
        },
    ]
    resolved = client.resolve_contradictory_memories(raw_memories)
    assert len(resolved) == 1
    assert resolved[0]["memory_id"] == "mem_new_2026"
    assert "fragrance-free" in resolved[0]["directive"]


@pytest.mark.asyncio
async def test_feedback_distillation_and_persistence():
    """Verify reviewer critique is distilled into an atomic brand rule and persisted for subsequent runs."""
    client = MemoryBankClient()
    sync_record = await client.distill_and_persist_feedback(
        initiative_id="11111111-2222-3333-4444-555555555555",
        brand_id="brand_apex",
        feedback_text="Tone is too aggressive. We do not shame competitors by name. Keep focus on fabric longevity.",
    )
    assert sync_record["brand_id"] == "brand_apex"
    assert len(sync_record["distilled_rule"]) > 15
    assert sync_record["memory_bank_record_id"].startswith("mem_sync_")

    updated_memories = await client.retrieve_brand_memories("brand_apex", "fabric_care")
    assert any(sync_record["memory_bank_record_id"] == m["memory_id"] for m in updated_memories)
