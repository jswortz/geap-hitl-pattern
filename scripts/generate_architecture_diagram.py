"""Generate a high-resolution (2200x1240) Google Cloud Advisory Architecture Diagram for the repository & Google Slides."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _draw_card(
    draw: ImageDraw.ImageDraw,
    rect: Tuple[int, int, int, int],
    top_color: Tuple[int, int, int],
    bg_color: Tuple[int, int, int] = (255, 255, 255),
    border_color: Tuple[int, int, int] = (218, 220, 224),
) -> None:
    x, y, w, h = rect
    # Soft drop shadow
    draw.rounded_rectangle([(x + 4, y + 6), (x + w + 4, y + h + 6)], radius=18, fill=(232, 236, 242))
    # Main card body
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=18, fill=bg_color, outline=border_color, width=2)
    # Top accent bar
    draw.rounded_rectangle([(x, y), (x + w, y + 12)], radius=18, fill=top_color)
    draw.rectangle([(x, y + 6), (x + w, y + 12)], fill=top_color)


def _draw_pill(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    bg: Tuple[int, int, int],
    fg: Tuple[int, int, int],
    font_obj: ImageFont.ImageFont,
) -> int:
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pw = tw + 26
    ph = th + 14
    draw.rounded_rectangle([(x, y), (x + pw, y + ph)], radius=ph // 2, fill=bg)
    draw.text((x + 13, y + 6), text, fill=fg, font=font_obj)
    return pw


def _draw_arrow(
    draw: ImageDraw.ImageDraw,
    p1: Tuple[int, int],
    p2: Tuple[int, int],
    color: Tuple[int, int, int],
    label: str = "",
    font_obj: ImageFont.ImageFont | None = None,
) -> None:
    draw.line([p1, p2], fill=color, width=5)
    # Arrowhead at p2
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if abs(dx) >= abs(dy):
        sign = 1 if dx > 0 else -1
        pts = [p2, (p2[0] - 16 * sign, p2[1] - 10), (p2[0] - 16 * sign, p2[1] + 10)]
    else:
        sign = 1 if dy > 0 else -1
        pts = [p2, (p2[0] - 10, p2[1] - 16 * sign), (p2[0] + 10, p2[1] - 16 * sign)]
    draw.polygon(pts, fill=color)
    if label and font_obj:
        mx = (p1[0] + p2[0]) // 2
        my = (p1[1] + p2[1]) // 2
        bbox = draw.textbbox((0, 0), label, font=font_obj)
        lw = bbox[2] - bbox[0] + 18
        lh = bbox[3] - bbox[1] + 10
        draw.rounded_rectangle([(mx - lw // 2, my - lh // 2), (mx + lw // 2, my + lh // 2)], radius=8, fill=(255, 255, 255), outline=color, width=2)
        draw.text((mx - lw // 2 + 9, my - lh // 2 + 4), label, fill=(32, 33, 36), font=font_obj)


def generate_diagram() -> Path:
    W, H = 2200, 1240
    img = Image.new("RGB", (W, H), (248, 250, 252))
    draw = ImageDraw.Draw(img)

    # 4-Color Google Top Ribbon
    seg = W // 4
    draw.rectangle([(0, 0), (seg, 12)], fill=(66, 133, 244))
    draw.rectangle([(seg, 0), (seg * 2, 12)], fill=(234, 67, 53))
    draw.rectangle([(seg * 2, 0), (seg * 3, 12)], fill=(251, 188, 4))
    draw.rectangle([(seg * 3, 0), (W, 12)], fill=(52, 168, 83))

    f_eyebrow = _font(17, bold=True)
    f_h1 = _font(35, bold=True)
    f_sub = _font(20, bold=False)
    f_card_title = _font(23, bold=True)
    f_sec_title = _font(17, bold=True)
    f_body = _font(14, bold=False)
    f_mono = _font(14, bold=True)
    f_pill = _font(13, bold=True)

    # Header Banner
    draw.text((50, 32), "GOOGLE CLOUD REFERENCE IMPLEMENTATION  •  PROJECT: WORTZ-PROJECT-352116 (US-CENTRAL1)", fill=(95, 99, 104), font=f_eyebrow)
    draw.text((50, 62), "Brand Building HITL Approval Example Application — 3-Tier Architecture", fill=(32, 33, 36), font=f_h1)
    draw.text((50, 110), "Contract-Driven Handoffs, Zero-Compute Cloud Workflows Callbacks, Agent Platform Memory Bank, and AlloyDB System of Record", fill=(26, 115, 232), font=f_sub)

    # -------------------------------------------------------------------------
    # COLUMN 1: TIER 1 & TIER 2 (COGNITIVE TIER & AGENT PLATFORM MEMORY BANK)
    # -------------------------------------------------------------------------
    _draw_card(draw, (45, 165, 625, 660), top_color=(26, 115, 232))
    _draw_pill(draw, 70, 195, "TIER 1 & 2  •  COGNITIVE & MEMORY TIER", (232, 240, 254), (26, 115, 232), f_pill)
    draw.text((70, 240), "ADK Trend Discovery Agent (Agent 1)", fill=(32, 33, 36), font=f_card_title)
    draw.text((70, 274), "Cloud Run: trend-agent-service  •  Model: gemini-2.5-flash", fill=(95, 99, 104), font=f_mono)

    # Sub-box 1A: Google Search Grounding
    draw.rounded_rectangle([(70, 314), (645, 442)], radius=14, fill=(241, 246, 254), outline=(174, 203, 250), width=2)
    draw.text((90, 328), "1. Google Search Grounding Tool (search_tool.py)", fill=(26, 115, 232), font=f_sec_title)
    draw.text((90, 358), "• Queries live category consumer & sustainability signals", fill=(55, 65, 81), font=f_body)
    draw.text((90, 383), "• Deterministic citation filter strips unverified URLs (0% hallucination)", fill=(55, 65, 81), font=f_body)
    draw.text((90, 408), "• Fallback query broadening & exponential backoff rate-limit guards", fill=(55, 65, 81), font=f_body)

    # Sub-box 1B: Gemini Enterprise Agent Platform Memory Bank
    draw.rounded_rectangle([(70, 458), (645, 638)], radius=14, fill=(245, 243, 255), outline=(196, 181, 253), width=2)
    draw.text((90, 472), "2. Agent Platform Memory Bank (memory_tool.py)", fill=(109, 40, 217), font=f_sec_title)
    draw.text((90, 498), "Resource: reasoningEngines/5895016748914049024/memories", fill=(91, 33, 182), font=f_mono)
    draw.text((90, 526), "• Pre-Execution: POST .../memories:retrieve (scoped to brand_id)", fill=(55, 65, 81), font=f_body)
    draw.text((90, 551), "• Post-Review: POST .../memories:generate & CreateMemory", fill=(55, 65, 81), font=f_body)
    draw.text((90, 576), "• Resolves contradictory rules by 90-day timestamp recency", fill=(55, 65, 81), font=f_body)
    draw.text((90, 601), "• Cold-start brand baseline fallback initialization", fill=(55, 65, 81), font=f_body)

    # Sub-box 1C: Strict Pydantic Output Contract
    draw.rounded_rectangle([(70, 654), (645, 800)], radius=14, fill=(236, 253, 245), outline=(110, 231, 183), width=2)
    draw.text((90, 668), "3. Schema Contract: InitiativeIdeaBrief (schemas.py)", fill=(5, 122, 85), font=f_sec_title)
    draw.text((90, 698), "• Enforced via JSON response schema + self-correction loop", fill=(55, 65, 81), font=f_body)
    draw.text((90, 723), "• Emits strongly typed JSON contract (citations, memories, hooks)", fill=(55, 65, 81), font=f_body)
    draw.text((90, 748), "• Eliminates direct macro A2A chat transcript piping", fill=(55, 65, 81), font=f_body)

    # -------------------------------------------------------------------------
    # COLUMN 2: TIER 3 (DURABLE ORCHESTRATION — GOOGLE CLOUD WORKFLOWS)
    # -------------------------------------------------------------------------
    _draw_card(draw, (785, 165, 630, 660), top_color=(234, 67, 53))
    _draw_pill(draw, 810, 195, "TIER 3  •  SERVERLESS DURABLE ORCHESTRATOR", (254, 242, 242), (217, 48, 37), f_pill)
    draw.text((810, 240), "Google Cloud Workflows State Machine", fill=(32, 33, 36), font=f_card_title)
    draw.text((810, 274), "Workflow: trend_discovery_flow.yaml  •  OIDC Authenticated", fill=(95, 99, 104), font=f_mono)

    # Workflow DAG Steps inside Column 2
    wf_steps = [
        ("Step 1–2: init_constants & execute_trend_agent", "Invokes ADK Agent Service via OIDC POST", (241, 245, 249), (100, 116, 139)),
        ("Step 3: persist_draft_to_alloydb", "Writes validated JSONB brief (status = PENDING_APPROVAL)", (241, 245, 249), (100, 116, 139)),
        ("Step 4: events.create_callback_endpoint", "Generates unique authenticated HTTP POST webhook URL", (254, 249, 195), (180, 83, 9)),
        ("Step 5: events.await_callback (ZERO-COMPUTE GATE)", "Suspends up to 30 days — 0 CPU, 0 RAM, $0.00 LLM Quota!", (254, 243, 199), (217, 119, 6)),
        ("Step 6–7: process_review_decision & update_status", "Wakes on Reviewer POST -> Updates AlloyDB & Memory Bank", (236, 253, 245), (5, 122, 85)),
        ("Step 8–9: check_branch (Decision Router)", "APPROVED -> Step 2  |  REVISION_REQUESTED -> Loop (max 3x)", (239, 246, 255), (29, 78, 216)),
    ]
    sy = 314
    for title_s, sub_s, s_bg, s_border in wf_steps:
        draw.rounded_rectangle([(810, sy), (1390, sy + 72)], radius=12, fill=s_bg, outline=s_border, width=2)
        draw.text((828, sy + 11), title_s, fill=(32, 33, 36), font=f_sec_title)
        draw.text((828, sy + 40), sub_s, fill=(71, 85, 105), font=f_body)
        sy += 82

    # -------------------------------------------------------------------------
    # COLUMN 3: TIER 4 (ALLOYDB SYSTEM OF RECORD) & HITL WEB APPLICATION
    # -------------------------------------------------------------------------
    _draw_card(draw, (1530, 165, 625, 320), top_color=(52, 168, 83))
    _draw_pill(draw, 1555, 195, "TIER 4  •  ENTERPRISE SYSTEM OF RECORD", (230, 244, 234), (19, 115, 51), f_pill)
    draw.text((1555, 240), "AlloyDB for PostgreSQL + Data Service", fill=(32, 33, 36), font=f_card_title)
    draw.text((1555, 274), "Cloud Run: data-service  •  DDL: 001_initial_schema.sql", fill=(95, 99, 104), font=f_mono)
    draw.text((1555, 312), "• initiative_assets: Versioned JSONB briefs & optimistic locking", fill=(55, 65, 81), font=f_body)
    draw.text((1555, 342), "• workflow_callbacks: Active execution IDs & WAITING URLs", fill=(55, 65, 81), font=f_body)
    draw.text((1555, 372), "• initiative_reviews: Immutable compliance sign-off audit log", fill=(55, 65, 81), font=f_body)
    draw.text((1555, 402), "• memory_sync_events: Continuous learning distillation log", fill=(55, 65, 81), font=f_body)
    draw.text((1555, 432), "• Isolated Agent Read Pool vs. ACID Workflow Write Pool", fill=(19, 115, 51), font=f_sec_title)

    # HITL Web Interface Card
    _draw_card(draw, (1530, 505, 625, 320), top_color=(251, 188, 4))
    _draw_pill(draw, 1555, 535, "COMPONENT D  •  HUMAN-IN-THE-LOOP INTERFACE", (254, 247, 224), (176, 96, 0), f_pill)
    draw.text((1555, 580), "Brand Building HITL Approval Web UI", fill=(32, 33, 36), font=f_card_title)
    draw.text((1555, 614), "Cloud Run: approval-ui  •  Views: / (Queue), /graph, /initiatives/{id}", fill=(95, 99, 104), font=f_mono)
    draw.text((1555, 652), "• Renders verified Search Grounding citations & Memory Matrix", fill=(55, 65, 81), font=f_body)
    draw.text((1555, 682), "• Interactive 9-Node Asynchronous Workflow Graph Visualizer", fill=(55, 65, 81), font=f_body)
    draw.text((1555, 712), "• Approve / Request Revision / Reject buttons fire OAuth2 POST", fill=(55, 65, 81), font=f_body)
    draw.text((1555, 742), "  directly to Cloud Workflows callback endpoint", fill=(55, 65, 81), font=f_body)

    # -------------------------------------------------------------------------
    # BOTTOM BANNER: STEP 2 CONTRACT-DRIVEN HANDOFF & MEMORY BANK CONTEXT PULL
    # -------------------------------------------------------------------------
    _draw_card(draw, (45, 865, 2110, 325), top_color=(16, 185, 129), bg_color=(240, 253, 244), border_color=(16, 185, 129))
    _draw_pill(draw, 75, 895, "DOWNSTREAM VALUE STREAM HANDOFF (REINFORCING ADVISORY RECOMMENDATIONS)", (209, 250, 229), (6, 95, 70), f_pill)
    draw.text((75, 940), "What Happens When the Reviewer Clicks 'Approve': Contract + Memory Bank Context Pull", fill=(6, 78, 59), font=f_card_title)

    b_boxes = [
        (
            "1. Zero-Compute Callback Resumes",
            "approval-ui POSTs {decision: 'APPROVED'} to events.await_callback.\nCloud Workflows wakes from 0-CPU dormancy in <100ms.",
            (75, 988, 655, 175),
        ),
        (
            "2. Positive Memory Distillation (memories:generate)",
            "Approved headline & sign-off notes are distilled via Gemini into\nAgent Platform Memory Bank (reasoningEngines/.../memories).",
            (772, 988, 655, 175),
        ),
        (
            "3. Clean Step 2 Context Pull (pull_approved_step2_context)",
            "Step 2 Creative Asset Agent pulls ONLY the approved AlloyDB JSONB\ncontract + fresh Memory Bank rules (0% upstream chat bloat!).",
            (1470, 988, 655, 175),
        ),
    ]
    for b_title, b_desc, (bx, by, bw, bh) in b_boxes:
        draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=14, fill=(255, 255, 255), outline=(110, 231, 183), width=2)
        draw.text((bx + 20, by + 18), b_title, fill=(6, 95, 70), font=f_sec_title)
        for idx, line in enumerate(b_desc.splitlines()):
            draw.text((bx + 20, by + 56 + idx * 30), line, fill=(55, 65, 81), font=f_body)

    # Inter-Tier Arrows in the 115px wide alleys (670..785 and 1415..1530)
    _draw_arrow(draw, (785, 350), (670, 350), (26, 115, 232), "OIDC POST", f_pill)
    _draw_arrow(draw, (670, 725), (785, 725), (5, 122, 85), "JSONB Brief", f_pill)
    _draw_arrow(draw, (1415, 330), (1530, 330), (19, 115, 51), "ACID Write", f_pill)
    _draw_arrow(draw, (1530, 620), (1415, 620), (217, 119, 6), "Webhook", f_pill)

    out_path = ASSETS_DIR / "architecture_diagram.png"
    img.save(out_path, format="PNG", optimize=True)
    return out_path


if __name__ == "__main__":
    p = generate_diagram()
    print(f"Generated architecture diagram: {p} ({p.stat().st_size // 1024} KB)")
