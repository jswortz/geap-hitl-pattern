"""End-to-end integration test for the 3-Tier HITL Workflow lifecycle."""

import pytest
from httpx import ASGITransport, AsyncClient

from services.trend_agent.main import app as agent_app
from services.data_service.main import app as data_app


@pytest.mark.asyncio
async def test_e2e_trend_to_asset_hitl_workflow():
    """Simulate full Cloud Workflows execution: Agent 1 -> Data Service -> Callback -> Revision -> Approval."""
    async with AsyncClient(transport=ASGITransport(app=agent_app), base_url="http://agent") as agent_client, \
               AsyncClient(transport=ASGITransport(app=data_app), base_url="http://data") as data_client:

        # Step 1: Execute Trend Discovery Agent (Revision 0)
        agent_res = await agent_client.post(
            "/generate-trend-brief",
            json={
                "brand_id": "brand_apex",
                "category": "fabric_care",
                "revision_count": 0,
                "revision_notes": "",
                "search_query": "cold water eco wash consumer trends 2026",
            },
        )
        assert agent_res.status_code == 200
        brief = agent_res.json()["brief"]
        init_id = brief["initiative_id"]
        assert brief["brand_id"] == "brand_apex"
        assert len(brief["creative_hooks"]) >= 1

        # Step 2: Persist draft to Data Service with PENDING_APPROVAL
        persist_res = await data_client.post(
            "/initiatives",
            json={
                "initiative_id": init_id,
                "brand_id": "brand_apex",
                "category": "fabric_care",
                "trend_name": brief["trend_name"],
                "revision_count": 0,
                "status": "PENDING_APPROVAL",
                "brief_payload": brief,
            },
        )
        assert persist_res.status_code == 200
        assert persist_res.json()["status"] == "PENDING_APPROVAL"

        # Step 3: Register Cloud Workflows zero-compute HTTP callback
        cb_res = await data_client.post(
            "/callbacks",
            json={
                "initiative_id": init_id,
                "workflow_execution_id": "exec-e2e-100",
                "callback_url": "http://local-workflow-callback/cb-100",
                "status": "WAITING",
            },
        )
        assert cb_res.status_code == 200
        assert cb_res.json()["status"] == "WAITING"

        # Step 4: Verify empty revision feedback is rejected with HTTP 422 (PRD Section 12)
        bad_rev = await data_client.post(
            f"/initiatives/{init_id}/decision",
            json={
                "decision": "REVISION_REQUESTED",
                "reviewer": "director@enterprise.com",
                "comments": "short",
            },
        )
        assert bad_rev.status_code == 422

        # Step 5: Submit valid REVISION_REQUESTED decision & verify continuous learning memory sync
        rev_res = await data_client.patch(
            f"/initiatives/{init_id}/status",
            json={
                "status": "REVISION_REQUESTED",
                "reviewer": "director@enterprise.com",
                "comments": "Tone is too casual; emphasize scientific cold-water fabric longevity.",
            },
        )
        assert rev_res.status_code == 200
        assert rev_res.json()["status"] == "REVISION_REQUESTED"

        # Step 6: Re-run Agent 1 with revision_count=1 and verify updated brief
        agent_rev_res = await agent_client.post(
            "/generate-trend-brief",
            json={
                "initiative_id": init_id,
                "brand_id": "brand_apex",
                "category": "fabric_care",
                "revision_count": 1,
                "revision_notes": "Tone is too casual; emphasize scientific cold-water fabric longevity.",
                "search_query": "cold water eco wash consumer trends 2026",
            },
        )
        assert agent_rev_res.status_code == 200
        revised_brief = agent_rev_res.json()["brief"]
        assert revised_brief["initiative_id"] == init_id

        # Persist revision #1 back to PENDING_APPROVAL
        await data_client.post(
            "/initiatives",
            json={
                "initiative_id": init_id,
                "brand_id": "brand_apex",
                "category": "fabric_care",
                "trend_name": revised_brief["trend_name"],
                "revision_count": 1,
                "status": "PENDING_APPROVAL",
                "brief_payload": revised_brief,
            },
        )

        # Step 7: Approve final asset
        approve_res = await data_client.patch(
            f"/initiatives/{init_id}/status",
            json={
                "status": "APPROVED",
                "reviewer": "director@enterprise.com",
                "comments": "Approved for Q4 global campaign launch.",
            },
        )
        assert approve_res.status_code == 200
        assert approve_res.json()["status"] == "APPROVED"

        # Verify audit trail and workflow graph state
        detail_res = await data_client.get(f"/initiatives/{init_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["status"] == "APPROVED"
        assert len(detail["reviews"]) == 2
        assert len(detail["memory_sync_events"]) >= 1
