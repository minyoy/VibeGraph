from app.services.neo4j_service import Neo4jService
from app.utils.errors import Neo4jConnectionError, NoRecommendationsError


class GraphRecommendationService:
    def __init__(self):
        self.neo4j = Neo4jService()

    async def get_recommendations(self, user_id: str, limit: int = 10) -> list[dict]:
        try:
            candidates = await self.neo4j.get_recommendations(user_id, limit)
        except Neo4jConnectionError:
            raise
        except Exception as e:
            raise Neo4jConnectionError(f"Recommendation query failed: {str(e)}")

        if not candidates:
            raise NoRecommendationsError(
                "No recommendation candidates found. Sync more playlists to improve results."
            )
        return candidates
