"""Full-Stack FastAPI Web Application for Component D: Human-in-the-Loop Approval Interface & Workflow Graph Visualizer."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database.db_client import db_client
from services.data_service.routes.callbacks import (
    TriggerWorkflowPayload,
    trigger_cloud_workflow,
)
from services.data_service.routes.initiatives import (
    DecisionDispatchPayload,
    list_initiatives as local_list_initiatives,
    get_initiative as local_get_initiative,
    submit_human_review_decision as local_submit_decision,
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Brand Building HITL Approval Example Application - HITL Approval Dashboard & Workflow Graph",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.autoescape = True


def _get_id_token(audience_url: str) -> Optional[str]:
    """Fetch Google Cloud OIDC ID token when calling authenticated Cloud Run Data Service."""
    try:
        import google.auth.transport.requests
        import google.oauth2.id_token

        auth_req = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(auth_req, audience_url)
    except Exception:
        return None


async def _fetch_from_data_service(
    method: str, path: str, json_body: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Call remote `DATA_SERVICE_URL` if configured in production, with seamless in-process fallback."""
    data_url = os.getenv("DATA_SERVICE_URL", "").rstrip("/")
    if data_url and not data_url.startswith("http://127.0.0.1") and not data_url.startswith("http://localhost"):
        try:
            headers = {"Content-Type": "application/json"}
            id_token = _get_id_token(data_url)
            if id_token:
                headers["Authorization"] = f"Bearer {id_token}"
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.request(
                    method, f"{data_url}{path}", headers=headers, json=json_body
                )
                if resp.status_code in (200, 201):
                    return resp.json()
                if resp.status_code in (404, 409, 422):
                    raise HTTPException(status_code=resp.status_code, detail=resp.json().get("detail", resp.text))
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning("Remote DATA_SERVICE_URL request fallback (%s)", exc)
    return None


@app.get("/health")
async def health() -> Dict[str, str]:
    return {
        "status": "healthy",
        "service": "approval-ui",
        "project_id": os.getenv("PROJECT_ID", "wortz-project-352116"),
    }


@app.get("/", response_class=HTMLResponse)
async def queue_screen(
    request: Request, status: Optional[str] = None, brand_id: Optional[str] = None
) -> HTMLResponse:
    """Queue Screen (`/`) with KPI Metrics, Live Asynchronous Workflow Graph, and Pending Approvals Table."""
    await db_client.initialize()
    remote_data = await _fetch_from_data_service("GET", "/initiatives")
    if remote_data:
        initiatives = remote_data["initiatives"]
        metrics = remote_data["metrics"]
        if status:
            initiatives = [i for i in initiatives if i["status"] == status]
        if brand_id:
            initiatives = [i for i in initiatives if i["brand_id"] == brand_id]
    else:
        local_data = await local_list_initiatives(status=status, brand_id=brand_id)
        initiatives = local_data["initiatives"]
        metrics = local_data["metrics"]

    return templates.TemplateResponse(
        request=request,
        name="queue.html",
        context={
            "initiatives": initiatives,
            "metrics": metrics,
            "selected_status": status or "",
            "selected_brand": brand_id or "",
            "project_id": os.getenv("PROJECT_ID", "wortz-project-352116"),
            "region": os.getenv("REGION", "us-central1"),
            "workflow_name": os.getenv("WORKFLOWS_NAME", "trend_discovery_flow"),
        },
    )


@app.get("/graph", response_class=HTMLResponse)
async def workflow_graph_screen(request: Request) -> HTMLResponse:
    """Dedicated Asynchronous Workflow Graph & 3-Tier Architecture State Visualizer (`/graph`)."""
    await db_client.initialize()
    remote_data = await _fetch_from_data_service("GET", "/initiatives")
    if remote_data:
        initiatives = remote_data["initiatives"]
        metrics = remote_data["metrics"]
    else:
        local_data = await local_list_initiatives()
        initiatives = local_data["initiatives"]
        metrics = local_data["metrics"]

    return templates.TemplateResponse(
        request=request,
        name="graph.html",
        context={
            "initiatives": initiatives,
            "metrics": metrics,
            "project_id": os.getenv("PROJECT_ID", "wortz-project-352116"),
            "region": os.getenv("REGION", "us-central1"),
            "workflow_name": os.getenv("WORKFLOWS_NAME", "trend_discovery_flow"),
        },
    )


@app.get("/initiatives/{initiative_id}", response_class=HTMLResponse)
async def detail_review_screen(request: Request, initiative_id: str) -> HTMLResponse:
    """Detail Review Screen (`/initiatives/{id}`) with Grounding Inspector, Memory Matrix, and Action Toolbar."""
    await db_client.initialize()
    detail = await _fetch_from_data_service("GET", f"/initiatives/{initiative_id}")
    if not detail:
        detail = await local_get_initiative(initiative_id)

    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context={
            "initiative": detail,
            "brief": detail.get("brief_payload", {}),
            "callback": detail.get("active_callback") or {},
            "graph": detail.get("workflow_graph_state", {}),
            "reviews": detail.get("reviews", []),
            "memory_events": detail.get("memory_sync_events", []),
            "project_id": os.getenv("PROJECT_ID", "wortz-project-352116"),
            "region": os.getenv("REGION", "us-central1"),
            "workflow_name": os.getenv("WORKFLOWS_NAME", "trend_discovery_flow"),
        },
    )


@app.get("/api/initiatives")
async def api_list_initiatives() -> JSONResponse:
    remote_data = await _fetch_from_data_service("GET", "/initiatives")
    if remote_data:
        return JSONResponse(remote_data)
    local_data = await local_list_initiatives()
    return JSONResponse(local_data)


@app.get("/api/initiatives/{initiative_id}")
async def api_get_initiative(initiative_id: str) -> JSONResponse:
    remote_data = await _fetch_from_data_service("GET", f"/initiatives/{initiative_id}")
    if remote_data:
        return JSONResponse(remote_data)
    local_data = await local_get_initiative(initiative_id)
    return JSONResponse(local_data)


@app.get("/api/initiatives/{initiative_id}/callback")
async def api_get_callback(initiative_id: str) -> JSONResponse:
    remote_data = await _fetch_from_data_service("GET", f"/initiatives/{initiative_id}/callback")
    if remote_data:
        return JSONResponse(remote_data)
    cb = await db_client.get_active_callback(initiative_id)
    if not cb:
        raise HTTPException(status_code=404, detail="No callback registered")
    return JSONResponse(cb)


@app.post("/api/initiatives/{initiative_id}/decision")
async def api_submit_decision(
    initiative_id: str, payload: DecisionDispatchPayload
) -> JSONResponse:
    """Server-side BFF endpoint invoked by `static/js/approval.js`."""
    remote_res = await _fetch_from_data_service(
        "POST",
        f"/initiatives/{initiative_id}/decision",
        json_body=payload.model_dump(),
    )
    if remote_res:
        return JSONResponse(remote_res)
    local_res = await local_submit_decision(initiative_id, payload)
    return JSONResponse(local_res)


@app.post("/api/workflows/trigger")
async def api_trigger_workflow(payload: TriggerWorkflowPayload) -> JSONResponse:
    """Trigger a new Cloud Workflows execution from the UI."""
    remote_res = await _fetch_from_data_service(
        "POST", "/workflows/trigger", json_body=payload.model_dump()
    )
    if remote_res:
        return JSONResponse(remote_res)
    local_res = await trigger_cloud_workflow(payload)
    return JSONResponse(local_res)
