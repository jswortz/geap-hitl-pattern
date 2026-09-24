"""Pydantic Data Contracts for the Trend Discovery Agent (PRD Section 4.1 & Section 12)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field


class SearchCitation(BaseModel):
    title: str = Field(description="Title of the search source article or page")
    url: str = Field(description="Public URL of the verified search result")
    snippet: str = Field(description="Relevant quote or snippet extracted from source")
    publication_date: Optional[str] = Field(default=None, description="Date of publication if available")


class MemoryDirectiveApplied(BaseModel):
    memory_id: str = Field(description="Identifier of the rule loaded from Vertex AI Memory Bank")
    directive: str = Field(description="Summary of brand guideline or historical learning applied")
    category: str = Field(description="Category: tone, legal, hook, or audience")


class CreativeHook(BaseModel):
    headline: str = Field(description="Punchy, audience-facing headline")
    narrative_angle: str = Field(description="Contextual story hook connecting consumer trend to product")
    key_claims: List[str] = Field(description="Specific product or brand claims featured")
    visual_direction: str = Field(description="Recommended imagery, art direction, and color motifs")


class InitiativeIdeaBrief(BaseModel):
    initiative_id: str = Field(description="Unique UUID for this trend initiative")
    brand_id: str = Field(description="Brand identifier, e.g., brand_apex, brand_aurora")
    category: str = Field(description="Product category, e.g., fabric_care, personal_care, home_care")
    trend_name: str = Field(description="Short title for identified consumer trend")
    trend_summary: str = Field(description="Detailed overview of the consumer shift observed")
    target_audience: str = Field(description="Primary demographic and psychographic persona")
    citations: List[SearchCitation] = Field(description="Verified Google Search sources")
    memories_applied: List[MemoryDirectiveApplied] = Field(description="Brand memory directives incorporated")
    creative_hooks: List[CreativeHook] = Field(description="Proposed creative expressions for the trend")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Agent confidence in trend relevance")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TrendBriefRequest(BaseModel):
    initiative_id: Optional[str] = None
    brand_id: str = "brand_apex"
    category: str = "fabric_care"
    revision_count: int = 0
    revision_notes: str = ""
    search_query: str = "sustainable laundry cold water washing trends 2026"


def filter_hallucinated_citations(
    brief: InitiativeIdeaBrief, verified_urls: Iterable[str]
) -> InitiativeIdeaBrief:
    """Deterministic post-filter (PRD Section 12): strip any citation not matching verified search URLs/domains."""
    verified_list = list(verified_urls)
    verified_set = set(verified_list)
    verified_domains = {urlparse(u).netloc.lower() for u in verified_list if u}

    valid_citations: List[SearchCitation] = []
    for cit in brief.citations:
        domain = urlparse(cit.url).netloc.lower()
        if cit.url in verified_set or (domain and domain in verified_domains):
            valid_citations.append(cit)

    brief.citations = valid_citations
    return brief
