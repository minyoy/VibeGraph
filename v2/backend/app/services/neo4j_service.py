from neo4j import AsyncGraphDatabase
from app.core.config import settings
from app.utils.errors import Neo4jConnectionError

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
        )
    return _driver


async def close_driver():
    global _driver
    if _driver:
        await _driver.close()
        _driver = None


async def sync_playlists(user_id: str, playlists_with_tracks: list) -> dict:
    driver = get_driver()
    nodes_created = 0
    rels_created = 0

    try:
        async with driver.session() as session:
            await session.run(
                "MERGE (u:User {id: $id}) ON CREATE SET u.createdAt = timestamp()",
                id=user_id,
            )
            nodes_created += 1

            for pl in playlists_with_tracks:
                await session.run(
                    """
                    MERGE (p:Playlist {id: $id})
                    ON CREATE SET p.name = $name, p.createdAt = timestamp()
                    ON MATCH SET p.name = $name
                    """,
                    id=pl["id"], name=pl["name"],
                )
                await session.run(
                    """
                    MATCH (u:User {id: $userId}), (p:Playlist {id: $pid})
                    MERGE (u)-[:OWNS]->(p)
                    """,
                    userId=user_id, pid=pl["id"],
                )
                nodes_created += 1
                rels_created += 1

                for track in pl.get("tracks", []):
                    await session.run(
                        """
                        MERGE (t:Track {id: $id})
                        ON CREATE SET t.title = $title, t.artist = $artist,
                                      t.genre = $genre, t.albumArt = $albumArt
                        ON MATCH SET  t.title = $title, t.artist = $artist,
                                      t.genre = $genre, t.albumArt = $albumArt
                        """,
                        id=track["id"], title=track["title"],
                        artist=track["artist"], genre=track["genre"],
                        albumArt=track.get("albumArt") or "",
                    )
                    await session.run(
                        """
                        MATCH (p:Playlist {id: $pid}), (t:Track {id: $tid})
                        MERGE (p)-[:CONTAINS]->(t)
                        """,
                        pid=pl["id"], tid=track["id"],
                    )
                    await session.run(
                        "MERGE (a:Artist {name: $name})",
                        name=track["artist"],
                    )
                    await session.run(
                        """
                        MATCH (t:Track {id: $tid}), (a:Artist {name: $artist})
                        MERGE (t)-[:BY]->(a)
                        """,
                        tid=track["id"], artist=track["artist"],
                    )
                    await session.run(
                        "MERGE (g:Genre {name: $name})",
                        name=track["genre"],
                    )
                    await session.run(
                        """
                        MATCH (t:Track {id: $tid}), (g:Genre {name: $genre})
                        MERGE (t)-[:HAS_GENRE]->(g)
                        """,
                        tid=track["id"], genre=track["genre"],
                    )
                    await session.run(
                        """
                        MATCH (a:Artist {name: $artist}), (g:Genre {name: $genre})
                        MERGE (a)-[:HAS_GENRE]->(g)
                        """,
                        artist=track["artist"], genre=track["genre"],
                    )
                    nodes_created += 3
                    rels_created += 4

    except Exception as e:
        err = str(e)
        if "ServiceUnavailable" in err or "AuthError" in err or "Unable to connect" in err:
            raise Neo4jConnectionError(f"Cannot connect to Neo4j: {err}")
        raise Neo4jConnectionError(f"Graph DB error: {err}")

    return {"nodesCreated": nodes_created, "relationshipsCreated": rels_created}


async def get_user_artist_counts(user_id: str) -> list:
    driver = get_driver()
    try:
        async with driver.session() as session:
            result = await session.run(
                """
                MATCH (u:User {id: $userId})-[:OWNS]->(:Playlist)-[:CONTAINS]->(t:Track)-[:BY]->(a:Artist)
                RETURN a.name AS name, count(t) AS count
                ORDER BY count DESC LIMIT 20
                """,
                userId=user_id,
            )
            return [{"name": r["name"], "count": r["count"]} async for r in result]
    except Exception as e:
        raise Neo4jConnectionError(f"Graph DB error: {e}")


async def get_user_genre_counts(user_id: str) -> list:
    driver = get_driver()
    try:
        async with driver.session() as session:
            result = await session.run(
                """
                MATCH (u:User {id: $userId})-[:OWNS]->(:Playlist)-[:CONTAINS]->(t:Track)-[:HAS_GENRE]->(g:Genre)
                RETURN g.name AS name, count(t) AS count
                ORDER BY count DESC LIMIT 20
                """,
                userId=user_id,
            )
            return [{"name": r["name"], "count": r["count"]} async for r in result]
    except Exception as e:
        raise Neo4jConnectionError(f"Graph DB error: {e}")


async def get_recommendation_candidates(user_id: str, limit: int) -> list:
    driver = get_driver()
    try:
        async with driver.session() as session:
            genre_result = await session.run(
                """
                MATCH (u:User {id: $userId})-[:OWNS]->(:Playlist)-[:CONTAINS]->(t:Track)-[:HAS_GENRE]->(g:Genre)
                RETURN g.name AS genre, count(t) AS cnt
                ORDER BY cnt DESC LIMIT 5
                """,
                userId=user_id,
            )
            top_genres = [r["genre"] async for r in genre_result]

            if not top_genres:
                return []

            owned_result = await session.run(
                """
                MATCH (u:User {id: $userId})-[:OWNS]->(:Playlist)-[:CONTAINS]->(t:Track)
                RETURN t.id AS id
                """,
                userId=user_id,
            )
            owned_ids = [r["id"] async for r in owned_result]

            pool_size = limit * 10  # 후보 풀을 크게 뽑은 뒤 랜덤 샘플링
            cand_result = await session.run(
                """
                MATCH (g:Genre)<-[:HAS_GENRE]-(t:Track)
                WHERE g.name IN $genres AND NOT t.id IN $ownedIds
                WITH t, g, count(g) AS score
                WITH t, score, g.name AS matchedGenre,
                     score * (0.5 + rand() * 0.5) AS weightedScore
                ORDER BY weightedScore DESC
                LIMIT $poolSize
                WITH t, score, matchedGenre
                ORDER BY rand()
                LIMIT $limit
                RETURN t.id AS id, t.title AS title, t.artist AS artist,
                       t.genre AS genre, score, matchedGenre
                """,
                genres=top_genres,
                ownedIds=owned_ids,
                limit=limit,
                poolSize=pool_size,
            )

            candidates = []
            async for r in cand_result:
                candidates.append({
                    "id": r["id"],
                    "title": r["title"],
                    "artist": r["artist"],
                    "genre": r["genre"],
                    "score": float(r["score"]),
                    "graphPath": f"User -> Playlist -> Track -> Genre[{r['matchedGenre']}] -> {r['title']}",
                    "reason": "",
                })
            return candidates

    except Exception as e:
        raise Neo4jConnectionError(f"Graph DB error: {e}")
