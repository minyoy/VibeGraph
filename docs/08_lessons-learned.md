# VibeGraph Lessons Learned

## 1. 바이브코딩에 도움이 된 문서화 포인트

README만으로도 전체 흐름은 이해할 수 있지만, 실제 구현을 빠르게 확장하려면 다음 문서가 특히 도움이 된다.

- 요구사항 명세: 기능의 포함 범위와 제외 범위를 고정해 불필요한 구현을 줄인다.
- 유스케이스 다이어그램: 사용자, Apple Music, Neo4j, OpenAI의 책임 경계를 빠르게 파악하게 해준다.
- 액티비티 다이어그램: 프론트엔드 상태 흐름과 오류 분기를 구현할 때 유용하다.
- 도메인 모델: Neo4j 노드/관계와 API 스키마가 엇갈리지 않게 해준다.
- 시퀀스 다이어그램: 추천 후보 생성과 LLM 설명 생성의 호출 순서를 명확하게 만든다.
- API 명세: 프론트엔드와 백엔드의 필드명 불일치를 줄인다.
- 테스트 체크리스트: 외부 API 의존성이 있는 기능의 수동 검증 비용을 낮춘다.

## 2. 현재 설계에서 좋은 점

- Graph DB를 사용해 추천 이유의 근거가 되는 `graphPath`를 만들 수 있다.
- FastAPI 라우터가 `apple`, `graph`, `analysis`, `recommendations`, `agent`로 나뉘어 기능 경계가 비교적 명확하다.
- Pydantic 스키마가 있어 프론트엔드와 백엔드 간 데이터 계약을 문서화하기 쉽다.
- 추천 후보 생성과 LLM 설명 생성이 분리되어 있어, 추천 알고리즘을 바꿔도 설명 생성 흐름을 유지할 수 있다.
- Docker Compose 기반 실행 경로가 있어 개발 환경 재현이 쉽다.

## 3. 바이브코딩 중 주의해야 할 점

### API 필드명 불일치

현재 프론트엔드와 백엔드는 camelCase 필드를 사용한다. 예를 들어 `userId`, `trackIds`, `musicUserToken`, `graphPath`가 그대로 계약이다. 바이브코딩 중 Python 스타일의 snake_case로 바꾸면 프론트엔드가 즉시 깨질 수 있다.

### 외부 API 오류를 로컬 버그로 착각하기 쉬움

Apple Music과 OpenAI는 토큰, 권한, 네트워크, 계정 상태에 따라 실패할 수 있다. 실패 원인을 구분하려면 오류 메시지, 요청 헤더, 환경변수 존재 여부를 먼저 확인해야 한다.

### Neo4j 데이터가 없으면 추천도 없다

추천 API는 동기화된 그래프 데이터에 의존한다. 추천 후보가 없을 때는 알고리즘 오류인지, 데이터 부족인지, 동기화 실패인지 분리해서 봐야 한다.

### LLM 응답은 구조를 강제해야 함

Agent는 JSON 응답을 기대한다. 프롬프트를 수정할 때 `response_format={"type": "json_object"}`와 응답 스키마 요구를 유지해야 한다.

### 현재 추천 후보 풀은 제한적일 수 있음

지금은 사용자가 동기화한 그래프 안에 존재하면서 사용자가 소유하지 않은 트랙을 후보로 찾는다. 외부 카탈로그 검색이나 Artist 유사도 데이터가 없으면 추천 후보가 적거나 없을 수 있다.

## 4. 개선하면 좋은 설계 결정

| 영역 | 현재 | 개선 방향 |
| --- | --- | --- |
| 사용자 식별 | `user_default` 중심 | Apple Music 사용자 식별자 또는 자체 JWT 세션 |
| 오류 처리 | 전역 `500` 중심 | 인증, 외부 API, DB, 추천 없음 오류별 상태 코드 |
| 추천 알고리즘 | 상위 장르 기반 | Artist 유사도, PageRank, Node2Vec, 피드백 반영 |
| 토큰 관리 | 수동 설정 | Developer Token 자동 생성/갱신 |
| 추천 후보 소스 | Neo4j 내부 트랙 | Apple Music Catalog Search 또는 외부 음악 API 연동 |
| 테스트 | 수동 확인 중심 | 서비스 단위 테스트와 API 통합 테스트 추가 |

## 5. 다음 구현에 바로 쓸 수 있는 작업 단위

1. 오류 상태 코드 분리
   - `AppleMusicAuthError`: `401`
   - `AppleMusicAPIError`: `502`
   - `Neo4jConnectionError`: `503`
   - `NoRecommendationsError`: `404` 또는 `422`
   - `LLMError`: `502`

2. Graph 추천 후보 확장
   - Apple Music Catalog Search로 같은 장르의 새 곡을 가져온다.
   - Neo4j에 후보 트랙을 임시 저장하거나 API 응답으로만 사용한다.
   - 기존 보유 트랙 제외 조건을 유지한다.

3. Artist 유사도 관계 추가
   - `(:Artist)-[:SIMILAR_TO {source, score}]->(:Artist)` 관계를 추가한다.
   - Last.fm, MusicBrainz, Apple Music 카탈로그 정보를 후보 소스로 검토한다.
   - 추천 경로에 `SIMILAR_TO`가 포함되면 설명 가능성이 높아진다.

4. 사용자 피드백 반영
   - `(:User)-[:LIKED]->(:Track)`
   - `(:User)-[:DISLIKED]->(:Track)`
   - 추천 쿼리에서 liked 장르/아티스트 가중치 증가, disliked 후보 제외를 적용한다.

5. 프론트엔드 상태 머신 정리
   - `disconnected`
   - `connected`
   - `playlistSelected`
   - `synced`
   - `analyzed`
   - `recommended`
   - `explained`
   - `created`

## 6. 문서 기반 바이브코딩 체크 방법

새 기능을 추가할 때는 다음 순서로 문서를 갱신하면 좋다.

1. `01_requirements.md`에서 기능 범위와 성공 조건을 추가한다.
2. `04_domain-model.puml`에서 새 노드, 관계, 응답 모델을 추가한다.
3. `06_api-spec.md`에서 요청/응답 계약을 먼저 적는다.
4. 구현 후 `07_test-checklist.md`에 수동/자동 테스트 항목을 추가한다.
5. 실제 구현 중 막혔던 점은 `08_lessons-learned.md`에 남긴다.

## 7. 결론

VibeGraph는 바이브코딩으로 확장하기 좋은 구조를 가지고 있다. 다만 외부 API와 Graph DB, LLM이 함께 얽혀 있기 때문에 “작동하는 화면”만 보고 구현을 이어가면 데이터 계약과 실패 분기를 놓치기 쉽다.

이번 문서 세트는 추천 시스템의 핵심 흐름을 요구사항, 다이어그램, API 계약, 테스트 기준으로 나누어 고정한다. 따라서 새 기능을 빠르게 붙이더라도 어떤 필드가 유지되어야 하는지, 어떤 관계가 추천 근거가 되는지, 어떤 오류를 먼저 확인해야 하는지 판단하는 기준으로 사용할 수 있다.
