from fastapi import APIRouter
from app.models.schemas import AnalysisResponse
from app.services import analysis_service

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/{user_id}", response_model=AnalysisResponse)
async def get_analysis(user_id: str):
    return await analysis_service.get_analysis(user_id)
