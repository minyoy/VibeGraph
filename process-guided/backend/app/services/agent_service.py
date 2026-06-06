import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.utils.errors import LLMError


async def generate_explanation(candidates: list, taste_profile: dict) -> dict:
    if not settings.openai_api_key:
        raise LLMError("OpenAI API key is not configured")

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    prompt = f"""You are a music recommendation assistant for VibeGraph.

User taste profile:
- Top Genres: {[g['name'] for g in taste_profile.get('topGenres', [])[:5]]}
- Top Artists: {[a['name'] for a in taste_profile.get('topArtists', [])[:5]]}
- Detected Taste: {taste_profile.get('detectedTaste', [])}
- Mood Tags: {taste_profile.get('moodTags', [])}

Recommended tracks (with graph paths showing why they were selected):
{json.dumps([{
    'id': c['id'],
    'title': c['title'],
    'artist': c['artist'],
    'genre': c['genre'],
    'score': c['score'],
    'graphPath': c['graphPath'],
} for c in candidates], indent=2)}

Return a JSON object with this exact structure:
{{
  "playlistName": "A creative playlist name reflecting the user's taste",
  "explanation": "2-3 sentences explaining the overall recommendation strategy based on the graph paths and taste profile",
  "tracks": [
    {{
      "id": "same id as input",
      "title": "same title as input",
      "artist": "same artist as input",
      "genre": "same genre as input",
      "score": same score as input,
      "graphPath": "same graphPath as input",
      "reason": "1-2 sentences explaining why this specific track was recommended, referencing the graphPath, genre connection, and mood fit"
    }}
  ]
}}

Every track must have a non-empty reason that references at least one of: graphPath, genre, or mood."""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise LLMError(f"Failed to parse AI response as JSON: {e}")
    except Exception as e:
        raise LLMError(f"OpenAI API error: {e}")

    tracks = result.get("tracks", [])
    for i, track in enumerate(tracks):
        if not track.get("reason") and i < len(candidates):
            track["reason"] = f"Recommended via graph path: {candidates[i]['graphPath']}"

    return {
        "playlistName": result.get("playlistName", "VibeGraph Mix"),
        "explanation": result.get("explanation", "Recommendations based on your music graph."),
        "tracks": tracks,
    }
