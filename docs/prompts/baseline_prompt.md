너는 숙련된 풀스택 개발자야.
README.md 내용을 바탕으로 VibeGraph라는 개인화 음악 추천 웹앱의 1차 프로토타입을 실제 동작 가능한 서비스 형태로 구현해줘.

프로젝트 이름은 VibeGraph이다.

VibeGraph는 사용자의 Apple Music 플레이리스트 및 청취 데이터를 기반으로 음악 취향을 분석하고, Neo4j Graph Database를 활용하여 새로운 음악 추천 플레이리스트를 생성하는 AI 기반 음악 추천 시스템이다.

이번 1차 구현에서는 실제 Apple Music API, 실제 Neo4j, 실제 LLM API 연동을 목표로 한다.
단, API key, Apple developer token, user token, Neo4j URI, LLM API key 등 민감한 값은 코드에 직접 작성하지 말고 환경변수로 분리해줘.

전체 목표는 다음과 같다.

1. 사용자가 Apple Music 계정과 연동할 수 있어야 한다.
2. 사용자의 Apple Music 플레이리스트 또는 라이브러리 데이터를 조회할 수 있어야 한다.
3. 조회한 음악 데이터를 기반으로 자주 듣는 아티스트, 장르, 분위기 태그를 분석해야 한다.
4. 곡, 아티스트, 장르, 플레이리스트, 사용자 관계를 Neo4j Graph Database에 저장해야 한다.
5. Neo4j의 관계 탐색을 활용해 추천 후보 곡을 생성해야 한다.
6. 이미 사용자의 플레이리스트에 있는 곡은 추천에서 제외해야 한다.
7. LLM 기반 AI Agent는 Graph DB가 생성한 추천 후보를 바탕으로 추천 이유와 플레이리스트 이름을 생성해야 한다.
8. 사용자는 추천 결과를 확인하고 Apple Music에 새 플레이리스트를 생성할 수 있어야 한다.
9. 추천 결과는 곡 제목, 아티스트, 장르, 추천 점수, 추천 이유, 추천 경로를 포함해야 한다.

기술 스택은 다음을 기준으로 해줘.

Frontend:
- React
- Tailwind CSS
- Vite

Backend:
- FastAPI
- Python

Database:
- Neo4j
- neo4j Python driver 사용

AI / Agent:
- OpenAI API 또는 Claude API 중 하나를 사용할 수 있도록 구현
- 기본은 OpenAI API 기준으로 작성
- LLM 호출부는 agentService로 분리

External API:
- Apple Music API
- MusicKit JS 또는 Apple Music API를 사용할 수 있도록 구조화
- Apple Music 인증에 필요한 developer token, music user token은 환경변수 또는 프론트엔드 인증 흐름에서 안전하게 처리

환경변수 예시는 다음과 같이 구성해줘.

Backend:
- NEO4J_URI
- NEO4J_USERNAME
- NEO4J_PASSWORD
- OPENAI_API_KEY
- APPLE_MUSIC_DEVELOPER_TOKEN

Frontend:
- VITE_API_BASE_URL
- VITE_APPLE_MUSIC_DEVELOPER_TOKEN

보안상 .env 파일은 git에 올리지 않도록 .gitignore에 포함해줘.
.env.example 파일은 제공해줘.

백엔드 API는 다음과 같이 구성해줘.

1. GET /health
- 서버 상태 확인

2. GET /apple/playlists
- Apple Music API를 통해 사용자의 플레이리스트 목록을 조회
- 필요한 경우 music user token을 요청 헤더로 받음

3. GET /apple/playlists/{playlist_id}/tracks
- 특정 플레이리스트의 곡 목록을 조회

4. POST /graph/sync
- Apple Music에서 가져온 사용자, 플레이리스트, 곡, 아티스트, 장르 정보를 Neo4j에 저장
- 관계 예시는 다음과 같다.
  (User)-[:OWNS]->(Playlist)
  (Playlist)-[:CONTAINS]->(Track)
  (Track)-[:BY]->(Artist)
  (Track)-[:HAS_GENRE]->(Genre)

5. GET /analysis/{user_id}
- Graph DB에 저장된 데이터를 기반으로 사용자의 취향 분석 결과를 반환
- topArtists, topGenres, detectedTaste, moodTags 등을 포함

6. GET /recommendations/{user_id}
- Neo4j Graph DB 관계 탐색을 기반으로 추천 후보 곡을 생성
- 이미 사용자의 플레이리스트에 포함된 곡은 제외
- 추천 결과는 title, artist, genre, score, graphPath, reason을 포함

7. POST /agent/explain
- Graph DB 추천 후보를 LLM에 전달하여 추천 이유를 생성
- 추천 이유는 단순 감성 문장이 아니라 graphPath, artist, genre, mood를 반영해야 함

8. POST /apple/playlists/create
- Apple Music API를 통해 추천 곡으로 새 플레이리스트를 생성
- playlistName과 trackIds를 입력받음

백엔드 코드 구조는 다음과 같이 구성해줘.

backend/
  app/
    main.py
    core/
      config.py
    api/
      apple.py
      graph.py
      analysis.py
      recommendations.py
      agent.py
    services/
      apple_music_service.py
      neo4j_service.py
      graph_recommendation_service.py
      agent_service.py
      analysis_service.py
    models/
      schemas.py
    utils/
      errors.py
  requirements.txt
  .env.example
  README.md

프론트엔드 코드 구조는 다음과 같이 구성해줘.

frontend/
  src/
    main.jsx
    App.jsx
    services/
      api.js
      musicKit.js
    components/
      Header.jsx
      AppleMusicLogin.jsx
      PlaylistSelector.jsx
      TasteAnalysis.jsx
      RecommendationList.jsx
      GraphPathView.jsx
      CreatedPlaylistCard.jsx
    pages/
      Dashboard.jsx
  package.json
  .env.example
  README.md

프론트엔드 화면은 다음 흐름으로 구성해줘.

1. Apple Music 로그인 영역
- MusicKit JS 기반 로그인을 고려
- 로그인 성공 시 music user token을 저장해서 백엔드 요청에 사용

2. 플레이리스트 선택 영역
- 사용자의 Apple Music 플레이리스트 목록 표시
- 사용자가 분석할 플레이리스트 선택

3. 데이터 동기화 영역
- 선택한 플레이리스트의 곡 정보를 Neo4j에 저장하는 버튼 제공
- 동기화 성공/실패 메시지 표시

4. 취향 분석 영역
- Top Artists
- Top Genres
- Detected Taste
- Mood Tags

5. 추천 결과 영역
- 추천 곡 리스트
- 추천 이유
- 추천 점수
- 추천 경로 표시
  예: User → Playlist → Track → Artist → Genre → Recommended Track

6. 새 플레이리스트 생성 영역
- 추천 곡을 바탕으로 Apple Music에 새 플레이리스트 생성
- 생성 성공 시 결과 메시지 표시

중요한 구현 조건은 다음과 같다.

1. 외부 API 키와 토큰은 코드에 직접 넣지 않는다.
2. Apple Music API, Neo4j, LLM 호출부는 각각 별도 service로 분리한다.
3. 추천 후보 생성은 LLM이 직접 하지 않고 Neo4j 관계 탐색 결과를 기반으로 한다.
4. LLM은 추천 후보의 설명, 추천 이유, 플레이리스트 이름 생성을 담당한다.
5. 에러 처리를 포함한다.
   - Apple Music 인증 실패
   - 플레이리스트 조회 실패
   - Neo4j 연결 실패
   - 추천 후보 없음
   - LLM 호출 실패
   - 플레이리스트 생성 실패
6. 백엔드는 FastAPI의 Pydantic schema를 사용해 요청/응답 타입을 정의한다.
7. 프론트엔드는 API 호출 상태를 loading, success, error로 구분해 표시한다.
8. README에 실행 방법을 작성한다.
9. 가능하면 Docker Compose로 backend, frontend, neo4j를 실행할 수 있게 구성해줘.
10. 최소한의 동작 확인이 가능한 예시 사용 흐름을 README에 작성해줘.

이번 구현은 “자연어 프롬프트 기반 바이브코딩”의 결과물을 만들기 위한 것이다.
따라서 UML, PlantUML, 정식 요구사항 명세, 테스트 명세는 제공하지 않는다.
README와 이 자연어 프롬프트만을 바탕으로 구현해줘.

최종 결과물로 다음을 제공해줘.

1. 전체 프로젝트 폴더 구조
2. 주요 파일 코드
3. 실행 방법
4. 필요한 환경변수 목록
5. Apple Music API, Neo4j, OpenAI API 설정 방법
6. 현재 구현의 한계와 TODO
