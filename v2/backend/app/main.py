from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import apple, graph, analysis, recommendations, agent
from app.services.neo4j_service import close_driver

app = FastAPI(title="VibeGraph API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apple.router)
app.include_router(graph.router)
app.include_router(analysis.router)
app.include_router(recommendations.router)
app.include_router(agent.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "VibeGraph API"}


@app.on_event("shutdown")
async def shutdown():
    await close_driver()
