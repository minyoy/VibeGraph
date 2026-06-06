import asyncio
from pathlib import Path
import sys

import httpx
from neo4j import AsyncGraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings


APPLE_MUSIC_BASE = "https://api.music.apple.com/v1"
DEFAULT_STOREFRONTS = ["kr", "us"]
DEFAULT_LIMIT = 100


def parse_args() -> tuple[list[str], int]:
    storefronts = DEFAULT_STOREFRONTS
    limit = DEFAULT_LIMIT

    if len(sys.argv) > 1:
        storefronts = [part.strip().lower() for part in sys.argv[1].split(",") if part.strip()]
    if len(sys.argv) > 2:
        limit = int(sys.argv[2])

    return storefronts, limit


async def fetch_top_songs(
    client: httpx.AsyncClient,
    developer_token: str,
    storefront: str,
    limit: int,
) -> list[dict]:
    response = await client.get(
        f"{APPLE_MUSIC_BASE}/catalog/{storefront}/charts",
        headers={"Authorization": f"Bearer {developer_token}"},
        params={"types": "songs", "limit": limit},
    )
    response.raise_for_status()

    charts = response.json().get("results", {}).get("songs", [])
    songs = charts[0].get("data", []) if charts else []

    tracks = []
    for song in songs:
        attrs = song.get("attributes", {})
        artwork = attrs.get("artwork") or {}
        artwork_url = artwork.get("url")
        if artwork_url:
            artwork_url = artwork_url.replace("{w}", "300").replace("{h}", "300")

        genre_names = attrs.get("genreNames") or []
        tracks.append(
            {
                "id": song.get("id"),
                "title": attrs.get("name", "Unknown Track"),
                "artist": attrs.get("artistName", "Unknown Artist"),
                "genre": genre_names[0] if genre_names else "Unknown",
                "albumArt": artwork_url,
                "storefront": storefront,
            }
        )

    return [track for track in tracks if track["id"]]


async def upsert_tracks(session, tracks: list[dict]) -> int:
    created_tracks = 0
    for track in tracks:
        result = await session.run(
            """
            MERGE (t:Track {id: $id})
            ON CREATE SET
                t.title = $title,
                t.artist = $artist,
                t.genre = $genre,
                t.albumArt = $albumArt,
                t.source = 'apple_chart',
                t.storefront = $storefront,
                t.createdAt = timestamp()
            ON MATCH SET
                t.title = $title,
                t.artist = $artist,
                t.genre = $genre,
                t.albumArt = coalesce($albumArt, t.albumArt),
                t.source = coalesce(t.source, 'apple_chart'),
                t.storefront = coalesce(t.storefront, $storefront)
            WITH t
            MERGE (a:Artist {name: $artist})
            MERGE (g:Genre {name: $genre})
            MERGE (t)-[:BY]->(a)
            MERGE (t)-[:HAS_GENRE]->(g)
            MERGE (a)-[:HAS_GENRE]->(g)
            RETURN t
            """,
            **track,
        )
        summary = await result.consume()
        created_tracks += summary.counters.nodes_created
    return created_tracks


async def main() -> int:
    storefronts, limit = parse_args()
    settings = get_settings()
    if not settings.apple_music_developer_token:
        print("APPLE_MUSIC_DEVELOPER_TOKEN is not configured", file=sys.stderr)
        return 1

    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )

    all_tracks = []
    async with httpx.AsyncClient(timeout=30) as client:
        for storefront in storefronts:
            tracks = await fetch_top_songs(
                client,
                settings.apple_music_developer_token,
                storefront,
                limit,
            )
            print(f"Fetched {len(tracks)} top songs from {storefront}.")
            all_tracks.extend(tracks)

    unique_tracks = list({track["id"]: track for track in all_tracks}.values())

    async with driver:
        await driver.verify_connectivity()
        async with driver.session() as session:
            created_tracks = await upsert_tracks(session, unique_tracks)

    print(
        f"Seeded {len(unique_tracks)} unique chart songs "
        f"from {', '.join(storefronts)} ({created_tracks} new nodes)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
