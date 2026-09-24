"""Gemini Enterprise Agent Platform Memory Bank Client (PRD Section 6 & 12).

Implements the official Agent Platform Memory Bank API:
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank

Uses live Vertex AI Reasoning Engine (`projects/{project}/locations/{location}/reasoningEngines/{agent_engine_id}/memories`):
- `RetrieveMemories` (`POST .../memories:retrieve`) scoped to `{"app_name": ..., "user_id": brand_id}`
- `CreateMemory` (`POST .../memories`) to write pre-extracted memories directly
- `GenerateMemories` (`POST .../memories:generate`) for LLM-driven memory extraction & consolidation
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from database.db_client import db_client

logger = logging.getLogger(__name__)

# Baseline Brand Memories stored in Agent Platform Memory Bank Scope `{"app_name": "brand_building_hitl_approval_example", "user_id": brand_id}`
BRAND_MEMORY_BANK_STORE: Dict[str, List[Dict[str, str]]] = {
    "brand_apex": [
        {
            "memory_id": "mem_01",
            "directive": "Preferred Tone: Optimistic, empowering, and scientific yet accessible.",
            "category": "tone",
            "topic": "brand_tone",
            "expected_tag": "cold_water_energy_savings",
            "created_at": "2026-07-01T00:00:00Z",
        },
        {
            "memory_id": "mem_02",
            "directive": "Claim Guardrail: Emphasize cold_water_energy_savings (saves up to 90% energy in wash cycle) and enforce no_silk_stain_claims (avoid unsubstantiated silk stain elimination promises).",
            "category": "legal",
            "topic": "claim_guardrails",
            "expected_tag": "no_silk_stain_claims",
            "created_at": "2026-08-01T00:00:00Z",
        },
        {
            "memory_id": "mem_03",
            "directive": "Rejected Hook (2026-08): Do not use shame-based or negative parenting angles.",
            "category": "hook",
            "topic": "audience_hook",
            "expected_tag": "no_guilt_hooks",
            "created_at": "2026-08-15T00:00:00Z",
        },
        {
            "memory_id": "mem_04",
            "directive": "Brand Motif: Visuals must emphasize crisp natural daylight and water flow.",
            "category": "audience",
            "topic": "visual_motif",
            "expected_tag": "crisp_daylight_water",
            "created_at": "2026-08-20T00:00:00Z",
        },
    ],
    "brand_aurora": [
        {
            "memory_id": "mem_aurora_01",
            "directive": "Claim Guardrail: Always highlight pediatrician_tested validation and gentle_comfort for sensitive newborn skin.",
            "category": "legal",
            "topic": "claim_guardrails",
            "expected_tag": "pediatrician_tested",
            "created_at": "2026-08-01T00:00:00Z",
        },
        {
            "memory_id": "mem_aurora_02",
            "directive": "Prohibited Claims: Avoid clinical prescription or exaggerated therapeutic promises for infant skin care.",
            "category": "legal",
            "topic": "prohibited_claims",
            "expected_tag": "gentle_comfort",
            "created_at": "2026-08-12T00:00:00Z",
        },
        {
            "memory_id": "mem_aurora_03",
            "directive": "Preferred Tone: Warm, reassuring, gentle_comfort, and nurturing for first-time parents.",
            "category": "tone",
            "topic": "brand_tone",
            "expected_tag": "gentle_comfort",
            "created_at": "2026-08-19T00:00:00Z",
        },
    ],
    "brand_lumina": [
        {
            "memory_id": "mem_lumina_01",
            "directive": "Sustainability Mandate: Highlight zero_plastic_packaging and 100% biodegradable plant-derived surfactants.",
            "category": "hook",
            "topic": "sustainability_hook",
            "expected_tag": "zero_plastic_packaging",
            "created_at": "2026-08-05T00:00:00Z",
        },
        {
            "memory_id": "mem_lumina_02",
            "directive": "Safety Guardrail: Enforce biodegradable formula positioning and restrict harsh oxidizer claims on porous timber surfaces.",
            "category": "legal",
            "topic": "claim_guardrails",
            "expected_tag": "biodegradable",
            "created_at": "2026-08-18T00:00:00Z",
        },
        {
            "memory_id": "mem_lumina_03",
            "directive": "Preferred Tone: Architectural minimalism, modern clarity, and eco-modern design sensibility.",
            "category": "tone",
            "topic": "brand_tone",
            "expected_tag": "biodegradable",
            "created_at": "2026-08-25T00:00:00Z",
        },
    ],
}


def _get_gcp_access_token() -> Optional[str]:
    """Obtain OAuth2 Bearer token for calling Vertex AI Agent Platform Memory Bank."""
    try:
        import google.auth
        import google.auth.transport.requests

        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(google.auth.transport.requests.Request())
        return credentials.token
    except Exception:
        return None


class MemoryBankClient:
    """Manages pre-execution semantic memory retrieval and post-review feedback consolidation via Agent Platform Memory Bank."""

    def __init__(self) -> None:
        self.project_id = os.getenv("PROJECT_ID", "wortz-project-352116")
        self.location = os.getenv("MEMORY_BANK_LOCATION", "us-central1")
        self.agent_engine_id = os.getenv("AGENT_ENGINE_ID", "5895016748914049024")
        self.app_name = os.getenv("MEMORY_BANK_APP_NAME", "brand_building_hitl_approval_example")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    @property
    def memories_base_url(self) -> str:
        return (
            f"https://{self.location}-aiplatform.googleapis.com/v1beta1/"
            f"projects/{self.project_id}/locations/{self.location}/"
            f"reasoningEngines/{self.agent_engine_id}/memories"
        )

    @staticmethod
    def resolve_contradictory_memories(
        memories: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Resolve conflicting guidelines by recency weighting (PRD Section 12)."""
        sorted_mems = sorted(
            memories,
            key=lambda m: m.get("created_at", "1970-01-01T00:00:00Z"),
            reverse=True,
        )
        seen_topics = set()
        resolved: List[Dict[str, str]] = []
        for mem in sorted_mems:
            topic = mem.get("topic")
            if topic:
                if topic in seen_topics:
                    continue
                seen_topics.add(topic)
            resolved.append(mem)
        return list(reversed(resolved))

    async def _retrieve_live_agent_platform_memories(
        self, brand_id: str
    ) -> List[Dict[str, str]]:
        """Call official Agent Platform Memory Bank `memories:retrieve` REST endpoint."""
        if os.getenv("PYTEST_CURRENT_TEST") is not None:
            return []
        token = _get_gcp_access_token()
        if not token:
            return []
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    f"{self.memories_base_url}:retrieve",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "scope": {
                            "app_name": self.app_name,
                            "user_id": brand_id,
                        }
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    retrieved: List[Dict[str, str]] = []
                    for item in data.get("retrievedMemories", []):
                        mem = item.get("memory", {})
                        full_name = mem.get("name", "")
                        short_id = full_name.split("/")[-1] if full_name else uuid.uuid4().hex[:8]
                        fact = mem.get("fact", "")
                        if fact:
                            retrieved.append(
                                {
                                    "memory_id": f"mb_{short_id[:10]}",
                                    "directive": fact,
                                    "category": "tone",
                                    "topic": f"mb_{short_id}",
                                    "created_at": mem.get("updateTime") or mem.get("createTime") or datetime.now(timezone.utc).isoformat(),
                                    "resource_name": full_name,
                                }
                            )
                    return retrieved
        except Exception as exc:
            logger.info("Agent Platform Memory Bank retrieve fallback (%s)", exc)
        return []

    async def _create_and_generate_live_agent_platform_memory(
        self, brand_id: str, distilled_rule: str
    ) -> Optional[str]:
        """Call official Agent Platform Memory Bank `CreateMemory` and `GenerateMemories` endpoints."""
        if os.getenv("PYTEST_CURRENT_TEST") is not None:
            return None
        token = _get_gcp_access_token()
        if not token:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. CreateMemory (`POST .../memories`) for immediate deterministic availability
                create_resp = await client.post(
                    self.memories_base_url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "scope": {
                            "app_name": self.app_name,
                            "user_id": brand_id,
                        },
                        "fact": distilled_rule,
                    },
                )
                # 2. GenerateMemories (`POST .../memories:generate`) for managed LLM consolidation
                await client.post(
                    f"{self.memories_base_url}:generate",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "scope": {
                            "app_name": self.app_name,
                            "user_id": brand_id,
                        },
                        "direct_memories_source": {
                            "direct_memories": [{"fact": distilled_rule}]
                        },
                    },
                )
                if create_resp.status_code in (200, 201):
                    c_data = create_resp.json()
                    mem_name = c_data.get("response", {}).get("name") or c_data.get("name", "")
                    if mem_name:
                        short_id = mem_name.split("/memories/")[-1].split("/")[0]
                        return f"mem_sync_{short_id[:10]}"
        except Exception as exc:
            logger.info("Agent Platform Memory Bank write fallback (%s)", exc)
        return None

    async def retrieve_brand_memories_with_metadata(
        self, brand_id: str, category: str
    ) -> Dict[str, Any]:
        """Retrieve brand memories from Agent Platform Memory Bank + baseline store (PRD Section 12)."""
        base_memories = list(BRAND_MEMORY_BANK_STORE.get(brand_id, []))
        live_mb_memories = await self._retrieve_live_agent_platform_memories(brand_id)
        for lm in live_mb_memories:
            if not any(m["directive"] == lm["directive"] for m in base_memories):
                base_memories.append(lm)

        synced_events = await db_client.get_brand_memory_events(brand_id)
        for ev in synced_events:
            rec_id = ev.get("memory_bank_record_id") or f"mem_sync_{ev['id'][:8]}"
            if not any(m["memory_id"] == rec_id or m["directive"] == ev["distilled_rule"] for m in base_memories):
                base_memories.append(
                    {
                        "memory_id": rec_id,
                        "directive": ev["distilled_rule"],
                        "category": "tone",
                        "topic": f"synced_{rec_id}",
                        "created_at": ev.get("synced_at", datetime.now(timezone.utc).isoformat()),
                    }
                )

        if not base_memories:
            return {
                "brand_id": brand_id,
                "category": category,
                "is_cold_start": True,
                "memory_status": "COLD_START_DEFAULT_INITIALIZED",
                "agent_engine_resource": f"projects/{self.project_id}/locations/{self.location}/reasoningEngines/{self.agent_engine_id}",
                "baseline_instruction": (
                    "Default Enterprise Baseline: Maintain a professional, accessible tone and require substantiated claims."
                ),
                "memories_applied": [],
            }

        resolved = self.resolve_contradictory_memories(base_memories)
        return {
            "brand_id": brand_id,
            "category": category,
            "is_cold_start": False,
            "memory_status": "ACTIVE_AGENT_PLATFORM_MEMORY_BANK",
            "agent_engine_resource": f"projects/{self.project_id}/locations/{self.location}/reasoningEngines/{self.agent_engine_id}",
            "baseline_instruction": "Adhere strictly to all retrieved brand memory directives. If two directives conflict, adhere strictly to the newer directive.",
            "memories_applied": [
                {
                    "memory_id": m["memory_id"],
                    "directive": m["directive"],
                    "category": m.get("category", "tone"),
                }
                for m in resolved
            ],
        }

    async def retrieve_brand_memories(
        self, brand_id: str, category: str
    ) -> List[Dict[str, str]]:
        meta = await self.retrieve_brand_memories_with_metadata(brand_id, category)
        return meta["memories_applied"]

    async def distill_and_persist_feedback(
        self,
        initiative_id: str,
        brand_id: str,
        feedback_text: str,
        decision: str = "REVISION_REQUESTED",
        approved_headline: str = "",
    ) -> Dict[str, Any]:
        """Distill human review feedback and persist to Gemini Enterprise Agent Platform Memory Bank (`CreateMemory` & `GenerateMemories`)."""
        distilled_rule: Optional[str] = None

        if os.getenv("PYTEST_CURRENT_TEST") is None:
            try:
                from google import genai

                client = genai.Client(
                    vertexai=True, project=self.project_id, location=self.location
                )
                prompt = (
                    "You are the Vertex AI Memory Bank Distillation Engine for an enterprise brand system.\n"
                    f"Brand ID: {brand_id}\n"
                    f"Review Decision: {decision}\n"
                    f"Approved Headline (if any): {approved_headline}\n"
                    f"Reviewer Commentary: {feedback_text}\n"
                    "Distill this review outcome into a single concise, reusable imperative brand rule (1 sentence, under 25 words) "
                    "that future and downstream Step 2 creative agents must follow."
                )
                resp = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                if resp and resp.text:
                    distilled_rule = resp.text.strip().strip('"')
            except Exception as exc:
                logger.info("Fallback rule distillation (%s)", exc)

        if not distilled_rule:
            cleaned = feedback_text.strip().rstrip(".")
            if decision == "APPROVED":
                exemplar = f" ('{approved_headline}')" if approved_headline else ""
                distilled_rule = f"Approved Brand Exemplar ({brand_id}){exemplar}: {cleaned}. Replicate this validated positioning in Step 2 asset generation."
            else:
                distilled_rule = f"Continuous Learning Directive ({brand_id}): {cleaned}. Enforce in all subsequent creative hooks."

        # Write to live Agent Platform Memory Bank (`CreateMemory` + `GenerateMemories`)
        live_record_id = await self._create_and_generate_live_agent_platform_memory(brand_id, distilled_rule)
        mem_record_id = live_record_id or f"mem_sync_{uuid.uuid4().hex[:8]}"

        BRAND_MEMORY_BANK_STORE.setdefault(brand_id, []).append(
            {
                "memory_id": mem_record_id,
                "directive": distilled_rule,
                "category": "hook" if decision == "APPROVED" else "tone",
                "topic": f"learned_{mem_record_id}",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        event = await db_client.record_memory_sync_event(
            initiative_id=initiative_id,
            brand_id=brand_id,
            feedback_text=feedback_text,
            distilled_rule=distilled_rule,
            memory_bank_record_id=mem_record_id,
        )
        return event

    async def pull_approved_step2_context(
        self,
        initiative_id: str,
        brand_id: str,
        category: str,
        brief_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Pull live context from Gemini Enterprise Agent Platform Memory Bank (`memories:retrieve`) + AlloyDB JSONB contract upon Approve."""
        memory_context = await self.retrieve_brand_memories_with_metadata(brand_id, category)
        return {
            "handoff_stage": "STEP_2_CREATIVE_ASSET_GENERATION",
            "context_isolation_mode": "CONTRACT_AND_MEMORY_BANK_ONLY_ZERO_CHAT_TRANSCRIPT",
            "agent_engine_memory_bank": memory_context.get("agent_engine_resource"),
            "memory_bank_scope": {"app_name": self.app_name, "user_id": brand_id},
            "initiative_id": initiative_id,
            "brand_id": brand_id,
            "category": category,
            "memories_pulled_count": len(memory_context["memories_applied"]),
            "memories_pulled": memory_context["memories_applied"],
            "approved_contract_headline": (
                brief_payload.get("creative_hooks", [{}])[0].get("headline", "")
                if brief_payload.get("creative_hooks")
                else brief_payload.get("trend_name", "")
            ),
            "pulled_at": datetime.now(timezone.utc).isoformat(),
        }


memory_bank_client = MemoryBankClient()
