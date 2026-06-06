# VibeGraph Backend

FastAPI 기반 백엔드 서버

## 빠른 시작

```bash
cd backend
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # .env 파일 편집 후
uvicorn app.main:app --reload
```

API 문서: http://localhost:8000/docs

## 환경변수

| 변수 | 설명 |
|------|------|
| `NEO4J_URI` | Neo4j bolt URI (기본: bolt://localhost:7687) |
| `NEO4J_USERNAME` | Neo4j 사용자명 |
| `NEO4J_PASSWORD` | Neo4j 패스워드 |
| `OPENAI_API_KEY` | OpenAI API 키 |
| `APPLE_MUSIC_DEVELOPER_TOKEN` | Apple Music Developer JWT 토큰 |
