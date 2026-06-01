from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.api import apple, graph, analysis, recommendations, agent
from app.utils.errors import (
    AppleMusicAuthError, AppleMusicAPIError, Neo4jConnectionError,
    NoRecommendationsError, LLMError, PlaylistCreationError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


settings = get_settings()

app = FastAPI(
    title="VibeGraph API",
    description="Graph-based personalized music recommendation system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apple.router)
app.include_router(graph.router)
app.include_router(analysis.router)
app.include_router(recommendations.router)
app.include_router(agent.router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "VibeGraph API"}


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )
