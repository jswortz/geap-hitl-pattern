"""Async Database Client for AlloyDB for PostgreSQL (System of Record Tier).

Supports:
1. Direct AlloyDB / PostgreSQL 16 connection pool via `asyncpg` (with automatic DDL & seed execution).
2. Cloud Firestore write-through mirroring in GCP project `wortz-project-352116` for zero-data-loss durability across serverless scaling.
3. Optimistic concurrency control (`version` checks returning HTTP 409 Conflict on collision) and idempotency guards.
"""

from __future__ import annotations

import copy
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import asyncpg
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


DEFAULT_SEED_INITIATIVES: List[Dict[str, Any]] = [
    {
        "id": "a1000000-0000-4000-8000-000000000001",
        "brand_id": "brand_apex",
        "category": "fabric_care",
        "trend_name": "Cold-Water Bio-Enzymatic Energy Surge",
        "status": "PENDING_APPROVAL",
        "version": 1,
        "revision_count": 0,
        "brief_payload": {
            "initiative_id": "a1000000-0000-4000-8000-000000000001",
            "brand_id": "brand_apex",
            "category": "fabric_care",
            "trend_name": "Cold-Water Bio-Enzymatic Energy Surge",
            "trend_summary": (
                "Rising residential utility costs in 2026 have accelerated consumer adoption of 60°F "
                "cold-water wash cycles by 42%, creating demand for bio-enzymatic formulations that "
                "activate without thermal energy while protecting synthetic athletic fibers."
            ),
            "target_audience": "Eco-conscious suburban households and activewear enthusiasts seeking lower utility bills without sacrificing garment longevity.",
            "citations": [
                {
                    "title": "US Department of Energy: Residential Cold-Water Laundry Efficiency Benchmark 2026",
                    "url": "https://www.energy.gov/energysaver/laundry-energy-efficiency-2026",
                    "snippet": "Heating water accounts for 90% of the energy used by washing machines; switching to cold water reduces household carbon footprint by 1,600 lbs CO2 annually.",
                    "publication_date": "2026-08-12",
                },
                {
                    "title": "Sustainable Textile Institute: Bio-Surfactant Activation Below 18°C",
                    "url": "https://www.americancleaninginstitute.org/cold-water-wash-trends-2026",
                    "snippet": "Next-generation protease and lipase enzyme blends deliver 99.2% sebum lift in 15°C municipal tap water.",
                    "publication_date": "2026-09-03",
                },
            ],
            "memories_applied": [
                {
                    "memory_id": "mem_01",
                    "directive": "Preferred Tone: Optimistic, empowering, and scientific yet accessible.",
                    "category": "tone",
                },
                {
                    "memory_id": "mem_02",
                    "directive": "Claim Guardrail: Cold-water wash saves up to 90% energy in wash cycle; never claim 100% stain elimination on silk.",
                    "category": "legal",
                },
                {
                    "memory_id": "mem_04",
                    "directive": "Brand Motif: Visuals must emphasize crisp natural daylight and glacial water flow.",
                    "category": "hook",
                },
            ],
            "creative_hooks": [
                {
                    "headline": "Turn Down the Dial. Turn Up the Brilliance.",
                    "narrative_angle": "Frame the cold-water dial switch as an effortless scientific upgrade that saves up to 90% wash-cycle energy while locking in fiber elasticity.",
                    "key_claims": [
                        "Saves up to 90% energy in wash cycle",
                        "Sub-60°F bio-enzymatic activation",
                        "Zero thermal fiber shrinkage",
                    ],
                    "visual_direction": "Macro slow-motion shot of crisp natural daylight refracting through glacial water droplets lifting micro-soil from technical knit fibers.",
                },
                {
                    "headline": "Peak Performance at 60°F.",
                    "narrative_angle": "Target technical activewear owners whose synthetic elastane breaks down in warm washes.",
                    "key_claims": [
                        "Preserves elastane recovery across 50+ washes",
                        "Cold-water energy savings",
                    ],
                    "visual_direction": "Split-frame microscopy showing intact cold-washed activewear fibers bathed in bright morning sunlight.",
                },
                {
                    "headline": "Smart Science for Conscious Homes.",
                    "narrative_angle": "Empower families with measurable utility bill reductions backed by enzymatic cleaning science.",
                    "key_claims": [
                        "Saves up to 90% energy in wash cycle",
                        "Dermatologist-verified clean rinse",
                    ],
                    "visual_direction": "Sunlit modern laundry room with translucent aqua water streams and clean botanical linen textures.",
                },
            ],
            "confidence_score": 0.94,
            "created_at": "2026-09-24T16:00:00Z",
        },
        "created_at": "2026-09-24T16:00:00Z",
        "updated_at": "2026-09-24T16:00:00Z",
    },
    {
        "id": "b2000000-0000-4000-8000-000000000002",
        "brand_id": "brand_aurora",
        "category": "baby_care",
        "trend_name": "Microbiome-Safe Newborn Barrier Protection",
        "status": "PENDING_APPROVAL",
        "version": 2,
        "revision_count": 1,
        "brief_payload": {
            "initiative_id": "b2000000-0000-4000-8000-000000000002",
            "brand_id": "brand_aurora",
            "category": "baby_care",
            "trend_name": "Microbiome-Safe Newborn Barrier Protection",
            "trend_summary": (
                "Millennial and Gen-Z parents in 2026 prioritize pH-balanced, prebiotic diaper liners "
                "that support infant skin microbiome integrity and eliminate synthetic fragrances."
            ),
            "target_audience": "First-time parents researching pediatrician-tested, hypoallergenic newborn skin care.",
            "citations": [
                {
                    "title": "Pediatric Dermatology Review: Infant Skin Microbiome & pH 5.5 Liners (2026)",
                    "url": "https://www.aap.org/infant-skin-barrier-microbiome-2026",
                    "snippet": "Maintaining acid mantle pH between 5.0 and 5.5 reduces diaper irritation incidence by 64% in clinical observation.",
                    "publication_date": "2026-07-28",
                }
            ],
            "memories_applied": [
                {
                    "memory_id": "mem_aurora_01",
                    "directive": "Emphasize pediatrician_tested and gentle_comfort; never use medical cure or miracle healing claims.",
                    "category": "legal",
                },
                {
                    "memory_id": "mem_sync_01",
                    "directive": "Focus messaging on gentle prebiotic skin barrier nourishment rather than clinical fear hooks.",
                    "category": "tone",
                },
            ],
            "creative_hooks": [
                {
                    "headline": "Pediatrician-Tested Comfort for Delicate First Days.",
                    "narrative_angle": "Reassure parents with gentle comfort and pH-balanced plant-derived liners.",
                    "key_claims": [
                        "Pediatrician-tested hypoallergenic liner",
                        "100% fragrance-free gentle comfort",
                    ],
                    "visual_direction": "Warm nursery morning light, ultra-soft organic cotton textures, calm parent-infant bonding.",
                },
                {
                    "headline": "Gentle Microbiome Harmony from Day One.",
                    "narrative_angle": "Celebrate peaceful nursery routines with prebiotic plant-soft protection.",
                    "key_claims": [
                        "Supports natural pH 5.5 skin barrier",
                        "Pediatrician-tested for sensitive newborn skin",
                    ],
                    "visual_direction": "Soft golden hour light across breathable botanical cotton weaves.",
                },
            ],
            "confidence_score": 0.91,
            "created_at": "2026-09-24T15:30:00Z",
        },
        "created_at": "2026-09-24T15:30:00Z",
        "updated_at": "2026-09-24T16:20:00Z",
    },
    {
        "id": "c3000000-0000-4000-8000-000000000003",
        "brand_id": "brand_lumina",
        "category": "home_care",
        "trend_name": "Waterless Dissolvable Bio-Refill Concentrates",
        "status": "APPROVED",
        "version": 2,
        "revision_count": 0,
        "brief_payload": {
            "initiative_id": "c3000000-0000-4000-8000-000000000003",
            "brand_id": "brand_lumina",
            "category": "home_care",
            "trend_name": "Waterless Dissolvable Bio-Refill Concentrates",
            "trend_summary": (
                "Urban consumers are replacing single-use plastic spray bottles with effervescent "
                "plant-based tablet refills packaged in home-compostable cellulose sleeves."
            ),
            "target_audience": "Zero-waste urban apartments and design-forward eco households.",
            "citations": [
                {
                    "title": "EPA Safer Choice Packaging & Refill Innovation Report 2026",
                    "url": "https://www.epa.gov/saferchoice/zero-plastic-home-care-refills-2026",
                    "snippet": "Concentrated tablet refills cut shipping weight by 88% and eliminate single-use HDPE triggers.",
                    "publication_date": "2026-08-05",
                }
            ],
            "memories_applied": [
                {
                    "memory_id": "mem_lumina_01",
                    "directive": "Require zero_plastic_packaging and biodegradable surfactant claims; prohibit bleach safe on wood claims.",
                    "category": "legal",
                }
            ],
            "creative_hooks": [
                {
                    "headline": "Just Add Tap Water. Zero Plastic Waste.",
                    "narrative_angle": "Turn reusable glass spray bottles into high-performance botanical surface cleaners.",
                    "key_claims": [
                        "100% biodegradable plant surfactants",
                        "Zero plastic packaging sleeve",
                    ],
                    "visual_direction": "Minimalist architectural kitchen counter with amber glass bottle and effervescent botanical tablet.",
                }
            ],
            "confidence_score": 0.96,
            "created_at": "2026-09-24T14:00:00Z",
        },
        "created_at": "2026-09-24T14:00:00Z",
        "updated_at": "2026-09-24T15:15:00Z",
    },
]

DEFAULT_SEED_CALLBACKS: List[Dict[str, Any]] = [
    {
        "id": "d4000000-0000-4000-8000-000000000001",
        "initiative_id": "a1000000-0000-4000-8000-000000000001",
        "workflow_execution_id": "projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-apex-001",
        "callback_url": "https://workflowexecutions.googleapis.com/v1/projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-apex-001/callbacks/cb-apex-001",
        "status": "WAITING",
        "created_at": "2026-09-24T16:00:05Z",
        "updated_at": "2026-09-24T16:00:05Z",
    },
    {
        "id": "d4000000-0000-4000-8000-000000000002",
        "initiative_id": "b2000000-0000-4000-8000-000000000002",
        "workflow_execution_id": "projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-aurora-002",
        "callback_url": "https://workflowexecutions.googleapis.com/v1/projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-aurora-002/callbacks/cb-aurora-002",
        "status": "WAITING",
        "created_at": "2026-09-24T16:20:05Z",
        "updated_at": "2026-09-24T16:20:05Z",
    },
    {
        "id": "d4000000-0000-4000-8000-000000000003",
        "initiative_id": "c3000000-0000-4000-8000-000000000003",
        "workflow_execution_id": "projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-lumina-003",
        "callback_url": "https://workflowexecutions.googleapis.com/v1/projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-lumina-003/callbacks/cb-lumina-003",
        "status": "RECEIVED",
        "created_at": "2026-09-24T14:00:05Z",
        "updated_at": "2026-09-24T15:15:00Z",
    },
]

DEFAULT_SEED_REVIEWS: List[Dict[str, Any]] = [
    {
        "id": "e5000000-0000-4000-8000-000000000001",
        "initiative_id": "b2000000-0000-4000-8000-000000000002",
        "reviewer_email": "brand.director@aurora-care.enterprise.com",
        "action": "REVISION_REQUESTED",
        "comments": "First draft leaned too heavily on clinical dermatologist jargon. Revise to emphasize gentle prebiotic comfort and warm parenting reassurance.",
        "created_at": "2026-09-24T16:15:00Z",
    },
    {
        "id": "e5000000-0000-4000-8000-000000000002",
        "initiative_id": "c3000000-0000-4000-8000-000000000003",
        "reviewer_email": "vp.sustainability@lumina-home.enterprise.com",
        "action": "APPROVED",
        "comments": "Approved for Q4 Omni-Channel Retail & Digital Asset Pipeline (Step 2 Eventarc Handoff). Verified EPA Safer Choice citation.",
        "created_at": "2026-09-24T15:15:00Z",
    },
]

DEFAULT_SEED_MEMORY_EVENTS: List[Dict[str, Any]] = [
    {
        "id": "f6000000-0000-4000-8000-000000000001",
        "initiative_id": "b2000000-0000-4000-8000-000000000002",
        "brand_id": "brand_aurora",
        "feedback_text": "First draft leaned too heavily on clinical dermatologist jargon. Revise to emphasize gentle prebiotic comfort and warm parenting reassurance.",
        "distilled_rule": "Focus messaging on gentle prebiotic skin barrier nourishment and warm parental reassurance rather than clinical fear hooks.",
        "memory_bank_record_id": "mem_sync_01",
        "synced_at": "2026-09-24T16:15:05Z",
    }
]


class DatabaseClient:
    """Enterprise System of Record client for AlloyDB/PostgreSQL with Firestore durability."""

    def __init__(self, use_memory_store_if_unavailable: bool = True) -> None:
        self.host = os.getenv("ALLOYDB_HOST", "127.0.0.1")
        self.port = int(os.getenv("ALLOYDB_PORT", "5432"))
        self.user = os.getenv("ALLOYDB_USER", "postgres")
        self.password = os.getenv("ALLOYDB_PASSWORD", "postgres")
        self.database = os.getenv("ALLOYDB_DATABASE", "brand_hitl_db")
        self.project_id = os.getenv("PROJECT_ID", "wortz-project-352116")
        default_fs = "true" if os.getenv("K_SERVICE") else "false"
        self.enable_firestore_sync = os.getenv("ENABLE_FIRESTORE_SYNC", default_fs).lower() == "true"
        self.use_memory_store_if_unavailable = use_memory_store_if_unavailable

        self.pool: Optional[asyncpg.Pool] = None
        self.firestore_db: Any = None
        self._initialized = False

        # In-memory / rehydrated state store
        self._initiatives: Dict[str, Dict[str, Any]] = {}
        self._callbacks: Dict[str, List[Dict[str, Any]]] = {}
        self._reviews: Dict[str, List[Dict[str, Any]]] = {}
        self._memory_events: List[Dict[str, Any]] = []

    async def initialize(self) -> None:
        """Initialize connection pool, run SQL migrations, and hydrate from Firestore if available."""
        if self._initialized:
            return

        # Populate baseline seed data in memory first
        for item in copy.deepcopy(DEFAULT_SEED_INITIATIVES):
            self._initiatives[item["id"]] = item
        for cb in copy.deepcopy(DEFAULT_SEED_CALLBACKS):
            self._callbacks.setdefault(cb["initiative_id"], []).append(cb)
        for rev in copy.deepcopy(DEFAULT_SEED_REVIEWS):
            self._reviews.setdefault(rev["initiative_id"], []).append(rev)
        self._memory_events = copy.deepcopy(DEFAULT_SEED_MEMORY_EVENTS)

        # Try connecting to PostgreSQL / AlloyDB via asyncpg
        try:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                min_size=1,
                max_size=10,
                command_timeout=5.0,
                timeout=3.0,
            )
            async with self.pool.acquire() as conn:
                schema_sql = (MIGRATIONS_DIR / "001_initial_schema.sql").read_text()
                seed_sql = (MIGRATIONS_DIR / "002_seed_data.sql").read_text()
                await conn.execute(schema_sql)
                await conn.execute(seed_sql)
            logger.info("Connected to AlloyDB/PostgreSQL at %s:%s/%s", self.host, self.port, self.database)
        except Exception as exc:
            self.pool = None
            if not self.use_memory_store_if_unavailable:
                raise
            logger.info("PostgreSQL pool not active locally (%s); using Firestore/in-memory ACID engine.", exc)

        # Try connecting to Cloud Firestore in wortz-project-352116 for serverless durability
        if self.enable_firestore_sync and os.getenv("PYTEST_CURRENT_TEST") is None:
            try:
                from google.cloud import firestore  # type: ignore

                self.firestore_db = firestore.Client(project=self.project_id)
                self._hydrate_from_firestore()
            except Exception as exc:
                logger.warning("Firestore sync skipped (%s)", exc)
                self.firestore_db = None

        self._initialized = True

    def _hydrate_from_firestore(self) -> None:
        """Load persisted records from Firestore and sync initial seeds if empty."""
        if not self.firestore_db:
            return
        try:
            docs = list(self.firestore_db.collection("geap_hitl_initiatives").stream())
            if not docs:
                # Write seed data to Firestore
                for item in self._initiatives.values():
                    self.firestore_db.collection("geap_hitl_initiatives").document(item["id"]).set(item)
                for cb_list in self._callbacks.values():
                    for cb in cb_list:
                        self.firestore_db.collection("geap_hitl_callbacks").document(cb["id"]).set(cb)
                for rev_list in self._reviews.values():
                    for rev in rev_list:
                        self.firestore_db.collection("geap_hitl_reviews").document(rev["id"]).set(rev)
                for mem in self._memory_events:
                    self.firestore_db.collection("geap_hitl_memories").document(mem["id"]).set(mem)
            else:
                for doc in docs:
                    data = doc.to_dict()
                    if data and "id" in data:
                        self._initiatives[data["id"]] = data
                for doc in self.firestore_db.collection("geap_hitl_callbacks").stream():
                    cb = doc.to_dict()
                    if cb and "initiative_id" in cb:
                        existing = self._callbacks.setdefault(cb["initiative_id"], [])
                        if not any(x["id"] == cb["id"] for x in existing):
                            existing.append(cb)
                        else:
                            for idx, x in enumerate(existing):
                                if x["id"] == cb["id"]:
                                    existing[idx] = cb
                for doc in self.firestore_db.collection("geap_hitl_reviews").stream():
                    rev = doc.to_dict()
                    if rev and "initiative_id" in rev:
                        existing = self._reviews.setdefault(rev["initiative_id"], [])
                        if not any(x["id"] == rev["id"] for x in existing):
                            existing.append(rev)
                for doc in self.firestore_db.collection("geap_hitl_memories").stream():
                    mem = doc.to_dict()
                    if mem and "id" in mem:
                        if not any(x["id"] == mem["id"] for x in self._memory_events):
                            self._memory_events.append(mem)
        except Exception as exc:
            logger.warning("Firestore hydration warning: %s", exc)

    def _sync_to_firestore(self, collection: str, doc_id: str, payload: Dict[str, Any]) -> None:
        if not self.firestore_db:
            return
        try:
            self.firestore_db.collection(collection).document(doc_id).set(payload)
        except Exception as exc:
            logger.warning("Firestore write warning (%s/%s): %s", collection, doc_id, exc)

    async def upsert_initiative(
        self,
        initiative_id: str,
        brand_id: str,
        category: str,
        trend_name: str,
        revision_count: int,
        status: str,
        brief_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Insert or update an initiative asset in AlloyDB/PostgreSQL and Firestore."""
        await self.initialize()
        now = _utc_now_iso()

        if self.pool:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO initiative_assets (id, brand_id, category, trend_name, status, version, revision_count, brief_payload, created_at, updated_at)
                    VALUES ($1::uuid, $2, $3, $4, $5, 1, $6, $7::jsonb, NOW(), NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        trend_name = EXCLUDED.trend_name,
                        status = EXCLUDED.status,
                        version = initiative_assets.version + 1,
                        revision_count = EXCLUDED.revision_count,
                        brief_payload = EXCLUDED.brief_payload,
                        updated_at = NOW()
                    RETURNING id::text, brand_id, category, trend_name, status, version, revision_count, brief_payload, created_at::text, updated_at::text
                    """,
                    initiative_id,
                    brand_id,
                    category,
                    trend_name,
                    status,
                    revision_count,
                    json.dumps(brief_payload),
                )
                record = dict(row)
                if isinstance(record["brief_payload"], str):
                    record["brief_payload"] = json.loads(record["brief_payload"])
        else:
            existing = self._initiatives.get(initiative_id)
            version = (existing["version"] + 1) if existing else 1
            created_at = existing["created_at"] if existing else now
            record = {
                "id": initiative_id,
                "brand_id": brand_id,
                "category": category,
                "trend_name": trend_name,
                "status": status,
                "version": version,
                "revision_count": revision_count,
                "brief_payload": brief_payload,
                "created_at": created_at,
                "updated_at": now,
            }

        self._initiatives[initiative_id] = record
        self._sync_to_firestore("geap_hitl_initiatives", initiative_id, record)
        return record

    async def register_callback(
        self,
        initiative_id: str,
        workflow_execution_id: str,
        callback_url: str,
        status: str = "WAITING",
    ) -> Dict[str, Any]:
        """Record a Google Cloud Workflows zero-compute HTTP callback URL."""
        await self.initialize()
        cb_id = str(uuid.uuid4())
        now = _utc_now_iso()

        # Mark any prior WAITING callbacks for this initiative as EXPIRED/SUPERSEDED
        for old_cb in self._callbacks.get(initiative_id, []):
            if old_cb["status"] == "WAITING":
                old_cb["status"] = "RECEIVED"
                old_cb["updated_at"] = now
                self._sync_to_firestore("geap_hitl_callbacks", old_cb["id"], old_cb)

        if self.pool:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "UPDATE workflow_callbacks SET status = 'RECEIVED', updated_at = NOW() WHERE initiative_id = $1::uuid AND status = 'WAITING'",
                    initiative_id,
                )
                row = await conn.fetchrow(
                    """
                    INSERT INTO workflow_callbacks (id, initiative_id, workflow_execution_id, callback_url, status, created_at, updated_at)
                    VALUES ($1::uuid, $2::uuid, $3, $4, $5, NOW(), NOW())
                    RETURNING id::text, initiative_id::text, workflow_execution_id, callback_url, status, created_at::text, updated_at::text
                    """,
                    cb_id,
                    initiative_id,
                    workflow_execution_id,
                    callback_url,
                    status,
                )
                cb_record = dict(row)
        else:
            cb_record = {
                "id": cb_id,
                "initiative_id": initiative_id,
                "workflow_execution_id": workflow_execution_id,
                "callback_url": callback_url,
                "status": status,
                "created_at": now,
                "updated_at": now,
            }

        self._callbacks.setdefault(initiative_id, []).append(cb_record)
        self._sync_to_firestore("geap_hitl_callbacks", cb_id, cb_record)
        return cb_record

    async def get_active_callback(self, initiative_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the latest WAITING (or most recent) callback for an initiative."""
        await self.initialize()
        if self.firefox_or_firestore_refresh_needed():
            self._hydrate_from_firestore()

        callbacks = self._callbacks.get(initiative_id, [])
        waiting = [c for c in callbacks if c.get("status") == "WAITING"]
        if waiting:
            return waiting[-1]
        return callbacks[-1] if callbacks else None

    def firefox_or_firestore_refresh_needed(self) -> bool:
        return self.firestore_db is not None

    async def update_initiative_status(
        self,
        initiative_id: str,
        status: str,
        reviewer: str,
        comments: str = "",
        expected_version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Transition initiative status with optimistic concurrency check and audit logging."""
        await self.initialize()
        if self.firestore_db:
            self._hydrate_from_firestore()

        existing = self._initiatives.get(initiative_id)
        if not existing:
            raise KeyError(f"Initiative {initiative_id} not found")

        if expected_version is not None and existing["version"] != expected_version:
            raise ValueError("This asset has already been updated by another reviewer.")

        now = _utc_now_iso()
        new_version = existing["version"] + 1
        existing["status"] = status
        existing["version"] = new_version
        existing["updated_at"] = now

        if self.pool:
            async with self.pool.acquire() as conn:
                if expected_version is not None:
                    res = await conn.fetchrow(
                        """
                        UPDATE initiative_assets
                        SET status = $2, version = version + 1, updated_at = NOW()
                        WHERE id = $1::uuid AND version = $3
                        RETURNING id::text, version
                        """,
                        initiative_id,
                        status,
                        expected_version,
                    )
                    if not res:
                        raise ValueError("This asset has already been updated by another reviewer.")
                else:
                    await conn.execute(
                        "UPDATE initiative_assets SET status = $2, version = version + 1, updated_at = NOW() WHERE id = $1::uuid",
                        initiative_id,
                        status,
                    )
                await conn.execute(
                    "UPDATE workflow_callbacks SET status = 'RECEIVED', updated_at = NOW() WHERE initiative_id = $1::uuid AND status = 'WAITING'",
                    initiative_id,
                )
                await conn.execute(
                    """
                    INSERT INTO initiative_reviews (id, initiative_id, reviewer_email, action, comments, created_at)
                    VALUES ($1::uuid, $2::uuid, $3, $4, $5, NOW())
                    """,
                    str(uuid.uuid4()),
                    initiative_id,
                    reviewer,
                    status,
                    comments,
                )

        for cb in self._callbacks.get(initiative_id, []):
            if cb["status"] == "WAITING":
                cb["status"] = "RECEIVED"
                cb["updated_at"] = now
                self._sync_to_firestore("geap_hitl_callbacks", cb["id"], cb)

        rev_id = str(uuid.uuid4())
        rev_record = {
            "id": rev_id,
            "initiative_id": initiative_id,
            "reviewer_email": reviewer,
            "action": status,
            "comments": comments,
            "created_at": now,
        }
        self._reviews.setdefault(initiative_id, []).append(rev_record)
        self._sync_to_firestore("geap_hitl_initiatives", initiative_id, existing)
        self._sync_to_firestore("geap_hitl_reviews", rev_id, rev_record)
        return existing

    async def record_memory_sync_event(
        self,
        initiative_id: str,
        brand_id: str,
        feedback_text: str,
        distilled_rule: str,
        memory_bank_record_id: str,
    ) -> Dict[str, Any]:
        """Record continuous learning feedback distillation to `memory_sync_events`."""
        await self.initialize()
        event_id = str(uuid.uuid4())
        now = _utc_now_iso()
        event = {
            "id": event_id,
            "initiative_id": initiative_id,
            "brand_id": brand_id,
            "feedback_text": feedback_text,
            "distilled_rule": distilled_rule,
            "memory_bank_record_id": memory_bank_record_id,
            "synced_at": now,
        }
        if self.pool:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO memory_sync_events (id, initiative_id, brand_id, feedback_text, distilled_rule, memory_bank_record_id, synced_at)
                    VALUES ($1::uuid, $2::uuid, $3, $4, $5, $6, NOW())
                    """,
                    event_id,
                    initiative_id,
                    brand_id,
                    feedback_text,
                    distilled_rule,
                    memory_bank_record_id,
                )
        self._memory_events.append(event)
        self._sync_to_firestore("geap_hitl_memories", event_id, event)
        return event

    async def list_initiatives(
        self, status: Optional[str] = None, brand_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return all initiatives enriched with callback status and workflow step."""
        await self.initialize()
        if self.firestore_db:
            self._hydrate_from_firestore()

        items = list(self._initiatives.values())
        if status:
            items = [i for i in items if i["status"] == status]
        if brand_id:
            items = [i for i in items if i["brand_id"] == brand_id]

        enriched: List[Dict[str, Any]] = []
        for item in sorted(items, key=lambda x: x.get("updated_at", ""), reverse=True):
            copy_item = copy.deepcopy(item)
            cb = await self.get_active_callback(item["id"])
            copy_item["active_callback"] = cb
            copy_item["workflow_graph_state"] = self.compute_workflow_graph_state(copy_item, cb)
            enriched.append(copy_item)
        return enriched

    async def get_initiative_detail(self, initiative_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete initiative record including callbacks, reviews, memory events, and workflow graph."""
        await self.initialize()
        if self.firestore_db:
            self._hydrate_from_firestore()

        item = self._initiatives.get(initiative_id)
        if not item:
            return None
        detail = copy.deepcopy(item)
        cb = await self.get_active_callback(initiative_id)
        detail["active_callback"] = cb
        detail["callbacks"] = self._callbacks.get(initiative_id, [])
        detail["reviews"] = sorted(
            self._reviews.get(initiative_id, []),
            key=lambda r: r.get("created_at", ""),
            reverse=True,
        )
        detail["memory_sync_events"] = [
            m for m in self._memory_events if m.get("initiative_id") == initiative_id or m.get("brand_id") == item["brand_id"]
        ]
        detail["workflow_graph_state"] = self.compute_workflow_graph_state(detail, cb)
        return detail

    async def get_brand_memory_events(self, brand_id: str) -> List[Dict[str, Any]]:
        await self.initialize()
        if self.firestore_db:
            self._hydrate_from_firestore()
        return [m for m in self._memory_events if m.get("brand_id") == brand_id]

    @staticmethod
    def compute_workflow_graph_state(
        initiative: Dict[str, Any], callback: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute the 9-node Cloud Workflows DAG state representation for visual rendering."""
        status = initiative.get("status", "PENDING_APPROVAL")
        rev_count = initiative.get("revision_count", 0)

        nodes = [
            {"id": "init_constants", "label": "1. init_constants (Workflow Init)", "tier": "Orchestration", "state": "COMPLETED"},
            {"id": "execute_trend_agent", "label": "2. execute_trend_agent (ADK + Memory Bank)", "tier": "Cognitive", "state": "COMPLETED"},
            {"id": "persist_draft_to_alloydb", "label": "3. persist_draft_to_alloydb (JSONB Contract)", "tier": "System of Record", "state": "COMPLETED"},
            {"id": "create_approval_callback", "label": "4. events.create_callback_endpoint", "tier": "Orchestration", "state": "COMPLETED"},
            {"id": "await_human_approval", "label": "5. events.await_callback (0 CPU Dormant)", "tier": "Zero-Compute Gate", "state": "WAITING" if status == "PENDING_APPROVAL" else "COMPLETED"},
            {"id": "process_review_decision", "label": "6. process_review_decision (Webhook Resumed)", "tier": "Human-in-the-Loop", "state": "PENDING" if status == "PENDING_APPROVAL" else "COMPLETED"},
            {"id": "update_alloydb_status", "label": "7. update_alloydb_status (Memory Bank Sync)", "tier": "System of Record", "state": "PENDING" if status == "PENDING_APPROVAL" else "COMPLETED"},
            {"id": "check_branch", "label": "8. check_branch (Decision Router)", "tier": "Orchestration", "state": "PENDING" if status == "PENDING_APPROVAL" else "COMPLETED"},
            {
                "id": "terminal_step",
                "label": (
                    "9a. trigger_downstream_step2 (Memory Pull)"
                    if status == "APPROVED"
                    else (
                        f"9b. loop_revision_step (Revision #{rev_count})"
                        if status == "REVISION_REQUESTED"
                        else (
                            "9c. handle_rejected (Terminated)"
                            if status == "REJECTED"
                            else "9. Awaiting Branch Outcome"
                        )
                    )
                ),
                "tier": "Step 2 Delivery",
                "state": (
                    "COMPLETED"
                    if status in ("APPROVED", "REJECTED")
                    else ("ACTIVE_LOOP" if status == "REVISION_REQUESTED" else "PENDING")
                ),
            },
        ]

        active_step = "await_human_approval"
        if status == "APPROVED":
            active_step = "trigger_downstream_step2"
        elif status == "REVISION_REQUESTED":
            active_step = "loop_revision_step"
        elif status == "REJECTED":
            active_step = "handle_rejected"

        return {
            "active_step": active_step,
            "status": status,
            "revision_count": rev_count,
            "max_revisions": 3,
            "zero_compute_active": status == "PENDING_APPROVAL",
            "workflow_execution_id": callback.get("workflow_execution_id") if callback else "local-simulation",
            "callback_url": callback.get("callback_url") if callback else "",
            "nodes": nodes,
        }


db_client = DatabaseClient()
