from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from app.models.schemas import SyncRequest, SyncResponse
from app.services import apple_music_service, neo4j_service
from app.utils.errors import AppleMusicAuthError

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/sync", response_model=SyncResponse)
async def sync_graph(
    req: SyncRequest,
    music_user_token: Optional[str] = Header(None, alias="Music-User-Token"),
):
    if not music_user_token:
        raise AppleMusicAuthError("Music-User-Token header is required")
    if not req.playlists:
        raise HTTPException(status_code=422, detail="At least one playlist must be selected")

    playlists_with_tracks = []
    for pl in req.playlists:
        tracks = await apple_music_service.get_tracks(pl.id, music_user_token)
        playlists_with_tracks.append({
            "id": pl.id,
            "name": pl.name,
            "tracks": tracks,
        })

    result = await neo4j_service.sync_playlists(req.userId, playlists_with_tracks)
    return {
        "success": True,
        "message": f"Synced {len(req.playlists)} playlist(s) to graph",
        "nodesCreated": result["nodesCreated"],
        "relationshipsCreated": result["relationshipsCreated"],
    }
