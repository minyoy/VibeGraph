import asyncio
from pathlib import Path
import sys

import httpx
from neo4j import AsyncGraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings


APPLE_MUSIC_BASE = "https://api.music.apple.com/v1"
DEFAULT_USER_ID = "user_default"
DEFAULT_STOREFRONT = "us"
DEFAULT_LIMIT_PER_GENRE = 12


async def get_user_genres(session, user_id: str) -> list[str]:
    result = await session.run(
        """
        MATCH (:User {id: $uid})-[:OWNS]->(:Playlist)-[:CONTAINS]->(:Track)-[:HAS_GENRE]->(g:Genre)
        RETURN g.name AS genre, count(*) AS count
        ORDER BY count DESC
        LIMIT 8
        """,
        uid=user_id,
    )
    return [row["genre"] async for row in result]


async def get_owned_track_ids(session, user_id: str) -> set[str]:
    result = await session.run(
        """
        MATCH (:User {id: $uid})-[:OWNS]->(:Playlist)-[:CONTAINS]->(t:Track)
        RETURN t.id AS id
        """,
        uid=user_id,
    )
    return {row["id"] async for row in result}


async def search_catalog_tracks(
    client: httpx.AsyncClient,
    developer_token: str,
    storefront: str,
    genre: str,
    limit: int,
) -> list[dict]:
    response = await client.get(
        f"{APPLE_MUSIC_BASE}/catalog/{storefront}/search",
        headers={"Authorization": f"Bearer {developer_token}"},
        params={"term": genre, "types": "songs", "limit": limit},
    )
    response.raise_for_status()
    songs = response.json().get("results", {}).get("songs", {}).get("data", [])

    tracks = []
    for song in songs:
        attrs = song.get("attributes", {})
        artwork = attrs.get("artwork") or {}
        artwork_url = artwork.get("url")
        if artwork_url:
            artwork_url = artwork_url.replace("{w}", "300").replace("{h}", "300")

        tracks.append(
            {
                "id": song.get("id"),
                "title": attrs.get("name", "Unknown Track"),
                "artist": attrs.get("artistName", "Unknown Artist"),
                "genre": genre,
                "albumArt": artwork_url,
            }
        )
    return [track for track in tracks if track["id"]]


async def upsert_candidate_tracks(session, tracks: list[dict]) -> int:
    inserted = 0
    for track in tracks:
        result = await session.run(
            """
            MERGE (t:Track {id: $id})
            ON CREATE SET
                t.title = $title,
                t.artist = $artist,
                t.genre = $genre,
                t.albumArt = $albumArt,
                t.source = 'apple_catalog',
                t.createdAt = timestamp()
            ON MATCH SET
                t.title = $title,
                t.artist = $artist,
                t.genre = $genre,
                t.albumArt = coalesce($albumArt, t.albumArt),
                t.source = coalesce(t.source, 'apple_catalog')
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
        inserted += summary.counters.nodes_created
    return inserted


async def main() -> int:
    user_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USER_ID
    storefront = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_STOREFRONT
    limit_per_genre = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_LIMIT_PER_GENRE

    settings = get_settings()
    if not settings.apple_music_developer_token:
        print("APPLE_MUSIC_DEVELOPER_TOKEN is not configured", file=sys.stderr)
        return 1

    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )

    async with driver:
        await driver.verify_connectivity()
        async with driver.session() as session:
            genres = await get_user_genres(session, user_id)
            if not genres:
                print(f"No synced genres found for user '{user_id}'")
                return 1

            owned_track_ids = await get_owned_track_ids(session, user_id)

            all_candidates = []
            async with httpx.AsyncClient(timeout=30) as client:
                for genre in genres:
                    tracks = await search_catalog_tracks(
                        client,
                        settings.apple_music_developer_token,
                        storefront,
                        genre,
                        limit_per_genre,
                    )
                    all_candidates.extend(
                        track for track in tracks if track["id"] not in owned_track_ids
                    )

            unique_candidates = list({track["id"]: track for track in all_candidates}.values())
            inserted = await upsert_candidate_tracks(session, unique_candidates)
            print(
                f"Seeded {len(unique_candidates)} recommendation candidates "
                f"for {len(genres)} genres ({inserted} new nodes)."
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
