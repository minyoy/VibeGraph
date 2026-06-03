import asyncio
import httpx
from typing import Optional
from app.core.config import get_settings
from app.utils.errors import AppleMusicAuthError, AppleMusicAPIError

APPLE_MUSIC_BASE = "https://api.music.apple.com/v1"
APPLE_MUSIC_MAX_COUNT_REQUESTS = 3
APPLE_MUSIC_MAX_RETRIES = 3


class AppleMusicService:
    def __init__(self):
        self.settings = get_settings()

    def _headers(self, music_user_token: Optional[str] = None) -> dict:
        token = self.settings.apple_music_developer_token
        if not token:
            raise AppleMusicAuthError("Apple Music developer token not configured")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if music_user_token:
            headers["Music-User-Token"] = music_user_token
        return headers

    async def get_user_playlists(self, music_user_token: str) -> list[dict]:
        if not music_user_token:
            raise AppleMusicAuthError("Music user token is required")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{APPLE_MUSIC_BASE}/me/library/playlists",
                    headers=self._headers(music_user_token),
                    params={"limit": 25},
                )
                if resp.status_code == 401:
                    raise AppleMusicAuthError("Invalid or expired music user token")
                if resp.status_code != 200:
                    raise AppleMusicAPIError(f"Apple Music API error: {resp.status_code}")
                data = resp.json()
                playlists = self._parse_playlists(data.get("data", []))
                await self._fill_missing_track_counts(client, playlists, music_user_token)
                return playlists
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            raise AppleMusicAPIError(f"Failed to connect to Apple Music: {str(e)}")

    def _parse_playlists(self, raw: list) -> list[dict]:
        playlists = []
        for item in raw:
            attrs = item.get("attributes", {})
            relationships = item.get("relationships", {})
            tracks_relationship = relationships.get("tracks", {})
            artwork = attrs.get("artwork", {})
            art_url = None
            if artwork:
                w, h = artwork.get("width", 300), artwork.get("height", 300)
                art_url = artwork.get("url", "").replace("{w}", str(w)).replace("{h}", str(h))
            playlists.append({
                "id": item.get("id", ""),
                "name": attrs.get("name", "Unknown Playlist"),
                "trackCount": self._extract_track_count(attrs, tracks_relationship),
                "artwork": art_url,
            })
        return playlists

    def _extract_track_count(self, attrs: dict, tracks_relationship: dict) -> Optional[int]:
        for key in ("trackCount", "trackcount", "track_count"):
            value = attrs.get(key)
            if isinstance(value, int):
                return value

        meta = tracks_relationship.get("meta", {})
        total = meta.get("total")
        if isinstance(total, int):
            return total

        data = tracks_relationship.get("data")
        if isinstance(data, list):
            return len(data)

        return None

    async def _fill_missing_track_counts(
        self,
        client: httpx.AsyncClient,
        playlists: list[dict],
        music_user_token: str,
    ) -> None:
        missing = [playlist for playlist in playlists if playlist.get("trackCount") is None]
        if not missing:
            return

        semaphore = asyncio.Semaphore(APPLE_MUSIC_MAX_COUNT_REQUESTS)
        counts = await asyncio.gather(
            *[
                self._fetch_playlist_track_count(
                    client,
                    playlist["id"],
                    music_user_token,
                    semaphore,
                )
                for playlist in missing
            ],
            return_exceptions=True,
        )
        for playlist, count in zip(missing, counts):
            playlist["trackCount"] = None if isinstance(count, Exception) else count

    async def _fetch_playlist_track_count(
        self,
        client: httpx.AsyncClient,
        playlist_id: str,
        music_user_token: str,
        semaphore: asyncio.Semaphore,
    ) -> int:
        total = 0
        next_url = f"{APPLE_MUSIC_BASE}/me/library/playlists/{playlist_id}/tracks"
        params = {"limit": 100}

        while next_url:
            resp = await self._get_with_retries(
                client,
                next_url,
                music_user_token,
                params,
                semaphore,
            )
            if resp.status_code == 401:
                raise AppleMusicAuthError("Invalid or expired music user token")
            if resp.status_code != 200:
                raise AppleMusicAPIError(f"Apple Music API error: {resp.status_code}")

            data = resp.json()
            total += len(data.get("data", []))
            next_path = data.get("next")
            next_url = f"{APPLE_MUSIC_BASE}{next_path}" if next_path else None
            params = None

        return total

    async def _get_with_retries(
        self,
        client: httpx.AsyncClient,
        url: str,
        music_user_token: str,
        params: Optional[dict],
        semaphore: asyncio.Semaphore,
    ) -> httpx.Response:
        for attempt in range(APPLE_MUSIC_MAX_RETRIES + 1):
            async with semaphore:
                resp = await client.get(
                    url,
                    headers=self._headers(music_user_token),
                    params=params,
                )

            if resp.status_code != 429 or attempt == APPLE_MUSIC_MAX_RETRIES:
                return resp

            retry_after = resp.headers.get("Retry-After")
            delay = int(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
            await asyncio.sleep(delay)

        return resp

    async def get_playlist_tracks(self, playlist_id: str, music_user_token: str) -> list[dict]:
        if not music_user_token:
            raise AppleMusicAuthError("Music user token is required")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{APPLE_MUSIC_BASE}/me/library/playlists/{playlist_id}/tracks",
                    headers=self._headers(music_user_token),
                    params={"limit": 100},
                )
                if resp.status_code == 401:
                    raise AppleMusicAuthError("Invalid or expired music user token")
                if resp.status_code != 200:
                    raise AppleMusicAPIError(f"Apple Music API error: {resp.status_code}")
                data = resp.json()
                return self._parse_tracks(data.get("data", []))
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            raise AppleMusicAPIError(f"Failed to connect to Apple Music: {str(e)}")

    def _parse_tracks(self, raw: list) -> list[dict]:
        tracks = []
        for item in raw:
            attrs = item.get("attributes", {})
            artwork = attrs.get("artwork", {})
            art_url = None
            if artwork:
                w, h = artwork.get("width", 300), artwork.get("height", 300)
                art_url = artwork.get("url", "").replace("{w}", "300").replace("{h}", "300")
            genre_names = attrs.get("genreNames", [])
            tracks.append({
                "id": item.get("id", ""),
                "title": attrs.get("name", "Unknown Track"),
                "artist": attrs.get("artistName", "Unknown Artist"),
                "genre": genre_names[0] if genre_names else "Unknown",
                "albumArt": art_url,
            })
        return tracks

    async def create_playlist(
        self, playlist_name: str, track_ids: list[str], music_user_token: str
    ) -> dict:
        if not music_user_token:
            raise AppleMusicAuthError("Music user token is required")
        tracks_payload = [
            {"id": tid, "type": "library-songs"} for tid in track_ids
        ]
        body = {
            "attributes": {"name": playlist_name, "description": "Created by VibeGraph"},
            "relationships": {"tracks": {"data": tracks_payload}},
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{APPLE_MUSIC_BASE}/me/library/playlists",
                    headers=self._headers(music_user_token),
                    json=body,
                )
                if resp.status_code == 401:
                    raise AppleMusicAuthError("Invalid or expired music user token")
                if resp.status_code not in (200, 201):
                    raise AppleMusicAPIError(f"Failed to create playlist: {resp.status_code} {resp.text}")
                data = resp.json()
                created = data.get("data", [{}])[0]
                return {"playlistId": created.get("id"), "name": playlist_name}
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            raise AppleMusicAPIError(f"Failed to connect to Apple Music: {str(e)}")
