"""FastAPI Application for Component B: Data Access Service (System of Record API)."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from fastapi import FastAPI

from database.db_client import db_client
from services.data_service.routes.callbacks import router as callbacks_router
from services.data_service.routes.initiatives import router as initiatives_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await db_client.initialize()
    yield


app = FastAPI(
    title="Brand Building HITL Approval Example Application - Data Access Service (Component B)",
    version="1.0.0",
    description="System of Record API interfacing Cloud Workflows & Approval UI with AlloyDB/PostgreSQL & Firestore",
    lifespan=lifespan,
)

app.include_router(initiatives_router)
app.include_router(callbacks_router)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {
        "status": "healthy",
        "service": "data-service",
        "database": os.getenv("ALLOYDB_DATABASE", "brand_hitl_db"),
        "project_id": os.getenv("PROJECT_ID", "wortz-project-352116"),
    }
