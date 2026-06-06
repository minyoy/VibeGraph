# VibeGraph

Apple Music 플레이리스트 데이터를 가져와 Neo4j에 음악 취향 그래프를 만들고, LLM을 이용해 추천 플레이리스트와 추천 이유를 생성하는 프로토타입 프로젝트입니다.

```text
Apple Music API → FastAPI Backend → Neo4j Graph DB → LLM Agent → 추천 플레이리스트
```

이 프로젝트는 단순히 기능을 구현하는 것뿐 아니라, **설계 문서를 프롬프트에 함께 제공했을 때 AI가 생성한 코드가 어떻게 달라지는지** 확인하기 위한 실험도 함께 진행했습니다.

---

## 프로젝트 구조

```text
VibeGraph/
├── prompt-only/       # 기능 설명 프롬프트만으로 생성한 버전
│   ├── backend/       # FastAPI + Neo4j + OpenAI
│   └── frontend/      # React (Vite)
├── process-guided/    # 기능 설명 + 설계 문서를 함께 제공한 버전
│   ├── backend/
│   └── frontend/
└── docs/              # 실험에 사용한 요구사항, 설계, 테스트 문서
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

## 실험 방식

두 버전은 같은 기능을 목표로 만들었고, 차이는 Claude CLI에 제공한 입력이다.

| 구분 | prompt-only                   | process-guided |
| -- | ----------------------------- | -------------- |
| 입력 | 기능 설명 프롬프트                    | 기능 설명 + 설계 문서  |
| 목적 | 비교 기준                         | 프로세스 적용 효과 확인  |
| 스택 | FastAPI, React, Neo4j, OpenAI | 동일             |

prompt-only는 기능 설명만 제공해 생성했고, process-guided는 기능 설명과 함께 요구사항, 다이어그램, API 명세, 테스트 체크리스트를 제공해 생성했다. 이후 두 결과를 비교해 설계 문서가 코드 구조와 예외 처리에 어떤 영향을 주었는지 확인했다.

---

## 비교 결과

### 1. 문서에 적힌 내용은 코드에 비교적 잘 반영됨

process-guided에서 개선된 부분은 대부분 사전에 작성한 문서와 연결되어 있었다.

#### 프론트엔드 상태 관리

Activity Diagram과 Lessons Learned 문서에 서비스 진행 단계가 정리되어 있었기 때문에, process-guided에서는 화면 상태가 더 세분화되었다.

```jsx
const [appState, setAppState] = useState('disconnected')

// disconnected → connected → playlistSelected
// → synced → analyzed → recommended → explained → created
```

반면 prompt-only는 주로 토큰 유무를 기준으로 상태를 판단해, 중간 진행 단계가 명확하지 않았다.

#### 에러 처리

process-guided에서는 추천 후보가 없을 때의 예외 처리가 추가되었다.

| 에러 상황              | prompt-only | process-guided |
| ------------------ | ----------- | -------------- |
| 인증 실패              | 처리          | 처리             |
| Apple Music API 오류 | 처리          | 처리             |
| Neo4j 연결 오류        | 처리          | 처리             |
| 추천 후보 없음           | 미구현         | 구현             |

특히 `NoRecommendationsError`는 문서에 명시된 항목이 process-guided에 반영된 사례다.

#### 서비스 책임 분리

prompt-only에서는 DB 접근 로직과 취향 분석 규칙이 같은 서비스 안에 섞여 있었다. process-guided에서는 도메인 모델과 시퀀스 다이어그램의 영향으로 취향/무드 분석 로직이 별도 모듈로 분리되었다.

```python
# prompt-only
class Neo4jService:
    def _detect_taste(self, genres): ...
    def _detect_moods(self, genres): ...
```

```python
# process-guided
TASTE_MAP = {"hip-hop": "urban", "r-n-b": "urban", ...}
MOOD_MAP  = {"electronic": "energetic", "jazz": "chill", ...}
```

#### LLM 응답 누락 처리

테스트 체크리스트에 LLM 응답 누락 상황이 포함되어 있었기 때문에, process-guided에는 추천 이유가 비어 있을 때 기본 설명을 채우는 fallback 처리가 추가되었다.

```python
if not track.get("reason") and i < len(candidates):
    track["reason"] = f"Recommended via graph path: {candidates[i]['graphPath']}"
```

이 부분은 테스트 문서가 실제 예외 처리 코드로 이어진 사례로 볼 수 있다.

---

### 2. 문서에 없는 구현 전략은 자동으로 좋아지지 않음

반대로 문서에 구체적으로 작성하지 않은 부분은 process-guided에서도 충분히 개선되지 않았다.

#### 의존성 주입 방식

설계 문서에는 컴포넌트 관계는 있었지만, 의존성 주입 방식까지는 명시하지 않았다. 그 결과 process-guided에서도 테스트하기 쉬운 구조가 자동으로 만들어지지는 않았다.

#### 재시도 전략

외부 API 실패 상황은 테스트 항목에 있었지만, 몇 번 재시도할지, 어떤 조건에서 중단할지 같은 정책은 작성하지 않았다. 따라서 재시도와 복원력 측면에서는 뚜렷한 개선을 확인하기 어려웠다.

#### Neo4j 쿼리 최적화

도메인 모델은 그래프 구조를 설명했지만, 쿼리를 어떤 방식으로 최적화할지는 다루지 않았다. 이 때문에 process-guided가 항상 더 효율적인 쿼리를 생성하지는 않았다.

---

## 전체 비교

| 관점           | prompt-only | process-guided | 해석                  |
| ------------ | ----------- | -------------- | ------------------- |
| 프론트엔드 상태 관리  | 단순함         | 단계가 명확함        | Activity Diagram 영향 |
| 에러 처리        | 일부 처리       | 추천 없음 처리 추가    | 테스트/교훈 문서 영향        |
| 서비스 책임 분리    | 미흡          | 일부 개선          | Domain Model 영향     |
| LLM fallback | 없음          | 있음             | 테스트 체크리스트 영향        |
| API 타입 일관성   | 느슨함         | 더 엄격함          | API 명세 영향           |
| 의존성 주입       | 미흡          | 미흡             | 문서에 구체적 명세 없음       |
| 재시도 전략       | 일부 존재       | 충분하지 않음        | 정책 명세 부족            |
| 쿼리 최적화       | 제한적         | 제한적            | 최적화 기준 없음           |

---

## 정리

이번 실험에서 확인한 점은 단순하다.

**설계 문서는 AI가 코드를 생성할 때 참고할 기준을 만들어준다. 다만 문서에 적지 않은 품질까지 자동으로 보장해주지는 않는다.**

process-guided에서 좋아진 부분은 대부분 문서에 명시된 내용과 연결되어 있었다. 상태 흐름, 에러 처리, API 명세, 테스트 체크리스트처럼 구체적으로 적은 부분은 코드에 반영되었다. 반면 의존성 주입, 재시도 정책, 쿼리 최적화처럼 문서에 자세히 쓰지 않은 부분은 크게 개선되지 않았다.

결국 바이브코딩에서 설계 문서의 역할은 AI가 임의로 결정하는 영역을 줄이는 것이다. 더 좋은 코드를 얻으려면 “무엇을 만들 것인가”뿐만 아니라 “어떤 구조와 품질 기준으로 만들 것인가”까지 프롬프트에 포함해야 한다.

---

## 실행 방법

각 버전의 실행 환경은 `prompt-only/` 또는 `process-guided/` 디렉토리의 `.env.example`을 참고하면 된다.

공통으로 필요한 항목은 다음과 같다.

* Neo4j 4.x 이상
* Apple Music Developer Token
* OpenAI API Key
