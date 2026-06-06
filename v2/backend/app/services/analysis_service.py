from app.services.neo4j_service import get_user_artist_counts, get_user_genre_counts

TASTE_MAP = {
    "Pop": "Pop Vibes",
    "Hip-Hop": "Hip-Hop Head",
    "R&B": "R&B Soul",
    "Rock": "Rock Spirit",
    "Electronic": "Electronic Wave",
    "Jazz": "Jazz Lover",
    "Classical": "Classical Mind",
    "K-Pop": "K-Pop Fan",
    "Indie": "Indie Explorer",
    "Dance": "Dance Energy",
    "Soul": "Soul Depth",
    "Metal": "Metal Edge",
}

MOOD_MAP = {
    "Energetic": ["Pop", "Electronic", "Hip-Hop", "Dance", "K-Pop"],
    "Chill": ["R&B", "Jazz", "Soul", "Lo-Fi", "Acoustic"],
    "Melancholic": ["Indie", "Alternative", "Singer-Songwriter"],
    "Focused": ["Classical", "Instrumental", "Ambient"],
    "Hype": ["Hip-Hop", "Trap", "Electronic", "Metal"],
}


async def get_analysis(user_id: str) -> dict:
    artists = await get_user_artist_counts(user_id)
    genres = await get_user_genre_counts(user_id)

    top_genre_names = [g["name"] for g in genres[:5]]

    detected_taste = list({
        TASTE_MAP[g] for g in top_genre_names if g in TASTE_MAP
    })

    mood_tags = [
        mood for mood, keywords in MOOD_MAP.items()
        if any(k in top_genre_names for k in keywords)
    ]

    return {
        "topArtists": artists[:10],
        "topGenres": genres[:10],
        "detectedTaste": detected_taste or ["Eclectic"],
        "moodTags": mood_tags or ["Neutral"],
    }
