# Naver SmartStore FAQ ChatBot API

스마트스토어 FAQ 문서를 기반으로 질의응답이 가능한 **RAG 기반 챗봇 API**입니다.  
FastAPI로 구성되어 있으며, 의미 기반 검색과 OpenAI 모델을 활용한 답변 생성을 지원합니다.


## 주요 기능

- 사용자 질문에 대한 자연스러운 응답 생성
- 스마트스토어 FAQ 문서를 기반으로 RAG(Retrieval-Augmented Generation) 적용
- 유사 질문 검색 기능 (`Chroma + text-embedding-3-small`)
- 하이브리드 검색 방식 지원
- OpenAI API 기반 응답 생성
- 질의응답 로그 저장 기능
- 질문 재기술 기능


## 기술 스택

- Python 3.10+
- FastAPI
- ChromaDB
- Redis
- OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`)
- Streamlit (클라이언트 UI)
- Uvicorn (서버 실행)
- uv (패키지/환경 관리)
- ruff, black, isort (코드 스타일 자동화)
- dependency_injector


## 검색 구조 (Retrieval Architecture)

이 프로젝트는 RAG 기반 질의응답 시스템으로, 다음과 같은 검색 구조를 사용합니다:

1. **Query Rewriting**  
   - 질문 적합성 판단
   - 응답 친화적 문장으로 질문 재구성

2. **BM25**  
   - 전통적인 키워드 기반 검색
   - FAQ 텍스트에서 초기 후보군 n개 추출

3. **Bi-Encoder**   
   - 문장 임베딩 기반 Dense Vector 검색
   - 사용자 쿼리와 문서 간의 의미 유사도 계산
   - 빠른 벡터 검색을 위해 ChromaDB 사용

4. **Cross-Encoder**  
   - 상위 후보군 문서에 대해 정밀한 쿼리-문서 재평가
   - 의미적 정확도를 높이기 위해 최종 reranking 수행

> 전체 파이프라인:
> **사용자 질문 → 질문 재기술 → [BM25 or Bi-Encoder] → 후보군 상위 N개 → Cross-Encoder rerank → GPT 응답 생성**

## 모듈 구조
```bash
my_rag_chatbot/
├── app/
│   ├── run.py                   # FastAPI 엔트리포인트
│   ├── containers.py            # DI 컨테이너 모듈
│   ├── api/
│   │   ├── ask.py               # 질의응답 API 핸들러
│   │   └── logs.py              # 로그 저장 핸들러
│   ├── chroma_db                # 벡터 DB 저장 디렉토리
│   ├── services/
│   │   ├── prompting/
│   │   ├── └── prompt_builder.py
│   │   ├── __init__.py          # 패키지 초기화 파일
│   │   ├── embedding.py         # 임베딩 처리
│   │   ├── retrieval.py         # 유사도 검색 로직 (BM25, Bi-Encoder, Cross-Encoder)
│   │   ├── rewriter.py          # 질문 검증 후 질문 재기술(생성성)
│   │   ├── generator.py         # GPT 응답 생성기
│   │   ├── chat_session.py           # 대화 내용 저장
│   │   └── logger.py            # 로그 기록 모듈
│   ├── core/
│   │   ├── __init__.py          # 패키지 초기화 파일
│   │   ├── config.py            # 설정값 불러오기 (.env)
│   │   └── chroma_client.py     # ChromaDB 클라이언트
│   ├── docs/
│   │   └── *.pkl                # FAQ 데이터 파일
│   ├── models/
│   │   ├── __init__.py          # 패키지 초기화 파일
│   │   └── schemas.py           # Pydantic 스키마 정의
│   ├── utils/
│   │   ├── templates/     
│   │   ├──├── rewrite_prompt.txt  # 재기술 프롬프트 템플릿 
│   │   ├──└── system_prompt.py    # 생성 프롬프트 템플릿 
│   │   ├── __init__.py            # 패키지 초기화 파일
│   │   ├── reject_filters.py      # 질의 히스토리 저장 필터
│   │   └── reject_phrases.txt     # 필터 응답 모음 
│   └── example_docs/
│       └── faq.txt              # 스마트스토어 FAQ 문서
├── chat_log.csv                 # 질의응답 로그 저장 파일
├── requirements.txt
└── README.md
```

## Structured Output API
```bash
본 프로젝트의 답변/질문 생성 파이프라인은 OpenAI Function Calling (Structured Output)을 활용하여
- 답변
- 유도질문(follow-up question)

을 동시에 JSON 구조로 안정적으로 출력합니다.

예)
```json
{
  "answer": "네이버 스마트스토어 환불 정책은 ...",
  "follow_up": "다른 주문에 대해서도 환불을 원하시나요?"
}

이 방식을 통해 파싱 오류를 줄이고, 프론트엔드/후처리에서 손쉽게 후속 질문을 다룰 수 있도록 설계했습니다.
```
## Dependency Injection (DI) Architecture
dependency_injector를 사용해 서비스 간 결합도를 낮추고, 유지보수성과 테스트 용이성을 높였습니다. 주요 의존성은 Container 클래스를 통해 선언적으로 주입되며, FastAPI 또는 다른 앱 코드에서 쉽게 주입받을 수 있도록 설계되었습니다.

### 주요 DI 구조
- config: 환경 설정(Settings) 객체를 싱글턴으로 제공합니다.

- semaphore: 임베딩 동시성 제어용 asyncio 세마포어

- GPT_CLIENT: OpenAI Async 클라이언트

- ENCODING: 모델별 토크나이저

- redis_client: 세션 관리용 Redis 클라이언트

- chromadb_client: ChromaDB Persistent Client

- retriever: RAG 기반 재검색 서비스

- embedding_service: GPT 기반 임베딩 벡터 생성 서비스

- chat_session_service: Redis 세션 관리 서비스

- rewriter: 답변 리라이터

- OpenAIClient: GPT API 래퍼

- prompt_builder: 프롬프트 빌더

- logger: 로그 관리 서비스

- chroma_client: 벡터스토어를 이용한 검색/저장

- RejectFilter: 유해 메시지 필터링

## Code Quality & Linting
- ruff: 빠르고 효율적인 린터로, PEP8을 기반으로 코드의 문법적 오류나 스타일 위반을 감지합니다.

- black: 코드 자동 포매터. 일관된 코드 스타일을 유지합니다.

- isort: import 순서를 정리하여 가독성을 높입니다.
```bash
# 스타일 체크
ruff check . --fix

# 코드 자동 포매팅
black .

# import 정리
isort .

```

## Continuous Integration (CI)
- CI환경
   - GitHub Actions(or GitLab CI 등)를 사용하여 push/pull request 시 자동으로

      - 의존성 설치

      - 테스트 실행

      - 코드 스타일 검사

   - 를 수행하도록 구성되어 있습니다.
- .github/workflows/lint.yml
```bach

name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv pip install --system -r requirements.txt
      - name: Install ruff
        run: uv pip install --system ruff
      - name: Run ruff
        run: ruff check . --unsafe-fixes --fix
      - name: Install black
        run: uv pip install --system black
      - name: Run black
        run: black .
      - name: Install isort
        run: uv pip install --system isort
      - name: Run isort
        run: isort . 
```

## 설치 방법
### 1. 저장소 클론
```bash
git clone https://github.com/<YOUR_ID>/Naver-SmartStore-FAQ-ChatBot.git
cd Naver-SmartStore-FAQ-ChatBot
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 필수 디렉토리 생성
```bash
mkdir -p app/chroma_db
mkdir -p app/docs
```

### 4. FAQ 데이터 파일 준비
```bash
# 파일을 app/docs/final_result.pkl 위치에 넣어주세요:
app/
└── docs/
    └── final_result.pkl
```

### 5. OpenAI API 키 설정
```bash
# app/ 디렉토리 안에 .env 파일을 만들고 아래처럼 작성하세요. 
# ※실제 키는 OpenAI에서 발급받아야 합니다.
OPENAI_API_KEY=your_openai_api_key_here
```

### 6. API 서버 실행
```bash
cd app
uvicorn run:app --reload
```

### 7. 프론트엔드 실행 (Streamlit)
```bash
cd ../frontend
streamlit run streamlit_app.py
```

### 8. redis 서버 실행
```bash
redis-server
```