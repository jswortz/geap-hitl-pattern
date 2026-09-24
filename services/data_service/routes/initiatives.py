"""CRUD & HITL Decision routes for Initiatives (PRD Section 4.2, 5, & 12)."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from database.db_client import db_client
from services.trend_agent.agent import trend_agent
from services.trend_agent.tools.memory_tool import memory_bank_client

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateInitiativePayload(BaseModel):
    initiative_id: str
    brand_id: str
    category: str
    trend_name: str
    revision_count: int = 0
    status: str = "PENDING_APPROVAL"
    brief_payload: Dict[str, Any]


class UpdateStatusPayload(BaseModel):
    status: str
    reviewer: str
    comments: str = ""
    expected_version: Optional[int] = None


class DecisionDispatchPayload(BaseModel):
    decision: str = Field(description="APPROVED, REVISION_REQUESTED, or REJECTED")
    reviewer: str = "director@enterprise.com"
    comments: str = ""
    expected_version: Optional[int] = None


def _get_gcp_access_token() -> Optional[str]:
    """Obtain Google Cloud IAM OAuth2 token for calling Cloud Workflows callback endpoints."""
    try:
        import google.auth
        import google.auth.transport.requests

        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(google.auth.transport.requests.Request())
        return credentials.token
    except Exception as exc:
        logger.warning("Could not fetch GCP access token (%s)", exc)
        return None


@router.get("/initiatives")
async def list_initiatives(
    status: Optional[str] = None, brand_id: Optional[str] = None
) -> Dict[str, Any]:
    items = await db_client.list_initiatives(status=status, brand_id=brand_id)
    all_items = await db_client.list_initiatives()
    metrics = {
        "total": len(all_items),
        "pending_approval": sum(1 for i in all_items if i["status"] == "PENDING_APPROVAL"),
        "approved": sum(1 for i in all_items if i["status"] == "APPROVED"),
        "revision_requested": sum(1 for i in all_items if i["status"] == "REVISION_REQUESTED"),
        "rejected": sum(1 for i in all_items if i["status"] in ("REJECTED", "ESCALATED_MANUAL_REVIEW")),
        "memory_rules_learned": len(db_client._memory_events) + 10,
    }
    return {"initiatives": items, "metrics": metrics}


@router.post("/initiatives")
async def create_or_update_initiative(payload: CreateInitiativePayload) -> Dict[str, Any]:
    record = await db_client.upsert_initiative(
        initiative_id=payload.initiative_id,
        brand_id=payload.brand_id,
        category=payload.category,
        trend_name=payload.trend_name,
        revision_count=payload.revision_count,
        status=payload.status,
        brief_payload=payload.brief_payload,
    )
    return record


@router.get("/initiatives/{initiative_id}")
async def get_initiative(initiative_id: str) -> Dict[str, Any]:
    detail = await db_client.get_initiative_detail(initiative_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Initiative {initiative_id} not found")
    return detail


@router.patch("/initiatives/{initiative_id}/status")
async def patch_initiative_status(
    initiative_id: str, payload: UpdateStatusPayload
) -> Dict[str, Any]:
    if payload.status == "REVISION_REQUESTED" and len(payload.comments.strip()) < 10:
        raise HTTPException(
            status_code=422,
            detail="Actionable revision feedback must be at least 10 characters (PRD Section 12).",
        )

    detail = await db_client.get_initiative_detail(initiative_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Initiative {initiative_id} not found")

    try:
        updated = await db_client.update_initiative_status(
            initiative_id=initiative_id,
            status=payload.status,
            reviewer=payload.reviewer,
            comments=payload.comments,
            expected_version=payload.expected_version,
        )
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err))

    # Continuous Learning Loop: Distill reviewer feedback on APPROVED, REVISION_REQUESTED, or REJECTED into Vertex AI Memory Bank
    brief_hooks = detail.get("brief_payload", {}).get("creative_hooks", [])
    top_headline = brief_hooks[0].get("headline", "") if brief_hooks else detail.get("trend_name", "")
    if payload.comments and len(payload.comments.strip()) >= 5 and payload.status in ("APPROVED", "REVISION_REQUESTED", "REJECTED"):
        await memory_bank_client.distill_and_persist_feedback(
            initiative_id=initiative_id,
            brand_id=detail["brand_id"],
            feedback_text=payload.comments,
            decision=payload.status,
            approved_headline=top_headline,
        )

    if payload.status == "APPROVED":
        updated["step2_memory_context"] = await memory_bank_client.pull_approved_step2_context(
            initiative_id=initiative_id,
            brand_id=detail["brand_id"],
            category=detail["category"],
            brief_payload=detail.get("brief_payload", {}),
        )

    return updated


@router.post("/initiatives/{initiative_id}/decision")
async def submit_human_review_decision(
    initiative_id: str, payload: DecisionDispatchPayload
) -> Dict[str, Any]:
    """Authenticated BFF endpoint that dispatches human review decisions to Cloud Workflows callbacks."""
    if payload.decision == "REVISION_REQUESTED" and len(payload.comments.strip()) < 10:
        raise HTTPException(
            status_code=422,
            detail="Feedback comment must be at least 10 characters when requesting a revision (PRD Section 12).",
        )

    detail = await db_client.get_initiative_detail(initiative_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Initiative {initiative_id} not found")

    # Idempotency check (PRD Section 12: Duplicate Webhook Callbacks)
    if detail["status"] == "APPROVED" and payload.decision == "APPROVED":
        return {
            "status": "ALREADY_PROCESSED",
            "initiative_id": initiative_id,
            "decision": "APPROVED",
        }

    # Check hard revision cap (max_revisions: 3)
    rev_count = int(detail.get("revision_count", 0))
    if payload.decision == "REVISION_REQUESTED" and rev_count >= 3:
        updated = await db_client.update_initiative_status(
            initiative_id=initiative_id,
            status="ESCALATED_MANUAL_REVIEW",
            reviewer=payload.reviewer,
            comments=f"Max revisions (3) exceeded. {payload.comments}",
        )
        return {
            "status": "ESCALATED_MANUAL_REVIEW",
            "initiative_id": initiative_id,
            "initiative": updated,
        }

    active_cb = detail.get("active_callback")
    callback_url = active_cb.get("callback_url", "") if active_cb else ""
    workflow_resumed_live = False

    # 1. If there is a real Google Cloud Workflows callback URL waiting, dispatch authenticated POST to wake it!
    if (
        callback_url.startswith("https://workflowexecutions.googleapis.com/")
        and active_cb
        and active_cb.get("status") == "WAITING"
        and "/callbacks/cb-" not in callback_url  # Real GCP UUID callback vs static seed placeholder
    ):
        token = _get_gcp_access_token()
        if token:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    cb_resp = await client.post(
                        callback_url,
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "decision": payload.decision,
                            "reviewer": payload.reviewer,
                            "comments": payload.comments,
                        },
                    )
                    if cb_resp.status_code in (200, 201, 202):
                        workflow_resumed_live = True
                        logger.info("Resumed live Google Cloud Workflow callback: %s", callback_url)
            except Exception as exc:
                logger.warning("Live Cloud Workflow callback POST failed (%s); falling back to direct orchestration.", exc)

    # 2. Always ensure database & memory distillation reflect the decision immediately for UI responsiveness
    try:
        updated = await db_client.update_initiative_status(
            initiative_id=initiative_id,
            status=payload.decision,
            reviewer=payload.reviewer,
            comments=payload.comments,
            expected_version=payload.expected_version,
        )
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err))

    brief_hooks = detail.get("brief_payload", {}).get("creative_hooks", [])
    top_headline = brief_hooks[0].get("headline", "") if brief_hooks else detail.get("trend_name", "")

    memory_event = None
    if payload.comments and len(payload.comments.strip()) >= 5 and payload.decision in ("APPROVED", "REVISION_REQUESTED", "REJECTED"):
        memory_event = await memory_bank_client.distill_and_persist_feedback(
            initiative_id=initiative_id,
            brand_id=detail["brand_id"],
            feedback_text=payload.comments,
            decision=payload.decision,
            approved_headline=top_headline,
        )

    # 2b. When APPROVED, immediately pull the fresh context from Vertex AI Memory Bank + AlloyDB contract for Step 2!
    step2_memory_context = None
    if payload.decision == "APPROVED":
        step2_memory_context = await memory_bank_client.pull_approved_step2_context(
            initiative_id=initiative_id,
            brand_id=detail["brand_id"],
            category=detail["category"],
            brief_payload=detail.get("brief_payload", {}),
        )

    # 3. If REVISION_REQUESTED and not already handled by a live Cloud Workflow loop, execute the revision loop so the revised draft appears in PENDING_APPROVAL!
    revised_record = None
    if payload.decision == "REVISION_REQUESTED" and not workflow_resumed_live:
        next_rev = rev_count + 1
        gen_result = await trend_agent.generate_brief(
            brand_id=detail["brand_id"],
            category=detail["category"],
            search_query=f"{detail['trend_name']} {payload.comments}",
            revision_count=next_rev,
            revision_notes=payload.comments,
            initiative_id=initiative_id,
        )
        new_brief = gen_result["brief"]
        revised_record = await db_client.upsert_initiative(
            initiative_id=initiative_id,
            brand_id=detail["brand_id"],
            category=detail["category"],
            trend_name=new_brief["trend_name"],
            revision_count=next_rev,
            status="PENDING_APPROVAL",
            brief_payload=new_brief,
        )
        await db_client.register_callback(
            initiative_id=initiative_id,
            workflow_execution_id=(
                active_cb.get("workflow_execution_id", f"exec-{initiative_id[:8]}-rev{next_rev}")
                if active_cb
                else f"exec-{initiative_id[:8]}-rev{next_rev}"
            ),
            callback_url=f"https://workflowexecutions.googleapis.com/v1/projects/{os.getenv('PROJECT_ID', 'wortz-project-352116')}/locations/us-central1/workflows/trend_discovery_flow/executions/exec-rev-{next_rev}/callbacks/cb-{initiative_id[:8]}",
            status="WAITING",
        )

    final_detail = await db_client.get_initiative_detail(initiative_id)
    return {
        "status": "RESUMED_WORKFLOW",
        "workflow_resumed_live": workflow_resumed_live,
        "decision": payload.decision,
        "initiative_id": initiative_id,
        "memory_event": memory_event,
        "step2_memory_context": step2_memory_context,
        "revised_record": revised_record,
        "initiative": final_detail or updated,
    }
