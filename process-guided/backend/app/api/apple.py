from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from app.services import apple_music_service
from app.models.schemas import (
    PlaylistsResponse, TracksResponse,
    CreatePlaylistRequest, CreatePlaylistResponse,
)
from app.utils.errors import AppleMusicAuthError

router = APIRouter(prefix="/apple", tags=["apple"])


@router.get("/playlists", response_model=PlaylistsResponse)
async def get_playlists(
    music_user_token: Optional[str] = Header(None, alias="Music-User-Token"),
):
    if not music_user_token:
        raise AppleMusicAuthError("Music-User-Token header is required")
    data = await apple_music_service.get_playlists(music_user_token)
    return {"data": data}


@router.get("/playlists/{playlist_id}/tracks", response_model=TracksResponse)
async def get_tracks(
    playlist_id: str,
    music_user_token: Optional[str] = Header(None, alias="Music-User-Token"),
):
    if not music_user_token:
        raise AppleMusicAuthError("Music-User-Token header is required")
    data = await apple_music_service.get_tracks(playlist_id, music_user_token)
    return {"data": data}


@router.post("/playlists/create", response_model=CreatePlaylistResponse)
async def create_playlist(req: CreatePlaylistRequest):
    if not req.trackIds:
        raise HTTPException(status_code=422, detail="trackIds must not be empty")
    playlist_id = await apple_music_service.create_playlist(
        req.playlistName, req.trackIds, req.musicUserToken
    )
    return {
        "success": True,
        "playlistId": playlist_id,
        "message": f"Playlist '{req.playlistName}' created successfully",
    }
