1. 문제:
  프론트엔드가 http://localhost에서 실행 중인데, 백엔드 CORS 허용 목록에는 http://localhost:5173, http://localhost:3000만 등록되어 있었습니다. 그래서 Music-User-Token 커스텀 헤더 때문에 브라우저가 먼저 보내는 OPTIONS /apple/playlists preflight 요청이 400 Bad Request로 막혔습니다.

  해결방안:
  백엔드 CORS 허용 목록에 실제 프론트엔드 origin인 http://localhost와 http://127.0.0.1 계열 주소를 추가했습니다. 또한 Docker Compose가 .env를 컨테이너 생성 시점에 읽기 때문에 backend 컨테이너를 recreate해서 변경된 CORS 설정을 반영했습니다.

  결과:
  OPTIONS /apple/playlists는 200 OK로 통과하고, 실제 GET /apple/playlists 요청은 토큰이 없을 때 기존처럼 401 Unauthorized를 반환합니다.

2. 문제:
  프론트엔드 요청 헬퍼에서 Content-Type: application/json이 사라지고 있었습니다.

  기존 코드 구조가 이랬습니다:

  {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  }

  syncGraph 요청처럼 options.headers에 Music-User-Token이 있으면, 뒤의 ...options가 앞에서 만든 headers 전체를 덮어써서 최종 요청에는 Content-Type 없이
  Music-User-Token만 남았습니다.

  그 결과 백엔드는 body를 JSON 객체가 아니라 문자열로 해석했고, 이런 에러가 났습니다:

  Input should be a valid dictionary or object to extract fields from

  해결방안:
  ...options를 먼저 펼치고, 마지막에 headers를 병합하도록 수정했습니다.

  {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  }

  이제 Content-Type: application/json과 Music-User-Token이 둘 다 같이 전송됩니다.

  검증 결과:
  같은 형태의 /graph/sync 요청을 보내면 더 이상 body 파싱 에러가 아니라 정상적으로 인증 단계까지 도달해서, 토큰이 없을 때는 401 Music-User-Token header
  is required가 반환됩니다. 프론트 컨테이너도 재빌드해서 실행 중인 앱에 반영했습니다.

3. 문제:
  백엔드가 Neo4j에 접속할 때 쓰는 계정 정보와, 실제 Neo4j 컨테이너의 계정 정보가 달랐습니다.

  Neo4j 컨테이너는 Compose 설정상 기본적으로:

  username: neo4j
  password: vibegraph

  으로 실행되고 있었는데, 백엔드는 backend/.env에 있는 다른 NEO4J_USERNAME, NEO4J_PASSWORD 값을 읽고 있어서 인증 실패가 발생했습니다.

  해결방안:
  docker-compose.yml에서 백엔드 컨테이너가 Neo4j 컨테이너와 같은 계정 정보를 쓰도록 명시했습니다.

  environment:
    NEO4J_URI: bolt://neo4j:7687
    NEO4J_USERNAME: neo4j
    NEO4J_PASSWORD: ${NEO4J_PASSWORD:-vibegraph}

  그 다음 backend 컨테이너를 recreate해서 새 환경변수를 반영했습니다.

  검증 결과:
  Neo4j를 사용하는 API인 /analysis/user_default 호출이 이제 200 OK로 응답합니다.

  {
    "topArtists": [],
    "topGenres": [],
    "detectedTaste": ["Eclectic Mix"],
    "moodTags": ["Neutral"]
  }

4. 문제:
  백엔드가 플레이리스트 곡 수를 attributes.trackCount에서만 읽고 있었습니다.

  그런데 Apple Music 라이브러리 플레이리스트 응답에서는 곡 수가 항상 attributes.trackCount에 들어오지 않을 수 있습니다. 곡 수 정보가 없으면 기존 코드가
  기본값 0을 넣어서, 실제로 곡이 있어도 프론트에는 전부 0곡으로 표시됐습니다.

  해결방안:
  백엔드 파서를 더 견고하게 바꿨습니다.

  이제 순서대로 확인합니다:

  attributes.trackCount
  relationships.tracks.meta.total
  relationships.tracks.data.length

  그래도 곡 수를 알 수 없으면 0이 아니라 null을 내려보냅니다.

  프론트도 수정해서 null일 때는 잘못된 0곡 대신:

  곡 수 확인 필요로 표시하게 했습니다.

  반영 상태:
  백엔드/프론트 컨테이너 둘 다 재빌드해서 실행 중 앱에 반영했습니다.

  참고로 곡 수가 계속 곡 수 확인 필요로 뜬다면, Apple Music의 /me/library/playlists 목록 API가 해당 필드를 안 주는 케이스입니다. 이 경우엔 각 플레이리
  스트의 /tracks를 따로 조회해서 개수를 세는 방식으로 바꿔야 정확합니다.

5. 문제:
  Apple Music의 /me/library/playlists 목록 응답에 곡 수가 안 들어오는 경우가 있어서, 프론트에 0곡 또는 곡 수 확인 필요로 보였습니다.

  해결방안:
  백엔드에서 플레이리스트 목록을 가져온 뒤, 곡 수가 없는 플레이리스트만 추가로 조회하게 바꿨습니다.

  동작 방식:

  1. /me/library/playlists 호출
  2. trackCount가 있으면 그대로 사용
  3. trackCount가 없으면 /me/library/playlists/{playlist_id}/tracks 호출
  4. tracks 응답 개수를 세서 trackCount로 채움
  5. 100곡 초과 플레이리스트는 next 페이지까지 따라가며 전체 개수 계산

  반영 상태:
  백엔드 컨테이너 재빌드/재시작 완료했습니다.

  이제 새로고침하면 플레이리스트 곡 수가 실제 트랙 수 기준으로 표시되어야 합니다.

6. 문제:
  Apple Music API error: 429는 Apple Music API 요청을 너무 많이/빠르게 보내서 rate limit에 걸린 것입니다.

  방금 곡 수를 정확히 세기 위해 플레이리스트별 /tracks를 병렬 조회하도록 바꿨는데, 플레이리스트가 많으면 요청이 한꺼번에 몰릴 수 있었습니다.

  해결방안:
  백엔드에 rate limit 대응을 추가했습니다.

  변경 내용:

  - 플레이리스트 곡 수 조회 동시 요청 수를 최대 3개로 제한
  - Apple Music이 429를 반환하면 재시도
  - Retry-After 헤더가 있으면 그 시간만큼 대기
  - 일부 플레이리스트 count 조회가 실패해도 전체 /apple/playlists 요청은 실패하지 않게 처리

  반영 상태:

  - backend/app/services/apple_music_service.py 수정
  - 문법 검사 통과
  - 백엔드 컨테이너 재빌드/재시작 완료

  이제 다시 새로고침해보면 429가 훨씬 줄어들고, 일부 count 조회가 제한에 걸리더라도 플레이리스트 목록 자체는 뜰 겁니다