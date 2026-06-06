from fastapi import APIRouter, Query
from typing import List
from app.models.schemas import RecommendedTrack
from app.services import graph_recommendation_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{user_id}", response_model=List[RecommendedTrack])
async def get_recommendations(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50),
):
    return await graph_recommendation_service.get_recommendations(user_id, limit)
