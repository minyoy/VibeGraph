from fastapi import APIRouter, Header
from typing import Optional
from app.services.apple_music_service import AppleMusicService
from app.models.schemas import CreatePlaylistRequest, CreatePlaylistResponse
from app.utils.errors import AppleMusicAuthError

router = APIRouter(prefix="/apple", tags=["Apple Music"])
service = AppleMusicService()


@router.get("/playlists")
async def get_playlists(music_user_token: Optional[str] = Header(None, alias="Music-User-Token")):
    if not music_user_token:
        raise AppleMusicAuthError("Music-User-Token header is required")
    playlists = await service.get_user_playlists(music_user_token)
    return {"data": playlists}


@router.get("/playlists/{playlist_id}/tracks")
async def get_playlist_tracks(
    playlist_id: str,
    music_user_token: Optional[str] = Header(None, alias="Music-User-Token"),
):
    if not music_user_token:
        raise AppleMusicAuthError("Music-User-Token header is required")
    tracks = await service.get_playlist_tracks(playlist_id, music_user_token)
    return {"data": tracks}


@router.post("/playlists/create", response_model=CreatePlaylistResponse)
async def create_playlist(body: CreatePlaylistRequest):
    result = await service.create_playlist(
        body.playlistName, body.trackIds, body.musicUserToken
    )
    return CreatePlaylistResponse(
        success=True,
        playlistId=result.get("playlistId"),
        message=f"Playlist '{result['name']}' created successfully",
    )
