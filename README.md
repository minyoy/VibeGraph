# VibeGraph

> Graph Database 기반 개인화 음악 플레이리스트 생성 AI Agent

Apple Music 플레이리스트 데이터를 Neo4j Graph DB에 저장하고, 관계 탐색으로 추천 후보를 생성한 뒤 LLM이 추천 이유를 설명하는 음악 추천 시스템입니다.

---

## 프로젝트 구조

```
VibeGraph/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py             # 앱 진입점, 라우터 등록
│   │   ├── core/config.py      # 환경변수 설정
│   │   ├── api/                # 라우터 (apple, graph, analysis, recommendations, agent)
│   │   ├── services/           # 비즈니스 로직
│   │   │   ├── apple_music_service.py
│   │   │   ├── neo4j_service.py
│   │   │   ├── graph_recommendation_service.py
│   │   │   ├── agent_service.py
│   │   │   └── analysis_service.py
│   │   ├── models/schemas.py   # Pydantic 스키마
│   │   └── utils/errors.py     # 커스텀 예외
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # React + Vite + Tailwind
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/Dashboard.jsx
│   │   ├── components/         # UI 컴포넌트
│   │   └── services/           # api.js, musicKit.js
│   ├── package.json
│   └── .env.example
└── docker-compose.yml
```

---

## 필요한 환경변수

### Backend (`backend/.env`)

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=sk-...
APPLE_MUSIC_DEVELOPER_TOKEN=eyJ...
```

### Frontend (`frontend/.env.local`)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APPLE_MUSIC_DEVELOPER_TOKEN=eyJ...
```

---

## 실행 방법

### 방법 1: Docker Compose (권장)

```bash
# 1. 환경변수 파일 준비
cp backend/.env.example backend/.env
# backend/.env 편집 (NEO4J_PASSWORD, OPENAI_API_KEY, APPLE_MUSIC_DEVELOPER_TOKEN)

# 2. 실행
docker-compose up --build

# 앱:  http://localhost
# API: http://localhost:8000/docs
# Neo4j Browser: http://localhost:7474
```

### 방법 2: 로컬 개발

**Neo4j (Docker)**
```bash
docker run -d \
  --name vibegraph-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:5.23-community
```

**Backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # 값 채우기
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env.local    # 값 채우기
npm run dev
# → http://localhost:5173
```

---

## API 설정 방법

### 1. Apple Music Developer Token 생성

1. [Apple Developer Console](https://developer.apple.com) → Certificates, IDs & Profiles → Keys → Create Key
2. **MusicKit** 권한 체크 후 키 다운로드 (`.p8` 파일)
3. Key ID와 Team ID 확인
4. JWT 생성:

```bash
# 이 프로젝트 루트에 generate_apple_music_token.py 포함
python generate_apple_music_token.py \
  --key-id YOUR_KEY_ID \
  --team-id YOUR_TEAM_ID \
  --private-key-path ./AuthKey_XXXXXXXX.p8
```

생성된 JWT를 `APPLE_MUSIC_DEVELOPER_TOKEN` 환경변수에 설정합니다.

### 2. Neo4j 설정

- **로컬 Docker**: 위 명령어 참고
- **Neo4j AuraDB (클라우드)**: https://console.neo4j.io → Free tier 생성 후 URI/비밀번호 복사

### 3. OpenAI API Key

https://platform.openai.com/api-keys 에서 생성 후 `OPENAI_API_KEY`에 설정

---

## 사용 흐름 예시

1. **Apple Music 연결** — "Apple Music으로 로그인" 버튼 클릭 → 팝업 승인
2. **플레이리스트 선택** — 분석할 플레이리스트 1개 이상 선택
3. **Graph DB 동기화** — "Graph DB에 동기화" 버튼 → Neo4j에 곡/아티스트/장르 관계 저장
4. **취향 분석** — "분석 실행" → Top Artists, Top Genres, Detected Taste, Mood Tags 확인
5. **추천 생성** — "Graph 추천 생성" → Neo4j 관계 탐색 기반 추천 후보 생성
6. **AI 추천 이유** — "AI 추천 이유 생성" → OpenAI가 각 곡의 추천 이유와 플레이리스트 이름 생성
7. **플레이리스트 생성** — "Apple Music에 생성" → 추천 곡으로 새 플레이리스트 생성

---

## 백엔드 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 확인 |
| GET | `/apple/playlists` | 사용자 플레이리스트 목록 |
| GET | `/apple/playlists/{id}/tracks` | 플레이리스트 트랙 목록 |
| POST | `/graph/sync` | Apple Music 데이터 → Neo4j 동기화 |
| GET | `/analysis/{user_id}` | 취향 분석 결과 |
| GET | `/recommendations/{user_id}` | Graph 기반 추천 후보 |
| POST | `/agent/explain` | LLM 추천 이유 생성 |
| POST | `/apple/playlists/create` | Apple Music 플레이리스트 생성 |

---

## 현재 구현의 한계 및 TODO

### 한계

- **userId 고정**: 현재 `user_default`로 고정. 실제 서비스는 Apple Music 사용자 ID 기반 다중 사용자 지원 필요
- **SIMILAR_TO 관계 없음**: `(Artist)-[:SIMILAR_TO]->(Artist)` 관계는 외부 API(MusicBrainz, Last.fm) 연동이 필요해 미구현
- **MusicKit JS 의존**: Apple Music 로그인은 브라우저 환경에서만 동작 (Safari/Chrome)
- **추천 알고리즘 단순**: 현재 장르 기반 단순 탐색. 협업 필터링, 임베딩 기반 유사도 없음
- **토큰 만료 미처리**: Apple Music Developer Token(6개월), Music User Token 갱신 로직 없음

### TODO

- [ ] 다중 사용자 인증 (JWT 기반 세션)
- [ ] Artist SIMILAR_TO 관계 (Last.fm API 연동)
- [ ] 추천 알고리즘 고도화 (PageRank, Node2Vec)
- [ ] 사용자 피드백 기반 추천 개선 (Like/Dislike)
- [ ] Spotify 연동
- [ ] 실시간 스트리밍 추천
- [ ] Apple Music Developer Token 자동 갱신
