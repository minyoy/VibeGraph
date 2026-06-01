from neo4j import AsyncGraphDatabase, AsyncDriver
from typing import Optional
from app.core.config import get_settings
from app.utils.errors import Neo4jConnectionError
import logging

logger = logging.getLogger(__name__)


class Neo4jService:
    _driver: Optional[AsyncDriver] = None

    def __init__(self):
        self.settings = get_settings()

    async def get_driver(self) -> AsyncDriver:
        if self._driver is None:
            try:
                self._driver = AsyncGraphDatabase.driver(
                    self.settings.neo4j_uri,
                    auth=(self.settings.neo4j_username, self.settings.neo4j_password),
                )
                await self._driver.verify_connectivity()
            except Exception as e:
                self._driver = None
                raise Neo4jConnectionError(f"Cannot connect to Neo4j: {str(e)}")
        return self._driver

    async def close(self):
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def sync_graph(self, user_id: str, playlists_with_tracks: list[dict]) -> dict:
        driver = await self.get_driver()
        nodes_created = 0
        rels_created = 0

        async with driver.session() as session:
            # Merge user node
            await session.run(
                "MERGE (u:User {id: $id}) ON CREATE SET u.createdAt = timestamp()",
                id=user_id,
            )
            nodes_created += 1

            for playlist in playlists_with_tracks:
                pl_id = playlist["id"]
                pl_name = playlist["name"]

                # Merge playlist node and OWNS relation
                result = await session.run(
                    """
                    MERGE (p:Playlist {id: $pid})
                    ON CREATE SET p.name = $name, p.createdAt = timestamp()
                    ON MATCH SET p.name = $name
                    WITH p
                    MATCH (u:User {id: $uid})
                    MERGE (u)-[r:OWNS]->(p)
                    ON CREATE SET r.since = timestamp()
                    RETURN r
                    """,
                    pid=pl_id, name=pl_name, uid=user_id,
                )
                summary = await result.consume()
                nodes_created += summary.counters.nodes_created
                rels_created += summary.counters.relationships_created

                for track in playlist.get("tracks", []):
                    t_id = track["id"]
                    t_title = track["title"]
                    t_artist = track["artist"]
                    t_genre = track.get("genre", "Unknown")

                    result = await session.run(
                        """
                        MERGE (t:Track {id: $tid})
                        ON CREATE SET t.title = $title, t.artist = $artist, t.genre = $genre
                        ON MATCH SET t.title = $title, t.artist = $artist, t.genre = $genre
                        WITH t
                        MATCH (p:Playlist {id: $pid})
                        MERGE (p)-[:CONTAINS]->(t)
                        WITH t
                        MERGE (a:Artist {name: $artist})
                        MERGE (t)-[:BY]->(a)
                        WITH t, a
                        MERGE (g:Genre {name: $genre})
                        MERGE (t)-[:HAS_GENRE]->(g)
                        MERGE (a)-[:HAS_GENRE]->(g)
                        RETURN t
                        """,
                        tid=t_id, title=t_title, artist=t_artist,
                        genre=t_genre, pid=pl_id,
                    )
                    summary = await result.consume()
                    nodes_created += summary.counters.nodes_created
                    rels_created += summary.counters.relationships_created

        return {"nodesCreated": nodes_created, "relationshipsCreated": rels_created}

    async def get_taste_analysis(self, user_id: str) -> dict:
        driver = await self.get_driver()
        async with driver.session() as session:
            top_artists_result = await session.run(
                """
                MATCH (u:User {id: $uid})-[:OWNS]->(p:Playlist)-[:CONTAINS]->(t:Track)-[:BY]->(a:Artist)
                RETURN a.name AS artist, count(t) AS count
                ORDER BY count DESC LIMIT 10
                """,
                uid=user_id,
            )
            top_artists = [{"name": r["artist"], "count": r["count"]} async for r in top_artists_result]

            top_genres_result = await session.run(
                """
                MATCH (u:User {id: $uid})-[:OWNS]->(p:Playlist)-[:CONTAINS]->(t:Track)-[:HAS_GENRE]->(g:Genre)
                RETURN g.name AS genre, count(t) AS count
                ORDER BY count DESC LIMIT 10
                """,
                uid=user_id,
            )
            top_genres = [{"name": r["genre"], "count": r["count"]} async for r in top_genres_result]

        detected_taste = self._detect_taste(top_genres)
        mood_tags = self._detect_moods(top_artists, top_genres)

        return {
            "topArtists": top_artists,
            "topGenres": top_genres,
            "detectedTaste": detected_taste,
            "moodTags": mood_tags,
        }

    def _detect_taste(self, genres: list[dict]) -> list[str]:
        taste_map = {
            "indie": "Chill Indie", "pop": "Pop Vibes", "rock": "Rock Energy",
            "electronic": "Electronic Beats", "jazz": "Jazz Soul", "r&b": "R&B Smooth",
            "hip-hop": "Hip-Hop Groove", "classical": "Classical Depth",
            "folk": "Folk Stories", "alternative": "Alternative Edge",
            "dream": "Dream Pop", "ambient": "Ambient Space",
        }
        result = []
        for g in genres[:5]:
            name_lower = g["name"].lower()
            for key, label in taste_map.items():
                if key in name_lower and label not in result:
                    result.append(label)
        return result if result else ["Eclectic Mix"]

    def _detect_moods(self, artists: list[dict], genres: list[dict]) -> list[str]:
        moods = []
        genre_names = " ".join(g["name"].lower() for g in genres)
        if any(k in genre_names for k in ["chill", "ambient", "indie", "folk"]):
            moods.append("Chill")
        if any(k in genre_names for k in ["dance", "electronic", "pop"]):
            moods.append("Energetic")
        if any(k in genre_names for k in ["jazz", "soul", "r&b"]):
            moods.append("Soulful")
        if any(k in genre_names for k in ["rock", "metal", "alternative"]):
            moods.append("Intense")
        if not moods:
            moods = ["Neutral"]
        return moods

    async def get_recommendations(self, user_id: str, limit: int = 10) -> list[dict]:
        driver = await self.get_driver()
        async with driver.session() as session:
            result = await session.run(
                """
                MATCH (u:User {id: $uid})-[:OWNS]->(p:Playlist)-[:CONTAINS]->(t:Track)-[:HAS_GENRE]->(g:Genre)
                WITH u, g, count(t) AS genre_weight ORDER BY genre_weight DESC LIMIT 5
                MATCH (candidate:Track)-[:HAS_GENRE]->(g)
                WHERE NOT (u)-[:OWNS]->(:Playlist)-[:CONTAINS]->(candidate)
                MATCH (candidate)-[:BY]->(a:Artist)
                WITH candidate, a, g, genre_weight,
                     candidate.id AS cid,
                     candidate.title AS title,
                     candidate.artist AS artist,
                     candidate.genre AS genre,
                     g.name AS matched_genre,
                     genre_weight AS score
                RETURN DISTINCT cid, title, artist, genre, matched_genre, score,
                       'User → Playlist → Track → Genre[' + matched_genre + '] → ' + title AS graph_path
                ORDER BY score DESC
                LIMIT $limit
                """,
                uid=user_id, limit=limit,
            )
            candidates = []
            async for row in result:
                candidates.append({
                    "id": row["cid"],
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "score": float(row["score"]),
                    "graphPath": row["graph_path"],
                    "reason": "",
                })
        return candidates
