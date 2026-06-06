from fastapi import HTTPException


class AppleMusicAuthError(HTTPException):
    def __init__(self, detail: str = "Apple Music authentication failed. Please reconnect."):
        super().__init__(status_code=401, detail=detail)


class AppleMusicAPIError(HTTPException):
    def __init__(self, detail: str = "Apple Music API error"):
        super().__init__(status_code=502, detail=detail)


class Neo4jConnectionError(HTTPException):
    def __init__(self, detail: str = "Graph database connection failed"):
        super().__init__(status_code=503, detail=detail)


class NoRecommendationsError(HTTPException):
    def __init__(self, detail: str = "No recommendation candidates found. Please sync more playlists to build your music graph."):
        super().__init__(status_code=404, detail=detail)


class LLMError(HTTPException):
    def __init__(self, detail: str = "AI explanation generation failed"):
        super().__init__(status_code=502, detail=detail)
