from app.services.neo4j_service import get_recommendation_candidates
from app.utils.errors import NoRecommendationsError


async def get_recommendations(user_id: str, limit: int) -> list:
    candidates = await get_recommendation_candidates(user_id, limit)
    if not candidates:
        raise NoRecommendationsError()
    return candidates
