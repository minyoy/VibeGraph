from fastapi import HTTPException


class AppleMusicAuthError(HTTPException):
    def __init__(self, detail: str = "Apple Music authentication failed"):
        super().__init__(status_code=401, detail=detail)


class AppleMusicAPIError(HTTPException):
    def __init__(self, detail: str = "Apple Music API request failed"):
        super().__init__(status_code=502, detail=detail)


class Neo4jConnectionError(HTTPException):
    def __init__(self, detail: str = "Neo4j connection failed"):
        super().__init__(status_code=503, detail=detail)


class NoRecommendationsError(HTTPException):
    def __init__(self, detail: str = "No recommendations available. Try syncing more playlists."):
        super().__init__(status_code=404, detail=detail)


class LLMError(HTTPException):
    def __init__(self, detail: str = "LLM API call failed"):
        super().__init__(status_code=502, detail=detail)


class PlaylistCreationError(HTTPException):
    def __init__(self, detail: str = "Failed to create playlist on Apple Music"):
        super().__init__(status_code=502, detail=detail)
