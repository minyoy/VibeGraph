from fastapi import APIRouter, Query
from app.services.graph_recommendation_service import GraphRecommendationService
from app.models.schemas import RecommendedTrack

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
service = GraphRecommendationService()


@router.get("/{user_id}", response_model=list[RecommendedTrack])
async def get_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
):
    candidates = await service.get_recommendations(user_id, limit)
    return [RecommendedTrack(**c) for c in candidates]
