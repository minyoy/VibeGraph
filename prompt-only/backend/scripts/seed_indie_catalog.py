import asyncio
from pathlib import Path
import sys

import httpx
from neo4j import AsyncGraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings


ITUNES_SEARCH_URL = "https://itunes.apple.com/search"
DEFAULT_COUNTRIES = ["US", "KR", "GB", "CA", "AU"]
DEFAULT_TARGET = 300
DEFAULT_LIMIT_PER_QUERY = 200
SEARCH_TERMS = [
    "indie",
    "indie rock",
    "indie pop",
    "indie folk",
    "korean indie",
    "k-indie",
    "bedroom pop",
    "dream pop",
    "shoegaze",
    "lo-fi indie",
    "alternative indie",
    "singer songwriter indie",
    "indie electronic",
    "jangle pop",
    "garage rock revival",
    "post punk revival",
]


def parse_args() -> tuple[int, list[str]]:
    target = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TARGET
    countries = DEFAULT_COUNTRIES
    if len(sys.argv) > 2:
        countries = [part.strip().upper() for part in sys.argv[2].split(",") if part.strip()]
    return target, countries


async def search_itunes(
    client: httpx.AsyncClient,
    term: str,
    country: str,
    limit: int,
) -> list[dict]:
    response = await client.get(
        ITUNES_SEARCH_URL,
        params={
            "term": term,
            "country": country,
            "media": "music",
            "entity": "song",
            "attribute": "songTerm",
            "limit": limit,
        },
    )
    response.raise_for_status()

    tracks = []
    for item in response.json().get("results", []):
        track_id = item.get("trackId")
        title = item.get("trackName")
        artist = item.get("artistName")
        if not track_id or not title or not artist:
            continue

        artwork = item.get("artworkUrl100")
        if artwork:
            artwork = artwork.replace("100x100bb", "300x300bb")

        tracks.append(
            {
                "id": str(track_id),
                "title": title,
                "artist": artist,
                "genre": item.get("primaryGenreName") or "Indie",
                "albumArt": artwork,
                "country": country.lower(),
                "searchTerm": term,
            }
        )
    return tracks


async def collect_tracks(target: int, countries: list[str]) -> list[dict]:
    unique_tracks: dict[str, dict] = {}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for country in countries:
            for term in SEARCH_TERMS:
                tracks = await search_itunes(
                    client,
                    term,
                    country,
                    DEFAULT_LIMIT_PER_QUERY,
                )
                for track in tracks:
                    unique_tracks.setdefault(track["id"], track)
                    if len(unique_tracks) >= target:
                        return list(unique_tracks.values())
                print(
                    f"Fetched {len(tracks)} tracks for '{term}' in {country}; "
                    f"{len(unique_tracks)} unique so far."
                )
    return list(unique_tracks.values())


async def upsert_tracks(session, tracks: list[dict]) -> dict:
    result = await session.run(
        """
        UNWIND $tracks AS track
        MERGE (t:Track {id: track.id})
        ON CREATE SET
            t.title = track.title,
            t.artist = track.artist,
            t.genre = track.genre,
            t.albumArt = track.albumArt,
            t.source = 'itunes_search_indie',
            t.storefront = track.country,
            t.searchTerm = track.searchTerm,
            t.createdAt = timestamp()
        ON MATCH SET
            t.title = track.title,
            t.artist = track.artist,
            t.genre = track.genre,
            t.albumArt = coalesce(track.albumArt, t.albumArt),
            t.source = coalesce(t.source, 'itunes_search_indie'),
            t.storefront = coalesce(t.storefront, track.country),
            t.searchTerm = coalesce(t.searchTerm, track.searchTerm)
        WITH t, track
        MERGE (a:Artist {name: track.artist})
        MERGE (g:Genre {name: track.genre})
        MERGE (t)-[:BY]->(a)
        MERGE (t)-[:HAS_GENRE]->(g)
        MERGE (a)-[:HAS_GENRE]->(g)
        RETURN count(t) AS upserted
        """,
        tracks=tracks,
    )
    row = await result.single()
    summary = await result.consume()
    return {
        "upserted": row["upserted"] if row else 0,
        "nodesCreated": summary.counters.nodes_created,
        "relationshipsCreated": summary.counters.relationships_created,
    }


async def main() -> int:
    target, countries = parse_args()
    tracks = await collect_tracks(target, countries)
    if not tracks:
        print("No tracks fetched from iTunes Search API.", file=sys.stderr)
        return 1

    settings = get_settings()
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )

    async with driver:
        await driver.verify_connectivity()
        async with driver.session() as session:
            result = await upsert_tracks(session, tracks)

    print(
        f"Seeded {result['upserted']} indie catalog tracks "
        f"({result['nodesCreated']} new nodes, "
        f"{result['relationshipsCreated']} new relationships)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
