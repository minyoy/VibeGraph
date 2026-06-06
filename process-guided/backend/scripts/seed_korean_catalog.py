"""
Apple Music Catalog Charts API로 한국(kr) 스토어프론트의 인기 트랙을 가져와
Neo4j에 시드 데이터로 주입하는 스크립트.

- Developer Token만 필요 (Music-User-Token 불필요)
- 장르별 차트를 병렬로 가져와 중복 제거 후 삽입
- user_default 소유가 아닌 카탈로그 트랙으로 추천 후보로 활용됨

실행: python -m scripts.seed_korean_catalog
(v2/backend 디렉토리에서 실행)
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from neo4j import AsyncGraphDatabase
from app.core.config import settings

STOREFRONT = "kr"
APPLE_MUSIC_BASE = "https://api.music.apple.com/v1"

# Apple Music 한국 스토어 장르 ID
# https://affiliate.itunes.apple.com/resources/documentation/genre-mapping/
GENRE_IDS = {
    "K-Pop":    "51",   # K-Pop
    "Hip-Hop":  "18",   # Hip-Hop/Rap
    "R&B":      "15",   # R&B/Soul
    "Indie":    "53",   # Singer/Songwriter (Indie 포함)
    "Pop":      "14",   # Pop
    "Electronic": "7",  # Electronic
    "Rock":     "21",   # Rock
    "Ballad":   "6",    # Country (Korean ballad는 Pop에 포함되는 경우 많음)
}

# 한국 록 아티스트 검색어 — 차트 API는 글로벌 록이 섞이므로 검색으로 보완
KOREAN_ROCK_ARTISTS = [
    "넬", "버스커버스커", "국카스텐", "혁오", "10cm",
    "데이식스", "FT아일랜드", "씨엔블루", "The Rose",
    "잔나비", "실리카겔", "새소년", "적재", "루시",
    "브로큰발렌타인", "검정치마", "위아더나잇", "카더가든",
]


def _dev_headers() -> dict:
    return {"Authorization": f"Bearer {settings.apple_music_developer_token}"}


async def fetch_chart(client: httpx.AsyncClient, genre_name: str, genre_id: str) -> list[dict]:
    """특정 장르의 top 100 차트를 가져온다."""
    try:
        resp = await client.get(
            f"{APPLE_MUSIC_BASE}/catalog/{STOREFRONT}/charts",
            headers=_dev_headers(),
            params={
                "types": "songs",
                "limit": 100,
                "genre": genre_id,
            },
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"  ⚠ {genre_name} 차트 실패: {resp.status_code}")
            return []

        songs = resp.json().get("results", {}).get("songs", [])
        if not songs:
            return []

        tracks = []
        for item in songs[0].get("data", []):
            attrs = item.get("attributes", {})
            genres = attrs.get("genreNames", [])
            genre = genres[0] if genres else genre_name
            artwork = None
            aw = attrs.get("artwork", {})
            if aw.get("url"):
                artwork = aw["url"].replace("{w}", "300").replace("{h}", "300")
            tracks.append({
                "id": item["id"],
                "title": attrs.get("name", ""),
                "artist": attrs.get("artistName", ""),
                "genre": genre,
                "albumArt": artwork or "",
            })

        print(f"  ✓ {genre_name}: {len(tracks)}곡")
        return tracks

    except Exception as e:
        print(f"  ✗ {genre_name} 차트 오류: {e}")
        return []


async def fetch_korean_rock(client: httpx.AsyncClient) -> list[dict]:
    """한국 록 아티스트를 검색 API로 조회해 상위 트랙을 반환한다."""
    tracks = []
    for artist in KOREAN_ROCK_ARTISTS:
        try:
            resp = await client.get(
                f"{APPLE_MUSIC_BASE}/catalog/{STOREFRONT}/search",
                headers=_dev_headers(),
                params={"term": artist, "types": "songs", "limit": 10},
                timeout=30,
            )
            if resp.status_code != 200:
                continue
            songs = resp.json().get("results", {}).get("songs", {}).get("data", [])
            for item in songs:
                attrs = item.get("attributes", {})
                genres = attrs.get("genreNames", [])
                artwork = None
                aw = attrs.get("artwork", {})
                if aw.get("url"):
                    artwork = aw["url"].replace("{w}", "300").replace("{h}", "300")
                tracks.append({
                    "id": item["id"],
                    "title": attrs.get("name", ""),
                    "artist": attrs.get("artistName", ""),
                    "genre": "Korean Rock",
                    "albumArt": artwork or "",
                })
        except Exception as e:
            print(f"  ⚠ {artist} 검색 오류: {e}")

    print(f"  ✓ Korean Rock (검색): {len(tracks)}곡")
    return tracks


async def fetch_all_charts() -> list[dict]:
    """모든 장르 차트 + 한국 록 검색을 병렬로 가져온 뒤 중복 제거."""
    async with httpx.AsyncClient() as client:
        chart_results = await asyncio.gather(*[
            fetch_chart(client, genre_name, genre_id)
            for genre_name, genre_id in GENRE_IDS.items()
        ])
        korean_rock = await fetch_korean_rock(client)

    seen_ids: set[str] = set()
    unique_tracks: list[dict] = []
    for tracks in [*chart_results, korean_rock]:
        for t in tracks:
            if t["id"] not in seen_ids:
                seen_ids.add(t["id"])
                unique_tracks.append(t)

    return unique_tracks


async def insert_tracks(driver, tracks: list[dict]):
    """트랙 목록을 Neo4j에 MERGE로 삽입."""
    async with driver.session() as session:
        for t in tracks:
            await session.run(
                """
                MERGE (tr:Track {id: $id})
                ON CREATE SET tr.title = $title, tr.artist = $artist,
                              tr.genre = $genre,  tr.albumArt = $albumArt
                ON MATCH SET  tr.title = $title, tr.artist = $artist,
                              tr.genre = $genre,  tr.albumArt = $albumArt
                """,
                id=t["id"], title=t["title"], artist=t["artist"],
                genre=t["genre"], albumArt=t["albumArt"],
            )
            await session.run("MERGE (a:Artist {name: $name})", name=t["artist"])
            await session.run(
                """
                MATCH (tr:Track {id: $id}), (a:Artist {name: $artist})
                MERGE (tr)-[:BY]->(a)
                """,
                id=t["id"], artist=t["artist"],
            )
            await session.run("MERGE (g:Genre {name: $name})", name=t["genre"])
            await session.run(
                """
                MATCH (tr:Track {id: $id}), (g:Genre {name: $genre})
                MERGE (tr)-[:HAS_GENRE]->(g)
                """,
                id=t["id"], genre=t["genre"],
            )
            await session.run(
                """
                MATCH (a:Artist {name: $artist}), (g:Genre {name: $genre})
                MERGE (a)-[:HAS_GENRE]->(g)
                """,
                artist=t["artist"], genre=t["genre"],
            )


async def main():
    if not settings.apple_music_developer_token:
        print("✗ APPLE_MUSIC_DEVELOPER_TOKEN이 설정되지 않았습니다.")
        sys.exit(1)

    # 로컬 실행 시 host.docker.internal 대신 localhost 사용
    neo4j_uri = settings.neo4j_uri.replace("host.docker.internal", "localhost")

    print(f"Apple Music [{STOREFRONT}] 차트 수집 중...")
    tracks = await fetch_all_charts()

    if not tracks:
        print("✗ 가져온 트랙이 없습니다. Developer Token을 확인하세요.")
        sys.exit(1)

    print(f"\n총 {len(tracks)}개 고유 트랙 → Neo4j 삽입 중...")

    driver = AsyncGraphDatabase.driver(
        neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )
    try:
        await insert_tracks(driver, tracks)

        async with driver.session() as session:
            r = await session.run("MATCH (t:Track) RETURN count(t) AS cnt")
            rec = await r.single()
            print(f"\n✓ 완료 — Neo4j 전체 트랙 수: {rec['cnt']}")

    finally:
        await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
