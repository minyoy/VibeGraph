# VibeGraph

> Graph Database 기반 개인화 음악 플레이리스트 생성 AI Agent

---

# 프로젝트 개요

VibeGraph는 사용자의 Apple Music 플레이리스트 및 청취 데이터를 기반으로 음악 취향을 분석하고, Graph Database를 활용하여 새로운 음악 추천 플레이리스트를 생성하는 AI 기반 음악 추천 시스템이다.

기존의 단순 분위기 기반 추천 시스템과 달리, VibeGraph는 실제 사용자의 음악 데이터 사이의 관계를 그래프 구조로 저장하고 탐색하여 추천 후보를 생성한다.

이후 AI Agent는 Graph DB 기반 추천 결과를 해석하고 추천 이유를 생성하며, Apple Music API를 통해 새로운 플레이리스트를 자동 생성한다.

---

# 프로젝트 목표

본 프로젝트의 목표는 다음과 같다.

* Apple Music 사용자 데이터 기반 개인화 추천 시스템 구현
* Graph Database 기반 관계 탐색 추천 시스템 설계
* AI Agent + MCP 기반 Tool Orchestration 구조 구현
* 추천 근거를 설명 가능한 형태로 제공
* 바이브코딩(Vibe Coding) 기반 개발 프로세스 분석

---

# 핵심 아이디어

VibeGraph는 단순히 LLM이 음악을 생성적으로 추천하는 방식이 아니라, Graph Database 기반 관계 탐색을 통해 추천 후보를 생성한다.

예시 관계:

```text id="8p7mg2"
사용자 → 플레이리스트 → 곡 → 아티스트 → 장르
```

이를 통해:

* 유사 아티스트 탐색
* 반복적으로 등장하는 장르 분석
* 분위기 기반 관계 탐색
* 기존 플레이리스트 패턴 분석

등이 가능하다.

---

# 주요 기능

## 1. Apple Music 연동

* Apple Music 로그인
* 사용자 플레이리스트 조회
* 최근 청취 기록 조회
* 플레이리스트 자동 생성

---

## 2. 사용자 음악 취향 분석

사용자의 플레이리스트 및 청취 데이터를 기반으로 다음 요소를 분석한다.

* 자주 듣는 아티스트
* 선호 장르
* 플레이리스트 구성 패턴
* 분위기(Mood)
* 반복적으로 등장하는 음악 관계

예시:

```text id="1exhpk"
Top Artists
- wave to earth
- Keshi
- The 1975
- NewJeans

Detected Taste
- Dream Pop
- Chill Indie
- Night Mood
- Soft Vocal
```

---

## 3. Graph Database 기반 추천 후보 생성

Neo4j 기반 Graph Database를 활용하여 사용자 음악 관계를 저장한다.

예시 구조:

```text id="2zn1oq"
(User)-[:OWNS]->(Playlist)
(Playlist)-[:CONTAINS]->(Track)
(Track)-[:BY]->(Artist)
(Track)-[:HAS_GENRE]->(Genre)
(Artist)-[:SIMILAR_TO]->(Artist)
```

Graph DB는 다음 역할을 수행한다.

* 유사 아티스트 탐색
* 장르 기반 관계 탐색
* 기존 플레이리스트와 유사한 곡 탐색
* 이미 들은 곡 제외
* 추천 후보 생성

---

## 4. AI Agent 기반 추천 해석

AI Agent는 Graph DB가 생성한 추천 후보를 기반으로:

* 추천 전략 조율
* 추천 이유 생성
* 추천 결과 정리
* 플레이리스트 이름 생성
* Apple Music 플레이리스트 생성

등을 수행한다.

즉:

* 추천 후보 생성 → Graph DB
* 추천 해석 및 자동화 → AI Agent

구조로 역할을 분리하였다.

---

## 5. Explainable Recommendation

추천 결과에 대해 설명 가능한 추천을 제공한다.

예시:

> “사용자가 자주 듣는 dream pop 계열 아티스트와 유사한 분위기를 가지며, 기존 플레이리스트에서 반복적으로 등장하는 chill indie 장르와 연결되어 추천되었습니다.”

---

# 시스템 흐름

```text id="i8qvow"
사용자 Apple Music 로그인
        ↓
플레이리스트 및 청취 데이터 수집
        ↓
Graph DB 관계 저장
        ↓
Graph 기반 추천 후보 생성
        ↓
AI Agent 추천 이유 생성 및 결과 정리
        ↓
Apple Music 플레이리스트 자동 생성
```

---

# 기술 스택

## Frontend

* React
* Tailwind CSS

## Backend

* FastAPI

## AI / Agent

* OpenAI API 또는 Claude API
* MCP 기반 Tool Orchestration

## Database

* Neo4j (Graph Database)

## External API

* Apple Music API
* MusicKit

---

# Graph Database를 사용하는 이유

음악 추천은 본질적으로 관계 탐색 문제에 가깝다.

예시:

* 사용자 ↔ 플레이리스트
* 플레이리스트 ↔ 곡
* 곡 ↔ 아티스트
* 아티스트 ↔ 장르
* 아티스트 ↔ 유사 아티스트

관계형 데이터베이스에서는 이러한 관계 탐색에 복잡한 Join 연산이 필요하다.

본 프로젝트에서는 Graph Database를 활용하여:

* 음악 관계를 직관적으로 표현하고
* 추천 경로를 효율적으로 탐색하며
* 추천 근거를 설명 가능한 형태로 제공한다.

---

# 시스템 아키텍처

```text id="n53pnq"
Frontend (React)
        ↓
Backend API (FastAPI)
        ↓
AI Agent Layer
        ↓
Neo4j Graph Database
        ↓
Apple Music API / MCP Tools
```

---

# 사용자 흐름 예시

1. 사용자가 Apple Music으로 로그인
2. 기존 플레이리스트 선택
3. 플레이리스트 곡/아티스트/장르 데이터 수집
4. Graph DB 관계 저장
5. Graph 기반 추천 후보 생성
6. AI Agent가 추천 이유 생성
7. 새로운 플레이리스트 자동 생성

---

# 데모 시나리오

## 입력

사용자가 다음 플레이리스트를 선택:

* Late Night
* Coding Playlist
* Indie Favorites

---

## 분석 결과

```text id="40f9yq"
Detected Taste
- Dream Pop
- Chill Indie
- Night Mood
- Soft Vocal
```

---

## 추천 결과

```text id="4iij8q"
Recommended Tracks
- Glue Song - beabadoobee
- seasons - wave to earth
```

---

## 결과

* 추천 이유 제공
* Apple Music 플레이리스트 자동 생성
* 새로운 플레이리스트 저장

---

# 바이브코딩(Vibe Coding) 분석 목표

본 프로젝트는 단순 구현뿐 아니라, AI 기반 개발 프로세스의 효과를 분석하는 것을 목표로 한다.

분석 항목:

* AI 생성 코드 품질
* 프롬프트 엔지니어링 효과
* API 연동 문제
* AI Hallucination 사례
* 리팩토링 필요성
* Human-AI 협업 방식
* 개발 생산성 변화

---

# 향후 확장 계획

* Spotify 연동
* YouTube Music 연동
* 실시간 추천 시스템
* 사용자 피드백 기반 추천 개선
* 그래프 기반 추천 알고리즘 고도화
* 소셜 플레이리스트 기능

---

# 프로젝트 목표 정리

VibeGraph는 Apple Music 사용자 데이터를 기반으로 Graph Database 기반 관계 탐색 추천 시스템을 구축하고, AI Agent와 MCP 기반 Tool Orchestration을 활용하여 개인화 플레이리스트를 자동 생성하는 것을 목표로 한다.

또한 바이브코딩 기반 개발 프로세스의 실제 효과와 한계를 분석하고, AI-assisted Software Engineering의 가능성을 탐구한다.
