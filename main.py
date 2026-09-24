"""CLI Quickstart Launcher for the Brand Building HITL Approval Example Application Autonomous Trend-to-Asset HITL Pipeline."""

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))
    print(f"Starting Brand Building HITL Approval Example Application HITL Dashboard & Workflow Graph on http://{host}:{port}")
    uvicorn.run("services.approval_ui.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
