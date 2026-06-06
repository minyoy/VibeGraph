from pydantic import BaseModel
from typing import Optional, List


class PlaylistItem(BaseModel):
    id: str
    name: str
    trackCount: int = 0
    artwork: Optional[str] = None


class TrackItem(BaseModel):
    id: str
    title: str
    artist: str
    genre: str
    albumArt: Optional[str] = None


class PlaylistsResponse(BaseModel):
    data: List[PlaylistItem]


class TracksResponse(BaseModel):
    data: List[TrackItem]


class SyncRequest(BaseModel):
    userId: str
    playlists: List[PlaylistItem]


class SyncResponse(BaseModel):
    success: bool
    message: str
    nodesCreated: int
    relationshipsCreated: int


class ArtistCount(BaseModel):
    name: str
    count: int


class GenreCount(BaseModel):
    name: str
    count: int


class AnalysisResponse(BaseModel):
    topArtists: List[ArtistCount]
    topGenres: List[GenreCount]
    detectedTaste: List[str]
    moodTags: List[str]


class RecommendedTrack(BaseModel):
    id: str
    title: str
    artist: str
    genre: str
    score: float
    graphPath: str
    reason: str = ""


class AgentExplainRequest(BaseModel):
    userId: str
    candidates: List[RecommendedTrack]
    tasteProfile: AnalysisResponse


class AgentExplainResponse(BaseModel):
    playlistName: str
    explanation: str
    tracks: List[RecommendedTrack]


class CreatePlaylistRequest(BaseModel):
    userId: str
    playlistName: str
    trackIds: List[str]
    musicUserToken: str


class CreatePlaylistResponse(BaseModel):
    success: bool
    playlistId: str
    message: str
