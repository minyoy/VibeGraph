# VibeGraph 요구사항 명세서

## 1. 목적

VibeGraph는 Apple Music 플레이리스트를 Neo4j Graph DB로 동기화하고, 사용자의 음악 취향 관계를 탐색하여 추천 후보를 만든 뒤, LLM이 추천 이유와 플레이리스트 이름을 생성하는 개인화 음악 추천 시스템이다.

이 문서는 바이브코딩 과정에서 다음 질문에 빠르게 답하기 위한 기준 문서로 사용한다.

- 어떤 기능을 먼저 구현해야 하는가?
- 프론트엔드, 백엔드, 외부 API, Graph DB의 책임은 어디까지인가?
- 추천 결과가 최소한 어떤 품질과 설명 가능성을 가져야 하는가?
- 현재 구현의 한계와 확장 방향은 무엇인가?

## 2. 시스템 범위

### 포함 범위

- Apple Music 사용자 인증 토큰을 이용한 플레이리스트 조회
- 선택한 플레이리스트의 트랙 조회
- 사용자, 플레이리스트, 트랙, 아티스트, 장르를 Neo4j에 저장
- 그래프 관계 기반 취향 분석
- 그래프 탐색 기반 추천 후보 생성
- OpenAI API를 통한 추천 이유 및 플레이리스트 이름 생성
- 추천 트랙으로 Apple Music 플레이리스트 생성

### 제외 범위 또는 현재 미구현 범위

- 자체 회원가입 및 다중 사용자 인증
- Apple Music Developer Token 자동 갱신
- Music User Token 갱신
- Artist 유사도 관계 `SIMILAR_TO`
- 협업 필터링, 임베딩, PageRank, Node2Vec 기반 추천
- 사용자 피드백 기반 추천 개선
- Spotify 등 다른 음악 플랫폼 연동

## 3. 이해관계자

| 이해관계자 | 관심사 |
| --- | --- |
| 최종 사용자 | Apple Music 기반으로 취향에 맞는 추천 플레이리스트를 쉽게 생성 |
| 프론트엔드 개발자 | MusicKit 로그인, 상태 흐름, API 호출 순서, 오류 표시 |
| 백엔드 개발자 | Apple Music API 프록시, Neo4j 동기화, 추천/분석 API 안정성 |
| AI/추천 개발자 | 그래프 모델, 추천 후보 생성 로직, LLM 설명 품질 |
| 운영자 | 환경변수, 토큰, 외부 API 장애, Neo4j 연결 상태 |

## 4. 사용자 목표

1. 사용자는 Apple Music 계정을 연결할 수 있어야 한다.
2. 사용자는 자신의 플레이리스트 목록을 볼 수 있어야 한다.
3. 사용자는 분석할 플레이리스트를 하나 이상 선택할 수 있어야 한다.
4. 사용자는 선택한 플레이리스트를 Graph DB에 동기화할 수 있어야 한다.
5. 사용자는 자신의 Top Artists, Top Genres, 취향 태그, 무드 태그를 볼 수 있어야 한다.
6. 사용자는 그래프 기반 추천 후보를 받을 수 있어야 한다.
7. 사용자는 각 추천 곡에 대해 왜 추천되었는지 설명을 볼 수 있어야 한다.
8. 사용자는 추천 곡으로 Apple Music 플레이리스트를 생성할 수 있어야 한다.

## 5. 기능 요구사항

### FR-01 Apple Music 연결

- 프론트엔드는 MusicKit JS를 이용해 `Music-User-Token`을 획득해야 한다.
- 백엔드는 Apple Music Developer Token을 서버 환경변수에서 읽어야 한다.
- Apple Music API를 호출하는 백엔드 엔드포인트는 `Music-User-Token` 헤더를 요구해야 한다.

### FR-02 플레이리스트 조회

- 사용자는 자신의 Apple Music 라이브러리 플레이리스트 목록을 조회할 수 있어야 한다.
- 각 플레이리스트는 `id`, `name`, `trackCount`, `artwork`를 포함해야 한다.

### FR-03 트랙 조회

- 사용자는 특정 플레이리스트의 트랙 목록을 조회할 수 있어야 한다.
- 각 트랙은 `id`, `title`, `artist`, `genre`, `albumArt`를 포함해야 한다.
- 장르가 없으면 `Unknown`으로 처리한다.

### FR-04 Graph DB 동기화

- 사용자는 선택한 플레이리스트 목록을 백엔드에 전달해 Neo4j에 동기화할 수 있어야 한다.
- 백엔드는 전달된 플레이리스트의 트랙을 Apple Music에서 다시 조회한 뒤 저장해야 한다.
- Neo4j에는 다음 노드가 생성 또는 갱신되어야 한다.
  - `User`
  - `Playlist`
  - `Track`
  - `Artist`
  - `Genre`
- Neo4j에는 다음 관계가 생성되어야 한다.
  - `(User)-[:OWNS]->(Playlist)`
  - `(Playlist)-[:CONTAINS]->(Track)`
  - `(Track)-[:BY]->(Artist)`
  - `(Track)-[:HAS_GENRE]->(Genre)`
  - `(Artist)-[:HAS_GENRE]->(Genre)`

### FR-05 취향 분석

- 사용자는 동기화된 그래프 데이터를 기반으로 취향 분석 결과를 조회할 수 있어야 한다.
- 분석 결과는 `topArtists`, `topGenres`, `detectedTaste`, `moodTags`를 포함해야 한다.
- 취향 태그와 무드 태그는 장르/아티스트 집계 결과에서 파생된다.

### FR-06 Graph 추천 후보 생성

- 사용자는 사용자 ID와 추천 개수를 지정해 추천 후보를 조회할 수 있어야 한다.
- 추천 후보는 사용자가 이미 보유한 플레이리스트에 포함된 곡을 제외해야 한다.
- 현재 추천 기준은 사용자의 상위 장르와 같은 장르에 연결된 미보유 트랙이다.
- 추천 결과는 `id`, `title`, `artist`, `genre`, `score`, `graphPath`, `reason`을 포함해야 한다.
- LLM 설명 전 `reason`은 빈 문자열일 수 있다.

### FR-07 AI 추천 이유 생성

- 사용자는 추천 후보와 취향 프로필을 LLM Agent에 전달해 추천 이유를 생성할 수 있어야 한다.
- Agent는 전체 추천 전략 설명, 플레이리스트 이름, 각 트랙별 추천 이유를 JSON으로 반환해야 한다.
- 추천 이유는 그래프 경로, 장르/무드/아티스트 연결, 사용자 취향과의 적합성을 포함해야 한다.

### FR-08 Apple Music 플레이리스트 생성

- 사용자는 AI가 추천한 트랙 ID 목록으로 Apple Music에 새 플레이리스트를 생성할 수 있어야 한다.
- 생성 요청은 `userId`, `playlistName`, `trackIds`, `musicUserToken`을 포함해야 한다.
- 성공 시 생성된 `playlistId`와 메시지를 반환해야 한다.

## 6. 비기능 요구사항

| 구분 | 요구사항 |
| --- | --- |
| 사용성 | 사용자는 연결, 선택, 동기화, 분석, 추천, 생성 흐름을 한 화면에서 순차적으로 진행할 수 있어야 한다. |
| 설명 가능성 | 추천 결과는 `graphPath`와 자연어 추천 이유를 제공해야 한다. |
| 안정성 | Apple Music, Neo4j, OpenAI 장애는 사용자에게 구체적인 오류로 표시되어야 한다. |
| 보안 | Developer Token과 OpenAI API Key는 백엔드 환경변수에만 저장한다. |
| 확장성 | 추천 로직은 `GraphRecommendationService`를 중심으로 교체 가능해야 한다. |
| 관측성 | 동기화 결과는 생성된 노드/관계 수를 반환해야 한다. |

## 7. 핵심 데이터

| 모델 | 필드 | 설명 |
| --- | --- | --- |
| User | `id` | 현재 구현에서는 `user_default` 사용 가능 |
| Playlist | `id`, `name` | Apple Music 라이브러리 플레이리스트 |
| Track | `id`, `title`, `artist`, `genre`, `albumArt` | 추천/분석의 기본 단위 |
| Artist | `name` | 트랙의 아티스트 |
| Genre | `name` | 트랙 및 아티스트의 장르 |
| RecommendedTrack | `id`, `title`, `artist`, `genre`, `score`, `graphPath`, `reason` | 추천 결과 |

## 8. 품질 기준

- 플레이리스트를 1개 이상 선택하지 않으면 동기화를 실행하지 않는다.
- `Music-User-Token`이 없으면 Apple Music 관련 API는 실패해야 한다.
- Neo4j 연결 실패 시 추천/분석/동기화는 명확한 오류를 반환해야 한다.
- 추천 후보가 없으면 “더 많은 플레이리스트를 동기화하라”는 취지의 오류를 반환해야 한다.
- LLM 응답은 유효한 JSON이어야 하며, 파싱 실패 시 오류를 반환해야 한다.

## 9. 바이브코딩 구현 우선순위

1. Apple Music 연결 및 플레이리스트 조회
2. Graph DB 동기화
3. 취향 분석 결과 표시
4. Graph 추천 후보 표시
5. AI 추천 이유 생성
6. Apple Music 플레이리스트 생성
7. 오류 상태와 재시도 UX 개선
8. 추천 알고리즘 고도화

## 10. 주요 리스크

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| Apple Music 토큰 만료 | 로그인/조회/생성 실패 | 토큰 만료 메시지와 재인증 흐름 추가 |
| Graph DB 데이터 부족 | 추천 후보 없음 | 최소 선택 플레이리스트 수 안내 |
| 추천 결과 단조로움 | 사용자 만족도 저하 | 장르 외 Artist 유사도, PageRank, 피드백 반영 |
| LLM JSON 파싱 실패 | 추천 이유 표시 실패 | JSON response format 유지, fallback reason 제공 |
| 다중 사용자 미지원 | 실제 서비스 확장 제한 | JWT 세션과 Apple 사용자 식별자 도입 |
