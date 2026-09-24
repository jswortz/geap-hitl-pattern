"""FastAPI Runner for Component A: Trend Discovery Agent Service."""

from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel

from services.trend_agent.agent import trend_agent
from services.trend_agent.schemas import TrendBriefRequest
from services.trend_agent.tools.memory_tool import memory_bank_client

app = FastAPI(
    title="Brand Building HITL Approval Example Application - Trend Discovery Agent (Component A)",
    version="1.0.0",
    description="ADK + Vertex AI Gemini + Google Search Grounding + Memory Bank Agent Service",
)


class FeedbackDistillRequest(BaseModel):
    initiative_id: str
    brand_id: str
    feedback_text: str


@app.get("/health")
async def health() -> Dict[str, str]:
    return {
        "status": "healthy",
        "service": "trend-agent-service",
        "project_id": os.getenv("PROJECT_ID", "wortz-project-352116"),
        "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    }


@app.post("/generate-trend-brief")
async def generate_trend_brief(req: TrendBriefRequest) -> Dict[str, Any]:
    """Endpoint invoked by Google Cloud Workflows `execute_trend_agent` step."""
    result = await trend_agent.generate_brief(
        brand_id=req.brand_id,
        category=req.category,
        search_query=req.search_query,
        revision_count=req.revision_count,
        revision_notes=req.revision_notes,
        initiative_id=req.initiative_id,
    )
    return result


@app.post("/distill-memory")
async def distill_memory(req: FeedbackDistillRequest) -> Dict[str, Any]:
    """Asynchronous continuous learning distillation endpoint for Vertex AI Memory Bank."""
    event = await memory_bank_client.distill_and_persist_feedback(
        initiative_id=req.initiative_id,
        brand_id=req.brand_id,
        feedback_text=req.feedback_text,
    )
    return {"status": "SYNCED", "memory_event": event}
