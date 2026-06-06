from fastapi import APIRouter, Header
from typing import Optional
from app.services.neo4j_service import Neo4jService
from app.services.apple_music_service import AppleMusicService
from app.models.schemas import SyncRequest, SyncResponse
from app.utils.errors import AppleMusicAuthError

router = APIRouter(prefix="/graph", tags=["Graph"])
neo4j_service = Neo4jService()
apple_service = AppleMusicService()


@router.post("/sync", response_model=SyncResponse)
async def sync_graph(
    body: SyncRequest,
    music_user_token: Optional[str] = Header(None, alias="Music-User-Token"),
):
    if not music_user_token:
        raise AppleMusicAuthError("Music-User-Token header is required")

    playlists_with_tracks = []
    for pl in body.playlists:
        tracks = await apple_service.get_playlist_tracks(pl["id"], music_user_token)
        playlists_with_tracks.append({
            "id": pl["id"],
            "name": pl["name"],
            "tracks": tracks,
        })

    result = await neo4j_service.sync_graph(body.userId, playlists_with_tracks)

    return SyncResponse(
        success=True,
        message=f"Synced {len(playlists_with_tracks)} playlists to graph",
        nodesCreated=result["nodesCreated"],
        relationshipsCreated=result["relationshipsCreated"],
    )
