# VibeGraph 테스트 체크리스트

이 체크리스트는 바이브코딩으로 빠르게 기능을 붙일 때 놓치기 쉬운 통합 흐름, 외부 API 의존성, Graph DB 상태, LLM 응답 품질을 점검하기 위한 문서다.

## 1. 환경 및 실행

- [ ] `backend/.env`에 `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `OPENAI_API_KEY`, `APPLE_MUSIC_DEVELOPER_TOKEN`이 설정되어 있다.
- [ ] `frontend/.env.local`에 `VITE_API_BASE_URL`, `VITE_APPLE_MUSIC_DEVELOPER_TOKEN`이 설정되어 있다.
- [ ] `docker-compose up --build` 실행 시 frontend, backend, neo4j가 모두 시작된다.
- [ ] `GET http://localhost:8000/health`가 `{ "status": "ok" }`를 반환한다.
- [ ] `http://localhost:8000/docs`에서 OpenAPI 문서가 열린다.
- [ ] Neo4j Browser `http://localhost:7474`에 접속할 수 있다.

## 2. Apple Music 인증

- [ ] Apple Music 로그인 버튼 클릭 시 MusicKit 승인 팝업이 열린다.
- [ ] 승인 후 `musicUserToken`이 프론트엔드 상태에 저장된다.
- [ ] 토큰이 없는 상태에서 `/apple/playlists` 호출 시 오류가 발생한다.
- [ ] 만료되거나 잘못된 Music User Token으로 호출 시 인증 오류가 표시된다.
- [ ] Apple Music Developer Token이 누락되면 백엔드가 명확한 오류를 반환한다.

## 3. 플레이리스트 조회

- [ ] `/apple/playlists`가 플레이리스트 목록을 반환한다.
- [ ] 각 항목에 `id`, `name`, `trackCount`, `artwork`가 포함된다.
- [ ] artwork가 없는 플레이리스트도 UI가 깨지지 않는다.
- [ ] 플레이리스트가 0개일 때 빈 상태 메시지가 표시된다.
- [ ] 플레이리스트 선택/해제가 정상 동작한다.

## 4. 트랙 조회

- [ ] `/apple/playlists/{id}/tracks`가 트랙 목록을 반환한다.
- [ ] 각 트랙에 `id`, `title`, `artist`, `genre`, `albumArt`가 포함된다.
- [ ] 장르가 없는 트랙은 `Unknown`으로 처리된다.
- [ ] 트랙이 100개 이상인 플레이리스트의 페이지네이션 한계를 확인한다.
- [ ] 삭제되었거나 접근 불가능한 플레이리스트 ID 호출 시 오류가 표시된다.

## 5. Graph DB 동기화

- [ ] 플레이리스트를 선택하지 않으면 동기화 버튼이 비활성화되거나 오류가 표시된다.
- [ ] `/graph/sync` 요청에 `Music-User-Token` 헤더가 포함된다.
- [ ] 동기화 성공 시 `nodesCreated`, `relationshipsCreated`가 표시된다.
- [ ] 같은 플레이리스트를 여러 번 동기화해도 중복 노드가 과도하게 늘어나지 않는다.
- [ ] Neo4j에서 `User`, `Playlist`, `Track`, `Artist`, `Genre` 노드가 생성된다.
- [ ] Neo4j에서 `OWNS`, `CONTAINS`, `BY`, `HAS_GENRE` 관계가 생성된다.

Neo4j 확인 쿼리:

```cypher
MATCH (n) RETURN labels(n), count(*) ORDER BY count(*) DESC;
```

```cypher
MATCH ()-[r]->() RETURN type(r), count(*) ORDER BY count(*) DESC;
```

## 6. 취향 분석

- [ ] `/analysis/user_default`가 `topArtists`, `topGenres`, `detectedTaste`, `moodTags`를 반환한다.
- [ ] Top Artists는 트랙 수 기준 내림차순이다.
- [ ] Top Genres는 트랙 수 기준 내림차순이다.
- [ ] 알려진 장르 키워드가 있으면 적절한 `detectedTaste`가 생성된다.
- [ ] 알려진 무드 키워드가 없으면 `Neutral`이 반환된다.
- [ ] 동기화 데이터가 없을 때 UI가 빈 분석 결과를 안전하게 처리한다.

## 7. Graph 추천

- [ ] `/recommendations/user_default?limit=10`이 추천 후보를 반환한다.
- [ ] `limit`은 1 이상 50 이하만 허용된다.
- [ ] 추천 후보에 `id`, `title`, `artist`, `genre`, `score`, `graphPath`, `reason`이 포함된다.
- [ ] 사용자가 이미 보유한 플레이리스트의 트랙은 추천 후보에서 제외된다.
- [ ] `graphPath`가 추천 근거를 이해할 수 있는 문자열로 표시된다.
- [ ] 후보가 없을 때 “더 많은 플레이리스트를 동기화”하라는 메시지가 표시된다.

## 8. AI 추천 이유

- [ ] `/agent/explain` 요청에 추천 후보와 취향 프로필이 포함된다.
- [ ] 응답에 `playlistName`, `explanation`, `tracks`가 포함된다.
- [ ] 각 추천 트랙에 빈 문자열이 아닌 `reason`이 포함된다.
- [ ] 추천 이유가 장르, 무드, 그래프 경로 중 하나 이상을 언급한다.
- [ ] OpenAI API Key가 없을 때 명확한 오류가 표시된다.
- [ ] LLM 응답 파싱 실패 상황을 대비한 UI 오류 처리가 있다.

## 9. 플레이리스트 생성

- [ ] `/apple/playlists/create` 요청에 `userId`, `playlistName`, `trackIds`, `musicUserToken`이 포함된다.
- [ ] `trackIds`가 비어 있으면 생성 요청을 보내지 않는다.
- [ ] 성공 시 `playlistId`와 성공 메시지가 표시된다.
- [ ] Apple Music 라이브러리에 새 플레이리스트가 실제로 생성된다.
- [ ] 생성 실패 시 원인을 포함한 오류 메시지가 표시된다.

## 10. 프론트엔드 사용성

- [ ] 연결 전에는 플레이리스트 조회/동기화/추천 액션이 실행되지 않는다.
- [ ] 각 비동기 작업 중 로딩 상태가 표시된다.
- [ ] 같은 버튼을 연속 클릭해 중복 요청이 발생하지 않는다.
- [ ] 모바일 화면에서도 주요 버튼과 결과 카드가 겹치지 않는다.
- [ ] 추천 후보와 AI 추천 이유가 구분되어 표시된다.
- [ ] 생성된 플레이리스트 카드가 생성 완료 후 표시된다.

## 11. 회귀 테스트 포인트

- [ ] API 스키마 필드명을 바꾼 경우 프론트엔드 `api.js`와 컴포넌트 props를 같이 수정했다.
- [ ] Neo4j 관계명을 바꾼 경우 분석/추천 Cypher 쿼리를 같이 수정했다.
- [ ] 추천 점수 산식을 바꾼 경우 정렬 기준과 UI 표시를 같이 확인했다.
- [ ] LLM 프롬프트를 바꾼 경우 JSON 응답 형식이 유지된다.
- [ ] Apple Music API 타입을 바꾼 경우 플레이리스트 생성이 실제 계정에서 성공한다.

## 12. 바이브코딩 중 빠른 수동 테스트 시나리오

1. 앱 실행 후 Apple Music 로그인
2. 플레이리스트 1개 선택
3. Graph DB 동기화 실행
4. 취향 분석 실행
5. Graph 추천 생성
6. AI 추천 이유 생성
7. Apple Music 플레이리스트 생성
8. Neo4j Browser에서 노드/관계 수 확인
9. Apple Music 앱에서 생성된 플레이리스트 확인
