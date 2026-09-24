"""Record high-resolution animated GIFs of the Human-in-the-Loop (HITL) process and Asynchronous Workflow Graph.

Generates:
1. `docs/assets/hitl_approval_workflow.gif`: Live Playwright browser recording of the HITL review queue, grounding & memory inspection, revision loop with Vertex AI Memory Bank distillation, and final Cloud Workflows callback approval.
2. `docs/assets/async_workflow_graph.gif`: Visual representation of the 9-node Cloud Workflows DAG & 3-Tier Architecture as multiple brand artifacts (`brand_apex`, `brand_aurora`, `brand_lumina`) transition asynchronously across states.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _annotate_frame(img: Image.Image, step_num: int, total_steps: int, title: str, subtitle: str, badge_color: Tuple[int, int, int]) -> Image.Image:
    """Overlay a clean bottom HUD banner on browser screenshots to explain the active HITL & Cloud Workflows stage."""
    canvas = img.convert("RGBA")
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    w, h = canvas.size
    bar_h = 84
    draw.rectangle([(0, h - bar_h), (w, h)], fill=(9, 14, 28, 235))
    draw.line([(0, h - bar_h), (w, h - bar_h)], fill=badge_color + (255,), width=3)

    font_badge = _load_font(14, bold=True)
    font_title = _load_font(19, bold=True)
    font_sub = _load_font(14, bold=False)

    # Step Pill
    pill_text = f"STEP {step_num}/{total_steps}"
    draw.rounded_rectangle([(24, h - bar_h + 18), (138, h - bar_h + 50)], radius=8, fill=badge_color + (255,))
    draw.text((38, h - bar_h + 25), pill_text, fill=(10, 15, 25, 255), font=font_badge)

    # Title & Subtitle
    draw.text((156, h - bar_h + 15), title, fill=(255, 255, 255, 255), font=font_title)
    draw.text((156, h - bar_h + 44), subtitle, fill=(185, 200, 225, 255), font=font_sub)

    return Image.alpha_composite(canvas, overlay).convert("RGB")


def generate_async_workflow_dag_frames() -> List[Image.Image]:
    """Render a 12-frame high-resolution animated diagram of the Cloud Workflows DAG & asynchronous artifact transitions."""
    width, height = 1400, 860
    font_h1 = _load_font(24, bold=True)
    font_h2 = _load_font(15, bold=True)
    font_body = _load_font(13, bold=False)
    font_mono = _load_font(12, bold=True)

    # Define the 9 DAG nodes with spacious coordinates (x, y, w, h) so all text has >= 24px margin
    dag_nodes = [
        {"id": "n1", "title": "1. init_constants", "sub": "Cloud Workflows Init", "tier": "ORCHESTRATION", "rect": (45, 145, 290, 96)},
        {"id": "n2", "title": "2. execute_trend_agent", "sub": "ADK + Search + Memory Bank", "tier": "COGNITIVE TIER", "rect": (375, 145, 310, 96)},
        {"id": "n3", "title": "3. persist_draft_alloydb", "sub": "JSONB Contract (PENDING)", "tier": "SYSTEM OF RECORD", "rect": (725, 145, 300, 96)},
        {"id": "n4", "title": "4. create_callback", "sub": "events.create_callback_endpoint", "tier": "ORCHESTRATION", "rect": (1065, 145, 290, 96)},
        {"id": "n5", "title": "5. await_human_approval", "sub": "events.await_callback (0 CPU Dormant)", "tier": "ZERO-COMPUTE GATE", "rect": (500, 325, 400, 112)},
        {"id": "n6", "title": "6. process_review_decision", "sub": "Webhook POST Resumes Execution", "tier": "HITL CALLBACK", "rect": (500, 495, 400, 96)},
        {"id": "n7", "title": "7. loop_revision_step", "sub": "Memory Bank:generate & Loop", "tier": "FEEDBACK LOOP", "rect": (65, 385, 355, 108)},
        {"id": "n8", "title": "8. update_alloydb_status", "sub": "ACID Commit + Audit Trail", "tier": "SYSTEM OF RECORD", "rect": (500, 640, 400, 92)},
        {"id": "n9", "title": "9. trigger_downstream_step2", "sub": "Memory Bank:retrieve + Step 2", "tier": "STEP 2 DELIVERY", "rect": (965, 555, 390, 125)},
    ]

    # 10 timeline states showing asynchronous progression of 3 brand initiatives
    timeline_states = [
        {
            "caption": "Frame 1/10: Cloud Workflows Triggered for Brand Apex & Brand Aurora (Lumina Approved)",
            "detail": "Agent 1 queries Google Search Grounding + Vertex AI Memory Bank (`brands/{brand_id}/guidelines`)",
            "active_nodes": {"n1": "DONE", "n2": "ACTIVE_BLUE", "n9": "APPROVED"},
            "tokens": [
                ("brand_apex (v1)", "n2", (59, 130, 246)),
                ("brand_aurora (v1)", "n3", (99, 102, 241)),
                ("brand_lumina (v2)", "n9", (16, 185, 129)),
            ],
            "active_edge": ("n1", "n2"),
        },
        {
            "caption": "Frame 2/10: Schema-Validated JSONB Persisted & Zero-Compute Callback Created",
            "detail": "Cloud Workflows calls `events.create_callback_endpoint` and commits callback URL to AlloyDB",
            "active_nodes": {"n1": "DONE", "n2": "DONE", "n3": "DONE", "n4": "ACTIVE_BLUE", "n5": "WAITING", "n9": "APPROVED"},
            "tokens": [
                ("brand_apex (v1)", "n4", (59, 130, 246)),
                ("brand_aurora (v1)", "n5", (245, 158, 11)),
                ("brand_lumina (v2)", "n9", (16, 185, 129)),
            ],
            "active_edge": ("n3", "n4"),
        },
        {
            "caption": "Frame 3/10: Both Initiatives Suspended at `events.await_callback` (Zero Compute / $0.00 Idle)",
            "detail": "Container threads released; zero CPU or LLM quota consumed while awaiting Brand Director review",
            "active_nodes": {"n1": "DONE", "n2": "DONE", "n3": "DONE", "n4": "DONE", "n5": "WAITING", "n9": "APPROVED"},
            "tokens": [
                ("brand_apex (v1) [WAITING]", "n5", (245, 158, 11)),
                ("brand_aurora (v1) [WAITING]", "n5", (245, 158, 11)),
                ("brand_lumina (v2) [STEP 2]", "n9", (16, 185, 129)),
            ],
            "active_edge": ("n4", "n5"),
        },
        {
            "caption": "Frame 4/10: Reviewer Submits `REVISION_REQUESTED` on Brand Apex via Approval UI",
            "detail": "Authenticated POST hits Cloud Workflows callback URL -> Execution wakes up at `process_review_decision`",
            "active_nodes": {"n5": "WAITING", "n6": "ACTIVE_AMBER", "n9": "APPROVED"},
            "tokens": [
                ("brand_apex (REVISION_REQ)", "n6", (245, 158, 11)),
                ("brand_aurora (v1) [WAITING]", "n5", (245, 158, 11)),
                ("brand_lumina (v2) [STEP 2]", "n9", (16, 185, 129)),
            ],
            "active_edge": ("n5", "n6"),
        },
        {
            "caption": "Frame 5/10: Continuous Learning Loop — Critique Distilled into Vertex AI Memory Bank",
            "detail": "`loop_revision_step` writes distilled rule `mem_sync` to Memory Bank and loops back to Agent 1",
            "active_nodes": {"n5": "WAITING", "n7": "ACTIVE_PURPLE", "n9": "APPROVED"},
            "tokens": [
                ("brand_apex (Rev #1 + Memory Sync)", "n7", (168, 85, 247)),
                ("brand_aurora (v1) [WAITING]", "n5", (245, 158, 11)),
                ("brand_lumina (v2) [STEP 2]", "n9", (16, 185, 129)),
            ],
            "active_edge": ("n6", "n7"),
        },
        {
            "caption": "Frame 6/10: Agent 1 Re-Executes with New Memory Directive (`Revision #1` -> `v2`)",
            "detail": "Brand Apex v2 brief incorporates reviewer directive & re-suspends at `events.await_callback`",
            "active_nodes": {"n2": "ACTIVE_PURPLE", "n5": "WAITING", "n9": "APPROVED"},
            "tokens": [
                ("brand_apex (v2 • Rev #1)", "n2", (168, 85, 247)),
                ("brand_aurora (v1) [WAITING]", "n5", (245, 158, 11)),
                ("brand_lumina (v2) [STEP 2]", "n9", (16, 185, 129)),
            ],
            "active_edge": ("n7", "n2"),
        },
        {
            "caption": "Frame 7/10: Asynchronous Approval #1 — Brand Aurora Approved While Brand Apex Re-Queues",
            "detail": "Brand Aurora callback receives `APPROVED` -> Updates AlloyDB `status=APPROVED`",
            "active_nodes": {"n5": "WAITING", "n6": "DONE", "n8": "ACTIVE_GREEN", "n9": "APPROVED"},
            "tokens": [
                ("brand_apex (v2) [WAITING]", "n5", (245, 158, 11)),
                ("brand_aurora (v2) [APPROVING]", "n8", (16, 185, 129)),
                ("brand_lumina (v2) [STEP 2]", "n9", (16, 185, 129)),
            ],
            "active_edge": ("n6", "n8"),
        },
        {
            "caption": "Frame 8/10: Brand Aurora Transitions to `trigger_downstream_step2` (Eventarc Handoff)",
            "detail": "2 of 3 initiatives now in `APPROVED` state; Brand Apex (v2) ready for final sign-off",
            "active_nodes": {"n5": "WAITING", "n8": "DONE", "n9": "APPROVED"},
            "tokens": [
                ("brand_apex (v2) [WAITING]", "n5", (245, 158, 11)),
                ("brand_aurora (v2) [APPROVED]", "n9", (16, 185, 129)),
                ("brand_lumina (v2) [APPROVED]", "n9", (16, 185, 129)),
            ],
            "active_edge": ("n8", "n9"),
        },
        {
            "caption": "Frame 9/10: Final Approval — Brand Director Clicks Approve on Revised Brand Apex (v2)",
            "detail": "Webhook callback resumes `trend_discovery_flow` -> AlloyDB ACID commit `status=APPROVED`",
            "active_nodes": {"n6": "ACTIVE_GREEN", "n8": "ACTIVE_GREEN", "n9": "APPROVED"},
            "tokens": [
                ("brand_apex (v2) [RESUMED]", "n8", (16, 185, 129)),
                ("brand_aurora (v2) [APPROVED]", "n9", (16, 185, 129)),
                ("brand_lumina (v2) [APPROVED]", "n9", (16, 185, 129)),
            ],
            "active_edge": ("n6", "n8"),
        },
        {
            "caption": "Frame 10/10: All 3 Brand Initiatives Approved Asynchronously! (`SUCCEEDED` -> Step 2)",
            "detail": "100% Schema-Validated JSONB Contracts Committed in AlloyDB + Continuous Learning Synced",
            "active_nodes": {"n1": "DONE", "n2": "DONE", "n3": "DONE", "n4": "DONE", "n5": "DONE", "n6": "DONE", "n8": "DONE", "n9": "APPROVED"},
            "tokens": [
                ("brand_apex (v2 • Rev 1) [APPROVED]", "n9", (16, 185, 129)),
                ("brand_aurora (v2 • Rev 1) [APPROVED]", "n9", (16, 185, 129)),
                ("brand_lumina (v2 • Rev 0) [APPROVED]", "n9", (16, 185, 129)),
            ],
            "active_edge": ("n8", "n9"),
        },
    ]

    edges = [
        ("n1", "n2"),
        ("n2", "n3"),
        ("n3", "n4"),
        ("n4", "n5"),
        ("n5", "n6"),
        ("n6", "n7"),
        ("n7", "n2"),
        ("n6", "n8"),
        ("n8", "n9"),
    ]

    node_lookup = {n["id"]: n for n in dag_nodes}
    frames: List[Image.Image] = []

    for state in timeline_states:
        img = Image.new("RGB", (width, height), (9, 13, 24))
        draw = ImageDraw.Draw(img)

        # Header Bar
        draw.rectangle([(0, 0), (width, 86)], fill=(15, 23, 42))
        draw.line([(0, 86), (width, 86)], fill=(51, 65, 85), width=2)
        draw.text((32, 18), "Brand Building HITL Approval Example Application — Asynchronous Workflow Graph", fill=(255, 255, 255), font=font_h1)
        draw.text((32, 52), "GCP Project: wortz-project-352116 (us-central1)  •  Workflow: trend_discovery_flow  •  Zero-Compute Callback Gate", fill=(148, 163, 184), font=font_body)

        # Draw edges connecting DAG nodes
        for src_id, dst_id in edges:
            sx, sy, sw, sh = node_lookup[src_id]["rect"]
            dx, dy, dw, dh = node_lookup[dst_id]["rect"]
            p1 = (sx + sw // 2, sy + sh // 2)
            p2 = (dx + dw // 2, dy + dh // 2)
            is_active = state["active_edge"] == (src_id, dst_id)
            color = (52, 211, 153) if is_active else (51, 65, 85)
            width_px = 4 if is_active else 2
            draw.line([p1, p2], fill=color, width=width_px)

        # Draw DAG nodes
        for node in dag_nodes:
            nid = node["id"]
            rx, ry, rw, rh = node["rect"]
            n_state = state["active_nodes"].get(nid, "IDLE")

            if n_state == "WAITING":
                bg = (69, 39, 10)
                border = (245, 158, 11)
            elif n_state in ("APPROVED", "ACTIVE_GREEN"):
                bg = (6, 55, 42)
                border = (16, 185, 129)
            elif n_state == "ACTIVE_PURPLE":
                bg = (59, 23, 84)
                border = (168, 85, 247)
            elif n_state == "ACTIVE_AMBER":
                bg = (75, 45, 12)
                border = (251, 191, 36)
            elif n_state == "ACTIVE_BLUE":
                bg = (23, 43, 84)
                border = (59, 130, 246)
            elif n_state == "DONE":
                bg = (17, 28, 48)
                border = (56, 189, 248)
            else:
                bg = (15, 23, 42)
                border = (51, 65, 85)

            draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=14, fill=bg, outline=border, width=3)
            draw.text((rx + 14, ry + 10), node["tier"], fill=border, font=font_mono)
            draw.text((rx + 14, ry + 30), node["title"], fill=(255, 255, 255), font=font_h2)
            draw.text((rx + 14, ry + 54), node["sub"], fill=(203, 213, 225), font=font_body)

        # Draw floating artifact tokens on their active nodes with dynamic width so text never overflows
        node_token_offsets: Dict[str, int] = {}
        for label, target_nid, t_color in state["tokens"]:
            rx, ry, rw, _ = node_lookup[target_nid]["rect"]
            idx = node_token_offsets.get(target_nid, 0)
            node_token_offsets[target_nid] = idx + 1
            pill_text = f"● {label}"
            bbox = draw.textbbox((0, 0), pill_text, font=font_mono)
            text_w = bbox[2] - bbox[0]
            pill_w = max(210, min(rw - 16, text_w + 26))
            tx = rx + 10
            ty = ry - 29 - (idx * 29)
            draw.rounded_rectangle([(tx, ty), (tx + pill_w, ty + 25)], radius=8, fill=t_color, outline=(255, 255, 255), width=1)
            draw.text((tx + 10, ty + 5), pill_text, fill=(10, 15, 25), font=font_mono)

        # Bottom telemetry banner
        draw.rectangle([(0, height - 92), (width, height)], fill=(15, 23, 42))
        draw.line([(0, height - 92), (width, height - 92)], fill=(56, 189, 248), width=3)
        draw.text((32, height - 74), state["caption"], fill=(255, 255, 255), font=font_h1)
        draw.text((32, height - 38), state["detail"], fill=(148, 163, 184), font=font_body)

        frames.append(img)

    return frames


async def capture_browser_hitl_gif(base_url: str) -> Tuple[Path, Path]:
    """Capture live Playwright browser interaction frames of the HITL approval process and save animated GIFs."""
    from playwright.async_api import async_playwright

    hitl_frames: List[Image.Image] = []
    graph_web_frames: List[Image.Image] = []

    async with async_playwright() as p:
        exec_path = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
        browser = await p.chromium.launch(
            headless=True,
            executable_path=exec_path,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        # 1. Visit Queue Screen (`/`)
        await page.goto(f"{base_url}/", wait_until="networkidle")
        await page.wait_for_timeout(400)
        raw1 = await page.screenshot()
        img1 = Image.open(Path("/tmp/f1.png") if False else __import__("io").BytesIO(raw1))
        hitl_frames.append(
            _annotate_frame(
                img1,
                1,
                7,
                "Phase 1: Pending Approvals Queue & Live Workflow Graph (`/`) ",
                "Brand Apex & Brand Aurora are suspended at `events.await_callback` (0 CPU, $0.00 Idle Compute).",
                (59, 130, 246),
            )
        )

        # 2. Visit Full-Screen Interactive Workflow Graph (`/graph`)
        await page.goto(f"{base_url}/graph", wait_until="networkidle")
        await page.wait_for_timeout(400)
        raw_g1 = await page.screenshot()
        img_g1 = Image.open(__import__("io").BytesIO(raw_g1))
        hitl_frames.append(
            _annotate_frame(
                img_g1,
                2,
                7,
                "Phase 2: Live Asynchronous Workflow Graph Monitor (`/graph`)",
                "Visualizing artifacts across Tier 2 (Cognitive), Tier 3 (Zero-Compute Callback), and Tier 4 (AlloyDB).",
                (245, 158, 11),
            )
        )
        graph_web_frames.append(img_g1)

        # 3. Open Brand Apex Detail Review Card (`/initiatives/a1000000-0000-4000-8000-000000000001`)
        init_id = "a1000000-0000-4000-8000-000000000001"
        await page.goto(f"{base_url}/initiatives/{init_id}", wait_until="networkidle")
        await page.wait_for_timeout(400)
        raw3 = await page.screenshot()
        img3 = Image.open(__import__("io").BytesIO(raw3))
        hitl_frames.append(
            _annotate_frame(
                img3,
                3,
                7,
                "Phase 3: Asset Detail Card — Search Grounding & Memory Compliance Inspector",
                "Workflow paused at `5. await_human_approval (WAITING)`. Verified DOE & ACI citations + Memory Bank rules.",
                (245, 158, 11),
            )
        )

        # 4. Click 'Request Revision & Distill Memory' button to open revision drawer
        await page.click("#btn-open-revision-drawer")
        await page.wait_for_timeout(350)
        raw4 = await page.screenshot()
        img4 = Image.open(__import__("io").BytesIO(raw4))
        hitl_frames.append(
            _annotate_frame(
                img4,
                4,
                7,
                "Phase 4: Human-in-the-Loop Revision Request & Continuous Learning Critique",
                "Brand Director enters critique: 'Emphasize 90% cold-water energy savings and scientific enzyme clarity.'",
                (245, 158, 11),
            )
        )

        wait_ms = 1500 if "127.0.0.1" in base_url or "localhost" in base_url else 8500
        # 5. Submit Revision Request -> Wakes Callback, Distills Memory Rule, Re-runs Agent 1 (Revision #1)
        await page.click("#btn-submit-revision")
        await page.wait_for_timeout(wait_ms)
        await page.goto(f"{base_url}/initiatives/{init_id}", wait_until="networkidle")
        await page.wait_for_timeout(500)
        raw5 = await page.screenshot()
        img5 = Image.open(__import__("io").BytesIO(raw5))
        hitl_frames.append(
            _annotate_frame(
                img5,
                5,
                7,
                "Phase 5: Continuous Learning Synced & Agent 1 Re-Executed (Version 2 • Revision 1/3)",
                "Critique distilled into Agent Platform Memory Bank (`memories:generate`) & applied to `[Rev #1]` Hooks!",
                (168, 85, 247),
            )
        )

        # 6. Click 'Approve & Resume Workflow' button on Revised Brief
        await page.click("#btn-approve-initiative")
        await page.wait_for_timeout(wait_ms)
        await page.goto(f"{base_url}/initiatives/{init_id}", wait_until="networkidle")
        await page.wait_for_timeout(500)
        raw6 = await page.screenshot()
        img6 = Image.open(__import__("io").BytesIO(raw6))
        hitl_frames.append(
            _annotate_frame(
                img6,
                6,
                7,
                "Phase 6: Callback Resumed -> Status Transitioned to `APPROVED` (Step 2 Dispatched)",
                "State machine reaches `9a. trigger_downstream_step2 (DONE)` and commits immutable audit log to AlloyDB.",
                (16, 185, 129),
            )
        )

        # 7. Return to Queue & Graph to verify updated metrics and asynchronous completion
        await page.goto(f"{base_url}/", wait_until="networkidle")
        await page.wait_for_timeout(400)
        raw7 = await page.screenshot()
        img7 = Image.open(__import__("io").BytesIO(raw7))
        hitl_frames.append(
            _annotate_frame(
                img7,
                7,
                7,
                "Phase 7: Updated Queue & Asynchronous Workflow Graph (`APPROVED` Handoff Complete)",
                "Approved count incremented; contract-validated JSONB brief handed off cleanly to Step 2 Asset Pipeline.",
                (16, 185, 129),
            )
        )

        await browser.close()

    hitl_gif_path = ASSETS_DIR / "hitl_approval_workflow.gif"
    hitl_frames[0].save(
        hitl_gif_path,
        save_all=True,
        append_images=hitl_frames[1:],
        duration=[2200, 2200, 2400, 2400, 2600, 2600, 2400],
        loop=0,
        optimize=True,
    )

    dag_frames = generate_async_workflow_dag_frames()
    dag_gif_path = ASSETS_DIR / "async_workflow_graph.gif"
    dag_frames[0].save(
        dag_gif_path,
        save_all=True,
        append_images=dag_frames[1:],
        duration=1600,
        loop=0,
        optimize=True,
    )

    return hitl_gif_path, dag_gif_path


async def main() -> None:
    import uvicorn
    from services.approval_ui.app import app

    # If a live URL is passed in RECORD_TARGET_URL, record directly against it; otherwise spin up local server on 127.0.0.1:8099
    target_url = os.getenv("RECORD_TARGET_URL", "")
    server_task = None
    if not target_url:
        config = uvicorn.Config(app, host="127.0.0.1", port=8099, log_level="warning")
        server = uvicorn.Server(config)
        server_task = asyncio.create_task(server.serve())
        await asyncio.sleep(1.2)
        target_url = "http://127.0.0.1:8099"

    try:
        hitl_gif, dag_gif = await capture_browser_hitl_gif(target_url)
        print(f"Recorded HITL UI GIF: {hitl_gif} ({hitl_gif.stat().st_size // 1024} KB)")
        print(f"Recorded Async Workflow Graph GIF: {dag_gif} ({dag_gif.stat().st_size // 1024} KB)")
    finally:
        if server_task:
            server_task.cancel()
            try:
                await server_task
            except (asyncio.CancelledError, Exception):
                pass


if __name__ == "__main__":
    asyncio.run(main())
