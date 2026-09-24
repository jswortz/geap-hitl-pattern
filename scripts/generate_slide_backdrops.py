"""Generate 2200x1240 (16:9, 720x405 pt) Google Cloud Advisory slide backdrops for Slides 9, 10, and 11."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

W, H = 2200, 1240


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


def _base_slide(eyebrow: str, title: str, subtitle: str) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 4-color Google Cloud top bar
    seg = W // 4
    draw.rectangle([(0, 0), (seg, 12)], fill=(66, 133, 244))
    draw.rectangle([(seg, 0), (seg * 2, 12)], fill=(234, 67, 53))
    draw.rectangle([(seg * 2, 0), (seg * 3, 12)], fill=(251, 188, 4))
    draw.rectangle([(seg * 3, 0), (W, 12)], fill=(52, 168, 83))

    f_eye = _font(18, bold=True)
    f_h1 = _font(38, bold=True)
    f_sub = _font(21, bold=False)

    draw.text((55, 34), eyebrow, fill=(95, 99, 104), font=f_eye)
    draw.text((55, 64), title, fill=(32, 33, 36), font=f_h1)
    draw.text((55, 114), subtitle, fill=(26, 115, 232), font=f_sub)
    return img, draw


def _draw_card(
    draw: ImageDraw.ImageDraw,
    rect: Tuple[int, int, int, int],
    top_color: Tuple[int, int, int],
    bg_color: Tuple[int, int, int] = (255, 255, 255),
) -> None:
    x, y, w, h = rect
    draw.rounded_rectangle([(x + 4, y + 6), (x + w + 4, y + h + 6)], radius=18, fill=(235, 239, 245))
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=18, fill=bg_color, outline=(218, 220, 224), width=2)
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
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    pw = (bbox[2] - bbox[0]) + 26
    ph = (bbox[3] - bbox[1]) + 14
    draw.rounded_rectangle([(x, y), (x + pw, y + ph)], radius=ph // 2, fill=bg)
    draw.text((x + 13, y + 6), text, fill=fg, font=font_obj)


def build_slide_09_backdrop() -> Path:
    """Slide 9: Left frame for animated HITL GIF (`x=55..1415, y=170..1045`), Right column cards for HITL pattern."""
    img, draw = _base_slide(
        "APPLICATION EXAMPLE  •  HUMAN-IN-THE-LOOP APPROVAL PROCESS (GITHUB.COM/JSWORTZ/GEAP-HITL-PATTERN)",
        "Live HITL Approval Workflow & Agent Platform Memory Bank",
        "Implementing the Zero-Compute Approval Gate (Slide 6) & Multi-Tiered State Longevity (Slide 4) on GCP",
    )

    f_pill = _font(14, bold=True)
    f_h2 = _font(22, bold=True)
    f_body = _font(16, bold=False)
    f_mono = _font(15, bold=True)

    # Left Frame where the Animated GIF (`hitl_approval_workflow.gif`) will be overlaid in Google Slides
    # In 720x405 pt coordinates: x=18pt (55px), y=56pt (170px), w=445pt (1360px), h=286pt (875px)
    draw.rounded_rectangle([(50, 165), (1420, 1050)], radius=18, fill=(15, 23, 42), outline=(26, 115, 232), width=3)

    # Bottom caption strip under GIF
    draw.rounded_rectangle([(50, 1068), (1420, 1185)], radius=14, fill=(241, 246, 254), outline=(174, 203, 250), width=2)
    draw.text((75, 1085), "LIVE CLOUD RUN DEPLOYMENT: https://approval-ui-679926387543.us-central1.run.app", fill=(26, 115, 232), font=f_mono)
    draw.text((75, 1116), "• Walks through Queue (/), Async Workflow Graph (/graph), and Asset Detail Card (/initiatives/{id})", fill=(55, 65, 81), font=f_body)
    draw.text((75, 1144), "• Demonstrates REVISION_REQUESTED feedback loop -> Memory Bank distillation -> Final APPROVED handoff", fill=(55, 65, 81), font=f_body)

    # Right Column Cards (3 stacked cards explaining how the repo reinforces prior slides)
    cards = [
        (
            "REINFORCES SLIDE 6  •  STEP 01 & 02",
            "Zero-Compute Callback Suspension",
            [
                "• Cloud Workflows calls events.create_callback_endpoint",
                "  and pauses at events.await_callback (0 CPU / $0.00 idle).",
                "• Eliminates synchronous open-socket anti-patterns.",
                "• Verified on GCP execution 33be042f-107b-4216-aa01.",
            ],
            (26, 115, 232),
            (232, 240, 254),
            165,
        ),
        (
            "REINFORCES SLIDE 4  •  CONTINUOUS LEARNING",
            "Agent Platform Memory Bank Sync",
            [
                "• Connected to reasoningEngines/5895016748914049024.",
                "• On Revision Request, calls POST .../memories:generate",
                "  & CreateMemory to consolidate reviewer critique.",
                "• Agent 1 re-executes Revision #1 applying the new rule.",
            ],
            (109, 40, 217),
            (245, 243, 255),
            515,
        ),
        (
            "REINFORCES SLIDE 5  •  STEP 04 RESOLUTION",
            "Clean Context Pull on 'Approve'",
            [
                "• Clicking Approve wakes the Cloud Workflow callback.",
                "• Calls pull_approved_step2_context() via memories:retrieve.",
                "• Step 2 receives ONLY the approved AlloyDB JSONB brief",
                "  + Memory Bank rules (0% upstream chat transcript drift!).",
            ],
            (19, 115, 51),
            (230, 244, 234),
            865,
        ),
    ]
    for badge_t, title_t, lines_t, color_t, badge_bg, cy in cards:
        _draw_card(draw, (1455, cy, 695, 320), top_color=color_t)
        _draw_pill(draw, 1480, cy + 26, badge_t, badge_bg, color_t, f_pill)
        draw.text((1480, cy + 72), title_t, fill=(32, 33, 36), font=f_h2)
        for idx, line in enumerate(lines_t):
            draw.text((1480, cy + 116 + idx * 36), line, fill=(55, 65, 81), font=f_body)

    out = ASSETS_DIR / "slide_09_hitl_backdrop.png"
    img.save(out, format="PNG", optimize=True)
    return out


def build_slide_10_backdrop() -> Path:
    """Slide 10: Left frame for animated Async Workflow Graph GIF, Right column cards for DAG & Cadence Isolation."""
    img, draw = _base_slide(
        "APPLICATION EXAMPLE  •  ASYNCHRONOUS WORKFLOW GRAPH & STATE MACHINE CHOREOGRAPHY",
        "Asynchronous Multi-Artifact Workflow Graph Progression",
        "Visualizing 9-Node Google Cloud Workflows State Transitions Across Multiple Brand Initiatives",
    )

    f_pill = _font(14, bold=True)
    f_h2 = _font(22, bold=True)
    f_body = _font(16, bold=False)
    f_mono = _font(15, bold=True)

    # Left Frame where the Animated GIF (`async_workflow_graph.gif`) will be overlaid
    draw.rounded_rectangle([(50, 165), (1420, 1050)], radius=18, fill=(9, 13, 24), outline=(52, 168, 83), width=3)

    # Bottom caption strip under GIF
    draw.rounded_rectangle([(50, 1068), (1420, 1185)], radius=14, fill=(236, 253, 245), outline=(110, 231, 183), width=2)
    draw.text((75, 1085), "ORCHESTRATOR: workflows/trend_discovery_flow.yaml (Deployed in us-central1)", fill=(5, 122, 85), font=f_mono)
    draw.text((75, 1116), "• Tracks brand_apex, brand_aurora, and brand_lumina progressing independently across 9 DAG nodes", fill=(55, 65, 81), font=f_body)
    draw.text((75, 1144), "• Shows concurrent zero-compute waiting, asynchronous revision looping, and Step 2 Eventarc delivery", fill=(55, 65, 81), font=f_body)

    cards = [
        (
            "REINFORCES SLIDE 3  •  MACRO ORCHESTRATION",
            "Decoupled State Machine vs. GEAP",
            [
                "• Proves why GEAP is paired with Cloud Workflows:",
                "  GEAP executes fast cognitive turns (~4s), while",
                "  Cloud Workflows manages multi-week sleep states.",
                "• Zero active containers while waiting at Node 5.",
            ],
            (234, 67, 53),
            (254, 242, 242),
            165,
        ),
        (
            "REINFORCES SLIDE 5  •  CADENCE ISOLATION",
            "Independent Multi-Brand Cadences",
            [
                "• brand_lumina completes Step 2 handoff immediately,",
                "  while brand_apex loops through Node 7 (Revision #1)",
                "  and brand_aurora waits at Node 5 (0-CPU callback).",
                "• Prevents cross-brand blocking or queue starvation.",
            ],
            (251, 188, 4),
            (254, 247, 224),
            515,
        ),
        (
            "REINFORCES SLIDE 7  •  ENTERPRISE GOVERNANCE",
            "Recursion & Concurrency Guardrails",
            [
                "• Enforces max_revisions: 3 in trend_discovery_flow.yaml",
                "  before escalating to ESCALATED_MANUAL_REVIEW.",
                "• Optimistic locking (version check in AlloyDB) blocks",
                "  conflicting concurrent approvals with HTTP 409.",
            ],
            (26, 115, 232),
            (232, 240, 254),
            865,
        ),
    ]
    for badge_t, title_t, lines_t, color_t, badge_bg, cy in cards:
        _draw_card(draw, (1455, cy, 695, 320), top_color=color_t)
        _draw_pill(draw, 1480, cy + 26, badge_t, badge_bg, color_t, f_pill)
        draw.text((1480, cy + 72), title_t, fill=(32, 33, 36), font=f_h2)
        for idx, line in enumerate(lines_t):
            draw.text((1480, cy + 116 + idx * 36), line, fill=(55, 65, 81), font=f_body)

    out = ASSETS_DIR / "slide_10_graph_backdrop.png"
    img.save(out, format="PNG", optimize=True)
    return out


def build_slide_11_mapping() -> Path:
    """Slide 11: 4-Column / 2x2 Matrix showing how the Repository directly implements every Advisory Recommendation."""
    img, draw = _base_slide(
        "ARCHITECTURAL TRACEABILITY  •  HOW THE REPOSITORY REINFORCES THE ADVISORY RECOMMENDATIONS",
        "From Advisory Architecture to Deployed Production Code",
        "1:1 Mapping Between Slides 3–7 Architectural Mandates and github.com/jswortz/geap-hitl-pattern",
    )

    f_pill = _font(14, bold=True)
    f_h2 = _font(24, bold=True)
    f_sub_h = _font(17, bold=True)
    f_body = _font(16, bold=False)
    f_mono = _font(15, bold=True)

    quadrants = [
        (
            "1. SLIDE 3 & 7 MANDATE: SEPARATE COGNITION FROM ORCHESTRATION",
            "Google Cloud Workflows + ADK Agent Service",
            "workflows/trend_discovery_flow.yaml  |  services/trend_agent/agent.py",
            [
                "• Advisory Mandate: Never use ephemeral agent sessions as a multi-week workflow engine.",
                "• Repo Proof: Cloud Workflows manages the 9-step lifecycle, OIDC service-to-service calls,",
                "  and 30-day durable suspension (events.await_callback), while ADK handles bounded Gemini turns.",
            ],
            (26, 115, 232),
            (232, 240, 254),
            (55, 175, 1020, 465),
        ),
        (
            "2. SLIDE 4 MANDATE: 4-PILLAR STATE & AGENT PLATFORM MEMORY BANK",
            "Live Memory Bank API + AlloyDB System of Record",
            "services/trend_agent/tools/memory_tool.py  |  database/migrations/001_initial_schema.sql",
            [
                "• Advisory Mandate: Pair ephemeral session cache with persistent Memory Bank & ACID database.",
                "• Repo Proof: Integrates Vertex AI Agent Platform Memory Bank (reasoningEngines/5895016748914049024)",
                "  using memories:retrieve, memories:generate, and CreateMemory + AlloyDB JSONB tables.",
            ],
            (234, 67, 53),
            (254, 242, 242),
            (1125, 175, 1020, 465),
        ),
        (
            "3. SLIDE 5 MANDATE: REPLACE MACRO A2A PIPING WITH JSON CONTRACTS",
            "Pydantic Schema Enforcement & Clean Step 2 Context Pull",
            "services/trend_agent/schemas.py  |  services/data_service/routes/initiatives.py",
            [
                "• Advisory Mandate: Eliminate direct conversational transcript piping across value stream steps.",
                "• Repo Proof: Enforces strict InitiativeIdeaBrief Pydantic validation + citation verification.",
                "  On Approve, pull_approved_step2_context() hydrates Step 2 strictly from AlloyDB + Memory Bank.",
            ],
            (251, 188, 4),
            (254, 247, 224),
            (55, 680, 1020, 465),
        ),
        (
            "4. SLIDE 6 & 7 MANDATE: ZERO-COMPUTE HITL & DETERMINISTIC EVALS",
            "Antigravity Evaluation Suite (100% Pass Rate) & Pytest Suite",
            "evals/run_evals.py  |  tests/integration/test_e2e_workflow.py",
            [
                "• Advisory Mandate: Validate agent output as software with deterministic rubrics before handoff.",
                "• Repo Proof: 4 automated rubrics (Schema Conformance 1.0, Grounding Accuracy 1.0, Memory",
                "  Compliance 1.0, Tone Alignment 0.96) + 9/9 unit & E2E integration tests passing.",
            ],
            (52, 168, 83),
            (230, 244, 234),
            (1125, 680, 1020, 465),
        ),
    ]

    for badge_t, title_t, code_t, bullets_t, color_t, badge_bg, rect in quadrants:
        x, y, w, h = rect
        _draw_card(draw, rect, top_color=color_t)
        _draw_pill(draw, x + 30, y + 30, badge_t, badge_bg, color_t, f_pill)
        draw.text((x + 30, y + 84), title_t, fill=(32, 33, 36), font=f_h2)
        draw.rounded_rectangle([(x + 30, y + 128), (x + w - 30, y + 170)], radius=8, fill=(241, 245, 249))
        draw.text((x + 44, y + 140), f"Code: {code_t}", fill=(26, 115, 232), font=f_mono)
        for idx, b_line in enumerate(bullets_t):
            draw.text((x + 30, y + 195 + idx * 42), b_line, fill=(55, 65, 81), font=f_body)

    out = ASSETS_DIR / "slide_11_recommendations_mapping.png"
    img.save(out, format="PNG", optimize=True)
    return out


if __name__ == "__main__":
    p9 = build_slide_09_backdrop()
    p10 = build_slide_10_backdrop()
    p11 = build_slide_11_mapping()
    print("Generated slide backdrops:", p9.name, p10.name, p11.name)
