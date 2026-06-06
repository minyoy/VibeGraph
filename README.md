# VibeGraph

Apple Music 청취 데이터를 기반으로 그래프 DB(Neo4j)에 취향 네트워크를 구성하고, LLM으로 개인화된 음악을 추천하는 프로토타입 프로젝트.

```
[Apple Music API] → [FastAPI Backend] → [Neo4j Graph DB] → [LLM Agent] → [추천 플레이리스트]
```

이 저장소는 기능 구현 외에 **"설계 문서를 LLM 프롬프트에 넣으면 생성 코드 품질이 달라지는가"** 를 검증하는 실험을 겸한다.

---

## 프로젝트 구조

```
VibeGraph/
├── prompt-only/       # 프롬프트만으로 생성
│   ├── backend/       # FastAPI + Neo4j + OpenAI
│   └── frontend/      # React (Vite)
├── process-guided/    # 프롬프트 + 설계 문서(docs/01~08) 제공
│   ├── backend/
│   └── frontend/
└── docs/              # 실험에 사용된 설계 문서
    ├── 01_requirements.md
    ├── 02_usecase.puml
    ├── 03_activity.puml
    ├── 04_domain-model.puml
    ├── 05_sequence-recommendation.puml
    ├── 06_api-spec.md
    ├── 07_test-checklist.md
    └── 08_lessons-learned.md
```

---

## 실험 개요

| 항목 | prompt-only (baseline) | process-guided (v2) |
|------|------------------------|---------------------|
| 생성 조건 | 기능 설명 프롬프트만 제공 | 동일 프롬프트 + docs/01~08 전체 제공 |
| 목적 | 대조군 | 설계 문서 효과 측정 |
| 스택 | FastAPI · Neo4j · OpenAI · React | 동일 |

---

## 실험 결과: prompt-only vs process-guided 비교

### 1. 설계 문서가 영향을 준 항목

문서를 제공했을 때 process-guided에서 뚜렷하게 달라진 부분은 **문서에 명시된 내용과 직접 대응한다.**

#### 프론트엔드 상태 머신

`03_activity.puml`과 `08_lessons-learned.md`에 상태 전이가 명시되어 있었고, process-guided Dashboard는 이를 그대로 구현했다.

```jsx
// process-guided/frontend — 문서에 기술된 상태 흐름을 코드로 직접 반영
const [appState, setAppState] = useState('disconnected')
// disconnected → connected → playlistSelected
// → synced → analyzed → recommended → explained → created
```

prompt-only는 토큰 유무만으로 상태를 구분하며 중간 단계가 없다.

#### 에러 상태 코드 분리

`08_lessons-learned.md` 섹션 5.1에 에러 코드가 명시됐고, process-guided 에러 클래스가 이를 따랐다.

| 에러 | 문서 명세 | prompt-only | process-guided |
|------|-----------|-------------|----------------|
| 인증 실패 | 401 | 401 ✓ | 401 ✓ |
| Apple Music API | 502 | 502 ✓ | 502 ✓ |
| Neo4j 연결 | 503 | 503 ✓ | 503 ✓ |
| 추천 없음 | 404 | 미구현 | 404 ✓ |

`NoRecommendationsError`는 문서에만 있던 항목으로 process-guided에서만 구현됐다.

#### 서비스 계층 책임 분리 (SRP)

`04_domain-model.puml`이 도메인 개념(Track, Artist, Genre, Playlist)을 명확히 분리했고, `05_sequence.puml`이 추천 흐름의 호출 경계를 그렸다. process-guided는 이에 맞춰 취향/무드 감지 로직을 `Neo4jService`에서 `analysis_service.py`로 분리했다.

```python
# prompt-only — Neo4jService가 DB + 도메인 규칙을 모두 담당
class Neo4jService:
    def _detect_taste(self, genres): ...   # 도메인 규칙이 DB 서비스 안에
    def _detect_moods(self, genres): ...

# process-guided — 도메인 규칙을 별도 모듈로 분리 (시퀀스 다이어그램의 경계 반영)
# analysis_service.py
TASTE_MAP = {"hip-hop": "urban", "r-n-b": "urban", ...}
MOOD_MAP  = {"electronic": "energetic", "jazz": "chill", ...}
```

#### LLM 응답 폴백 처리

`07_test-checklist.md`에 "LLM 응답 누락 시 처리"가 테스트 항목으로 있었고, process-guided만 폴백을 구현했다.

```python
# process-guided만 존재 — 체크리스트 항목이 구현으로 이어진 사례
if not track.get("reason") and i < len(candidates):
    track["reason"] = f"Recommended via graph path: {candidates[i]['graphPath']}"
```

#### API 필드명 일관성

`06_api-spec.md`가 요청/응답 계약을 명시했고, process-guided는 Pydantic 스키마에서 타입을 더 엄격하게 정의했다. prompt-only에서 `Optional[str]`이던 필드들이 process-guided에서 `str`(required)로 바뀐 것이 그 결과다.

---

### 2. 설계 문서가 영향을 주지 못한 항목

문서가 **"무엇을 만들어야 하는가"는 전달했지만 "어떻게 구현해야 하는가"는 기술하지 않은** 영역에서는 개선이 없거나 오히려 단순화됐다.

#### 의존성 역전 (DIP)

두 버전 모두 미달. 문서는 컴포넌트 간 관계를 다이어그램으로 표현했지만 의존성 주입 방식은 명세하지 않았다. 결과적으로 process-guided는 전역 싱글톤을 선택했고 이는 테스트 가능성 측면에서 prompt-only보다 후퇴다.

```python
# prompt-only — 클래스 구조라 생성자 주입으로 개선 여지 있음
class AnalysisService:
    def __init__(self):
        self.neo4j = Neo4jService()

# process-guided — 전역 싱글톤, 테스트 시 교체 불가
settings = Settings()
```

#### 재시도/복원력 (Resilience)

`07_test-checklist.md`에 외부 API 실패 항목은 있었지만 재시도 전략은 명세하지 않았다. process-guided는 재시도 로직을 제거했다. Docker 환경에서 인프라 레벨 재시도를 전제한 의도적 단순화로 보이지만, 그 전제가 코드에 명시되지 않아 판단 근거가 없다.

#### Neo4j 쿼리 최적화

`04_domain-model.puml`이 그래프 구조를 정의했지만 쿼리 전략은 다루지 않았다. process-guided는 복합 쿼리를 6개의 개별 쿼리로 분해했고 이는 DB 호출 비용을 증가시킨다. Docker 내부 네트워크에서는 라운드트립 비용이 작아 체감 차이는 크지 않을 수 있다.

---

### 3. 전체 비교

| 관점 | prompt-only | process-guided | 문서 기여 여부 |
|------|-------------|----------------|----------------|
| 프론트엔드 상태 머신 | 없음 | 명시적 8단계 | ✓ activity.puml 직접 반영 |
| 에러 코드 분리 | 3종 | 4종 (NoRecommendations 추가) | ✓ lessons-learned 반영 |
| SRP (서비스 계층) | 미흡 | 개선 | ✓ sequence/domain 다이어그램 반영 |
| LLM 폴백 처리 | 없음 | 있음 | ✓ test-checklist 반영 |
| API 타입 엄격성 | Optional 다수 | Required 위주 | ✓ api-spec 반영 |
| DIP | 미흡 | 더 미흡 | ✗ 문서에 명세 없음 |
| 재시도 로직 | 있음 | 제거 | ✗ 문서에 전략 없음 |
| DB 쿼리 효율 | 복합 쿼리 | 다중 호출 | ✗ 문서에 명세 없음 |
| 추천 다양성 | 결정론적 | 확률적 | △ 알고리즘 개선 의도는 있으나 문서 미명세 |

---

## 결론

**설계 문서는 "명세된 것"을 코드로 옮기는 정확도를 높인다. 명세되지 않은 구현 방식은 바뀌지 않는다.**

process-guided에서 개선된 항목들은 docs/01~08에 직접 기술된 내용과 1:1로 대응한다. 반대로 문서가 다루지 않은 DIP, 재시도 전략, 쿼리 최적화는 오히려 단순화 방향으로 흘렀다.

이는 다음을 시사한다:

- 바이브코딩에서 설계 문서의 역할은 **LLM이 임의로 결정하는 영역을 줄이는 것**이다.
- 문서가 다루는 범위가 곧 품질 보장 범위다. 문서 밖의 결정은 LLM의 기본값에 맡겨진다.
- **"어떻게 구현할 것인가"(DI 방식, 쿼리 전략, 재시도 정책)까지 명세하지 않으면 구현 품질의 절반은 여전히 불확실하다.**

---

## 실행 방법

각 버전의 `prompt-only/` 또는 `process-guided/` 디렉토리 내 `.env.example` 참고.

공통 의존:
- Neo4j 4.x 이상 (bolt 프로토콜)
- Apple Music Developer Token
- OpenAI API Key
