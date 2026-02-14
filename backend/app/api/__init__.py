"""FastAPI API routes."""

from fastapi import APIRouter

from app.api.narratives import router as narratives_router
from app.api.ideas import router as ideas_router
from app.api.hackathons import router as hackathons_router
from app.api.stats import router as stats_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(narratives_router)
api_router.include_router(ideas_router)
api_router.include_router(hackathons_router)
api_router.include_router(stats_router)
