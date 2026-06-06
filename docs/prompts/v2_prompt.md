너는 숙련된 풀스택 개발자야.
아래에 명시된 문서들을 모두 읽고 반영해서 VibeGraph의 1차 프로토타입을 실제 동작 가능한 서비스 형태로 구현해줘.

프로젝트 이름은 VibeGraph이다.

VibeGraph는 사용자의 Apple Music 플레이리스트 및 청취 데이터를 기반으로 음악 취향을 분석하고, Neo4j Graph Database를 활용하여 새로운 음악 추천 플레이리스트를 생성하는 AI 기반 음악 추천 시스템이다.

이번 1차 구현에서는 실제 Apple Music API, 실제 Neo4j, 실제 LLM API 연동을 목표로 한다.
단, API key, Apple developer token, user token, Neo4j URI, LLM API key 등 민감한 값은 코드에 직접 작성하지 말고 환경변수로 분리해줘.

---

# 참고 문서

아래 문서들을 모두 읽고 구현에 반영해줘.

- 요구사항 명세: `docs/01_requirements.md`
- 유스케이스 다이어그램: `docs/02_usecase.puml`
- 액티비티 다이어그램: `docs/03_activity.puml`
- 도메인 모델: `docs/04_domain-model.puml`
- 시퀀스 다이어그램: `docs/05_sequence-recommendation.puml`
- API 명세: `docs/06_api-spec.md`
- 테스트 체크리스트: `docs/07_test-checklist.md`
- 교훈 및 개선사항: `docs/08_lessons-learned.md`

---

# 최종 결과물 요구사항

1. 전체 프로젝트 폴더 구조
2. 모든 주요 파일 코드
3. Docker Compose 실행 방법
4. 필요한 환경변수 목록
5. Apple Music API, Neo4j, OpenAI API 설정 방법
6. 현재 구현의 한계와 TODO
