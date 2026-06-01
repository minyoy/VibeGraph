from fastapi import APIRouter
from app.services.analysis_service import AnalysisService
from app.models.schemas import TasteAnalysis

router = APIRouter(prefix="/analysis", tags=["Analysis"])
service = AnalysisService()


@router.get("/{user_id}", response_model=TasteAnalysis)
async def get_taste_analysis(user_id: str):
    result = await service.get_taste_analysis(user_id)
    return TasteAnalysis(**result)
