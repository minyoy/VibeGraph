from fastapi import APIRouter
from app.services.agent_service import AgentService
from app.models.schemas import AgentExplainRequest, AgentExplainResponse, RecommendedTrack

router = APIRouter(prefix="/agent", tags=["Agent"])
service = AgentService()


@router.post("/explain", response_model=AgentExplainResponse)
async def explain_recommendations(body: AgentExplainRequest):
    candidates = [c.model_dump() for c in body.candidates]
    result = await service.explain_recommendations(candidates, body.tasteProfile)
    return AgentExplainResponse(
        playlistName=result["playlistName"],
        explanation=result["explanation"],
        tracks=[RecommendedTrack(**t) for t in result["tracks"]],
    )
