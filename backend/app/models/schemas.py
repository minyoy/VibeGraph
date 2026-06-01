from pydantic import BaseModel
from typing import Optional


class Track(BaseModel):
    id: str
    title: str
    artist: str
    genre: Optional[str] = "Unknown"
    albumArt: Optional[str] = None


class Playlist(BaseModel):
    id: str
    name: str
    trackCount: Optional[int] = 0
    artwork: Optional[str] = None


class SyncRequest(BaseModel):
    userId: str
    playlists: list[dict]


class SyncResponse(BaseModel):
    success: bool
    message: str
    nodesCreated: int
    relationshipsCreated: int


class TasteAnalysis(BaseModel):
    topArtists: list[dict]
    topGenres: list[dict]
    detectedTaste: list[str]
    moodTags: list[str]


class RecommendedTrack(BaseModel):
    id: str
    title: str
    artist: str
    genre: str
    score: float
    graphPath: str
    reason: str


class AgentExplainRequest(BaseModel):
    userId: str
    candidates: list[RecommendedTrack]
    tasteProfile: Optional[dict] = None


class AgentExplainResponse(BaseModel):
    playlistName: str
    explanation: str
    tracks: list[RecommendedTrack]


class CreatePlaylistRequest(BaseModel):
    userId: str
    playlistName: str
    trackIds: list[str]
    musicUserToken: str


class CreatePlaylistResponse(BaseModel):
    success: bool
    playlistId: Optional[str] = None
    message: str
