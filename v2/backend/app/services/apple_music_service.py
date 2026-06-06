import asyncio
import httpx
from app.core.config import settings
from app.utils.errors import AppleMusicAuthError, AppleMusicAPIError

APPLE_MUSIC_BASE = "https://api.music.apple.com/v1"
_MAX_CONCURRENT = 3


def _headers(music_user_token: str) -> dict:
    return {
        "Authorization": f"Bearer {settings.apple_music_developer_token}",
        "Music-User-Token": music_user_token,
    }


def _extract_artwork(attrs: dict) -> str | None:
    artwork = attrs.get("artwork")
    if not artwork:
        return None
    url = artwork.get("url", "")
    w = str(artwork.get("width", 300))
    h = str(artwork.get("height", 300))
    return url.replace("{w}", w).replace("{h}", h)


def _extract_track_count(attrs: dict, relationships: dict) -> int | None:
    for key in ("trackCount", "trackcount", "track_count"):
        val = attrs.get(key)
        if isinstance(val, int):
            return val

    meta = relationships.get("tracks", {}).get("meta", {})
    if isinstance(meta.get("total"), int):
        return meta["total"]

    data = relationships.get("tracks", {}).get("data")
    if isinstance(data, list):
        return len(data)

    return None


async def _fetch_track_count(
    client: httpx.AsyncClient,
    playlist_id: str,
    music_user_token: str,
    semaphore: asyncio.Semaphore,
) -> int:
    total = 0
    next_url: str | None = f"{APPLE_MUSIC_BASE}/me/library/playlists/{playlist_id}/tracks"
    params: dict | None = {"limit": 100}

    while next_url:
        async with semaphore:
            resp = await client.get(next_url, headers=_headers(music_user_token), params=params)
        if resp.status_code != 200:
            break
        body = resp.json()
        total += len(body.get("data", []))
        next_path = body.get("next")
        next_url = f"{APPLE_MUSIC_BASE}{next_path}" if next_path else None
        params = None

    return total


async def get_playlists(music_user_token: str) -> list:
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(
                f"{APPLE_MUSIC_BASE}/me/library/playlists",
                headers=_headers(music_user_token),
                params={"limit": 100},
            )
        except httpx.RequestError as e:
            raise AppleMusicAPIError(f"Network error: {e}")

    if resp.status_code == 401:
        raise AppleMusicAuthError("Invalid or expired Music-User-Token. Please reconnect to Apple Music.")
    if resp.status_code != 200:
        raise AppleMusicAPIError(f"Apple Music returned {resp.status_code}: {resp.text}")

    result = []
    for item in resp.json().get("data", []):
        attrs = item.get("attributes", {})
        result.append({
            "id": item["id"],
            "name": attrs.get("name", "Unknown Playlist"),
            "trackCount": _extract_track_count(attrs, item.get("relationships", {})),
            "artwork": _extract_artwork(attrs),
        })

    # trackCount를 API에서 못 받은 플레이리스트는 트랙 엔드포인트로 직접 카운트
    missing = [pl for pl in result if pl["trackCount"] is None]
    if missing:
        semaphore = asyncio.Semaphore(_MAX_CONCURRENT)
        async with httpx.AsyncClient(timeout=30) as client:
            counts = await asyncio.gather(
                *[
                    _fetch_track_count(client, pl["id"], music_user_token, semaphore)
                    for pl in missing
                ],
                return_exceptions=True,
            )
        for pl, count in zip(missing, counts):
            pl["trackCount"] = 0 if isinstance(count, Exception) else count

    return result


async def get_tracks(playlist_id: str, music_user_token: str) -> list:
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(
                f"{APPLE_MUSIC_BASE}/me/library/playlists/{playlist_id}/tracks",
                headers=_headers(music_user_token),
                params={"limit": 100},
            )
        except httpx.RequestError as e:
            raise AppleMusicAPIError(f"Network error: {e}")

    if resp.status_code == 401:
        raise AppleMusicAuthError("Invalid or expired Music-User-Token. Please reconnect to Apple Music.")
    if resp.status_code != 200:
        raise AppleMusicAPIError(f"Apple Music returned {resp.status_code}: {resp.text}")

    result = []
    for item in resp.json().get("data", []):
        attrs = item.get("attributes", {})
        genres = attrs.get("genreNames", [])
        genre = genres[0] if genres else "Unknown"
        artwork = None
        if attrs.get("artwork"):
            url = attrs["artwork"].get("url", "")
            artwork = url.replace("{w}", "300").replace("{h}", "300")
        result.append({
            "id": item["id"],
            "title": attrs.get("name", ""),
            "artist": attrs.get("artistName", ""),
            "genre": genre,
            "albumArt": artwork,
        })
    return result


async def create_playlist(playlist_name: str, track_ids: list, music_user_token: str) -> str:
    body = {
        "attributes": {"name": playlist_name},
        "relationships": {
            "tracks": {
                "data": [{"id": tid, "type": "library-songs"} for tid in track_ids]
            }
        },
    }
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(
                f"{APPLE_MUSIC_BASE}/me/library/playlists",
                headers={**_headers(music_user_token), "Content-Type": "application/json"},
                json=body,
            )
        except httpx.RequestError as e:
            raise AppleMusicAPIError(f"Network error: {e}")

    if resp.status_code == 401:
        raise AppleMusicAuthError("Invalid or expired Music-User-Token. Please reconnect to Apple Music.")
    if resp.status_code not in (200, 201):
        raise AppleMusicAPIError(f"Playlist creation failed: {resp.status_code} {resp.text}")

    created = resp.json().get("data", [{}])
    return created[0].get("id", "unknown") if created else "unknown"
