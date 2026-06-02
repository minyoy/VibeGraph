# VibeGraph API 명세

Base URL:

- 로컬 개발: `http://localhost:8000`
- Docker Compose 프론트엔드 프록시 사용 시: `/api`

공통 사항:

- Content-Type은 `application/json`을 사용한다.
- Apple Music 사용자 라이브러리에 접근하는 API는 `Music-User-Token` 헤더가 필요하다.
- 현재 전역 예외 핸들러는 많은 오류를 `500`과 `{ "detail": "..." }` 형태로 반환한다. 향후 오류별 HTTP 상태 코드를 분리하는 것이 좋다.

## 1. Health Check

### `GET /health`

서버 상태를 확인한다.

Response:

```json
{
  "status": "ok",
  "service": "VibeGraph API"
}
```

## 2. Apple Music

### `GET /apple/playlists`

Apple Music 사용자 라이브러리의 플레이리스트 목록을 조회한다.

Headers:

| 이름 | 필수 | 설명 |
| --- | --- | --- |
| `Music-User-Token` | Y | MusicKit JS에서 획득한 사용자 토큰 |

Response:

```json
{
  "data": [
    {
      "id": "p.xxxxx",
      "name": "My Playlist",
      "trackCount": 25,
      "artwork": "https://..."
    }
  ]
}
```

### `GET /apple/playlists/{playlist_id}/tracks`

특정 플레이리스트의 트랙 목록을 조회한다.

Path Parameters:

| 이름 | 설명 |
| --- | --- |
| `playlist_id` | Apple Music 플레이리스트 ID |

Headers:

| 이름 | 필수 | 설명 |
| --- | --- | --- |
| `Music-User-Token` | Y | MusicKit JS에서 획득한 사용자 토큰 |

Response:

```json
{
  "data": [
    {
      "id": "i.xxxxx",
      "title": "Track Title",
      "artist": "Artist Name",
      "genre": "Pop",
      "albumArt": "https://..."
    }
  ]
}
```

### `POST /apple/playlists/create`

추천 트랙으로 Apple Music에 새 플레이리스트를 생성한다.

Request Body:

```json
{
  "userId": "user_default",
  "playlistName": "VibeGraph Mix",
  "trackIds": ["i.xxxxx", "i.yyyyy"],
  "musicUserToken": "music-user-token"
}
```

Response:

```json
{
  "success": true,
  "playlistId": "p.created",
  "message": "Playlist 'VibeGraph Mix' created successfully"
}
```

주의:

- 현재 구현은 Apple Music 생성 API 요청에서 `library-songs` 타입을 사용한다.
- `trackIds`는 Apple Music 라이브러리 곡 ID여야 한다.

## 3. Graph

### `POST /graph/sync`

선택한 플레이리스트와 해당 트랙을 Neo4j에 동기화한다.

Headers:

| 이름 | 필수 | 설명 |
| --- | --- | --- |
| `Music-User-Token` | Y | 트랙 재조회에 필요한 사용자 토큰 |

Request Body:

```json
{
  "userId": "user_default",
  "playlists": [
    {
      "id": "p.xxxxx",
      "name": "My Playlist"
    }
  ]
}
```

Response:

```json
{
  "success": true,
  "message": "Synced 1 playlists to graph",
  "nodesCreated": 42,
  "relationshipsCreated": 80
}
```

동기화되는 그래프 구조:

```text
(User)-[:OWNS]->(Playlist)-[:CONTAINS]->(Track)
(Track)-[:BY]->(Artist)
(Track)-[:HAS_GENRE]->(Genre)
(Artist)-[:HAS_GENRE]->(Genre)
```

## 4. Analysis

### `GET /analysis/{user_id}`

동기화된 그래프를 기반으로 사용자의 취향 분석 결과를 조회한다.

Path Parameters:

| 이름 | 설명 |
| --- | --- |
| `user_id` | 사용자 ID. 현재 기본값으로 `user_default` 사용 가능 |

Response:

```json
{
  "topArtists": [
    { "name": "Artist A", "count": 5 }
  ],
  "topGenres": [
    { "name": "Pop", "count": 10 }
  ],
  "detectedTaste": ["Pop Vibes"],
  "moodTags": ["Energetic"]
}
```

## 5. Recommendations

### `GET /recommendations/{user_id}?limit=10`

Neo4j 관계 탐색으로 추천 후보를 생성한다.

Path Parameters:

| 이름 | 설명 |
| --- | --- |
| `user_id` | 사용자 ID |

Query Parameters:

| 이름 | 필수 | 기본값 | 제한 | 설명 |
| --- | --- | --- | --- | --- |
| `limit` | N | `10` | `1..50` | 반환할 추천 후보 수 |

Response:

```json
[
  {
    "id": "i.candidate",
    "title": "Recommended Song",
    "artist": "Artist B",
    "genre": "Pop",
    "score": 8.0,
    "graphPath": "User -> Playlist -> Track -> Genre[Pop] -> Recommended Song",
    "reason": ""
  }
]
```

현재 추천 로직:

- 사용자가 보유한 트랙들의 장르 빈도를 집계한다.
- 상위 5개 장르를 기준으로 같은 장르에 연결된 후보 트랙을 찾는다.
- 사용자가 이미 보유한 플레이리스트에 포함된 트랙은 제외한다.
- 장르 빈도를 `score`로 사용한다.

## 6. Agent

### `POST /agent/explain`

추천 후보에 대해 LLM 기반 추천 이유와 플레이리스트 이름을 생성한다.

Request Body:

```json
{
  "userId": "user_default",
  "candidates": [
    {
      "id": "i.candidate",
      "title": "Recommended Song",
      "artist": "Artist B",
      "genre": "Pop",
      "score": 8.0,
      "graphPath": "User -> Playlist -> Track -> Genre[Pop] -> Recommended Song",
      "reason": ""
    }
  ],
  "tasteProfile": {
    "topArtists": [{ "name": "Artist A", "count": 5 }],
    "topGenres": [{ "name": "Pop", "count": 10 }],
    "detectedTaste": ["Pop Vibes"],
    "moodTags": ["Energetic"]
  }
}
```

Response:

```json
{
  "playlistName": "Neon Pop Routes",
  "explanation": "Recommendations were selected from genres that frequently appear in your playlists.",
  "tracks": [
    {
      "id": "i.candidate",
      "title": "Recommended Song",
      "artist": "Artist B",
      "genre": "Pop",
      "score": 8.0,
      "graphPath": "User -> Playlist -> Track -> Genre[Pop] -> Recommended Song",
      "reason": "This track follows your strong Pop graph path and fits your energetic listening pattern."
    }
  ]
}
```

## 7. 오류 케이스

| 상황 | 현재 응답 경향 | 바이브코딩 시 개선 포인트 |
| --- | --- | --- |
| `Music-User-Token` 누락 | `500` + detail | `401 Unauthorized`로 분리 |
| Apple Music 토큰 만료 | `500` + detail | 재로그인 CTA 표시 |
| Neo4j 연결 실패 | `500` + detail | `/health`에 DB 상태 포함 |
| 추천 후보 없음 | `500` + detail | `404` 또는 `422`와 안내 메시지 |
| OpenAI JSON 파싱 실패 | `500` + detail | fallback reason 생성 |

## 8. 프론트엔드 호출 순서

1. `GET /health`
2. MusicKit으로 `musicUserToken` 획득
3. `GET /apple/playlists`
4. 사용자가 플레이리스트 선택
5. `POST /graph/sync`
6. `GET /analysis/{userId}`
7. `GET /recommendations/{userId}?limit=10`
8. `POST /agent/explain`
9. `POST /apple/playlists/create`
