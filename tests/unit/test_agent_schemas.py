"""Unit tests for Pydantic data contracts and schema enforcement (PRD Section 4.1 & 12)."""

import pytest
from pydantic import ValidationError

from services.trend_agent.schemas import (
    CreativeHook,
    InitiativeIdeaBrief,
    MemoryDirectiveApplied,
    SearchCitation,
    filter_hallucinated_citations,
)


def test_valid_initiative_idea_brief():
    """Verify valid InitiativeIdeaBrief serializes and deserializes cleanly."""
    brief = InitiativeIdeaBrief(
        initiative_id="init-1234-5678",
        brand_id="brand_apex",
        category="fabric_care",
        trend_name="Cold-Water Eco Wash Revolution",
        trend_summary="Consumers are shifting to 60F cold water cycles to reduce household energy bills by up to 90%.",
        target_audience="Eco-conscious suburban families and utility-minded renters",
        citations=[
            SearchCitation(
                title="Cold Water Washing Energy Report 2026",
                url="https://www.energy.gov/articles/cold-water-laundry-savings-2026",
                snippet="Switching from hot to cold water saves up to 90% of laundry energy consumption.",
                publication_date="2026-08-15",
            )
        ],
        memories_applied=[
            MemoryDirectiveApplied(
                memory_id="mem_01",
                directive="Preferred Tone: Optimistic, empowering, and scientific yet accessible.",
                category="tone",
            )
        ],
        creative_hooks=[
            CreativeHook(
                headline="90% Less Energy. 100% Brilliant Clean.",
                narrative_angle="Connect rising utility awareness with effortless enzymatic cold-water power.",
                key_claims=["Saves up to 90% energy in wash cycle", "Active enzymatic lift at 60F"],
                visual_direction="Crisp natural daylight streaming through clear glacial water droplets.",
            )
        ],
        confidence_score=0.94,
    )

    data = brief.model_dump()
    assert data["brand_id"] == "brand_apex"
    assert data["confidence_score"] == 0.94
    assert len(data["citations"]) == 1
    assert len(data["creative_hooks"]) == 1

    restored = InitiativeIdeaBrief.model_validate_json(brief.model_dump_json())
    assert restored.initiative_id == "init-1234-5678"
    assert restored.creative_hooks[0].headline == "90% Less Energy. 100% Brilliant Clean."


def test_confidence_score_bounds_validation():
    """Verify confidence_score enforces [0.0, 1.0] bounds per PRD Section 4.1."""
    with pytest.raises(ValidationError):
        InitiativeIdeaBrief(
            initiative_id="init-bad-score",
            brand_id="brand_apex",
            category="fabric_care",
            trend_name="Invalid Confidence",
            trend_summary="Summary",
            target_audience="Audience",
            citations=[],
            memories_applied=[],
            creative_hooks=[],
            confidence_score=1.5,
        )


def test_filter_hallucinated_citations():
    """Verify deterministic post-filter strips citations not in raw search grounding results (PRD Section 12)."""
    brief = InitiativeIdeaBrief(
        initiative_id="init-citation-filter",
        brand_id="brand_apex",
        category="fabric_care",
        trend_name="Eco Wash",
        trend_summary="Summary",
        target_audience="Audience",
        citations=[
            SearchCitation(
                title="Verified Source",
                url="https://www.energy.gov/cold-water",
                snippet="Real quote",
            ),
            SearchCitation(
                title="Hallucinated Source",
                url="https://fake-hallucinated-domain-999.example.com/report",
                snippet="Invented quote",
            ),
        ],
        memories_applied=[],
        creative_hooks=[],
        confidence_score=0.88,
    )
    verified_urls = ["https://www.energy.gov/cold-water", "https://www.epa.gov/green-laundry"]
    cleaned = filter_hallucinated_citations(brief, verified_urls)
    assert len(cleaned.citations) == 1
    assert cleaned.citations[0].url == "https://www.energy.gov/cold-water"
