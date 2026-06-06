from app.services.neo4j_service import Neo4jService
from app.utils.errors import Neo4jConnectionError


class AnalysisService:
    def __init__(self):
        self.neo4j = Neo4jService()

    async def get_taste_analysis(self, user_id: str) -> dict:
        try:
            return await self.neo4j.get_taste_analysis(user_id)
        except Neo4jConnectionError:
            raise
        except Exception as e:
            raise Neo4jConnectionError(f"Analysis failed: {str(e)}")
