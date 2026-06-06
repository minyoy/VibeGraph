from fastapi import APIRouter
from app.models.schemas import AgentExplainRequest, AgentExplainResponse
from app.services import agent_service

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/explain", response_model=AgentExplainResponse)
async def explain(req: AgentExplainRequest):
    return await agent_service.generate_explanation(
        [c.model_dump() for c in req.candidates],
        req.tasteProfile.model_dump(),
    )
