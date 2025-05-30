# Naver SmartStore FAQ ChatBot API

스마트스토어 FAQ 문서를 기반으로 질의응답이 가능한 **RAG 기반 챗봇 API**입니다.  
FastAPI로 구성되어 있으며, 의미 기반 검색과 OpenAI 모델을 활용한 답변 생성을 지원합니다.

---

## 주요 기능

- 사용자 질문에 대한 자연스러운 응답 생성
- 스마트스토어 FAQ 문서를 기반으로 RAG(Retrieval-Augmented Generation) 적용
- 유사 질문 검색 기능 (`Chroma + text-embedding-3-small`)
- 하이브리드 검색 방식 지원
- OpenAI API 기반 응답 생성
- 질의응답 로그 저장 기능

---

## 기술 스택

- Python 3.10+
- FastAPI
- ChromaDB
- OpenAI API (`gpt-4`, `text-embedding-3-small`)
- LangChain (옵션)
- Streamlit (클라이언트 UI)
- Uvicorn (서버 실행)

---

## 검색 구조 (Retrieval Architecture)

이 프로젝트는 RAG 기반 질의응답 시스템으로, 다음과 같은 검색 구조를 사용합니다:

1. **BM25**  
   - 전통적인 키워드 기반 검색색
   - FAQ 텍스트에서 초기 후보군 n개 추출

2. **Bi-Encoder**   
   - 문장 임베딩 기반 Dense Vector 검색
   - 사용자 쿼리와 문서 간의 의미 유사도 계산
   - 빠른 벡터 검색을 위해 ChromaDB 사용

3. **Cross-Encoder**  
   - 상위 후보군 문서에 대해 정밀한 쿼리-문서 재평가
   - 의미적 정확도를 높이기 위해 최종 reranking 수행

> 전체 파이프라인:
> **사용자 질문 → [BM25 or Bi-Encoder] → 후보군 상위 N개 → Cross-Encoder rerank → GPT 응답 생성**

## 모듈 구조

my_rag_chatbot/
├── app/
│   ├── main.py                  # FastAPI 엔트리포인트
│   ├── api/
│   │   ├── ask.py               # 질의응답 API 핸들러
│   │   └── logs.py              # 로그 저장 핸들러
│   ├── services/
│   │   ├── embedding.py         # 임베딩 처리
│   │   ├── retrieval.py         # 유사도 검색 로직 (BM25, Bi-Encoder, Cross-Encoder)
│   │   ├── generator.py         # GPT 응답 생성기
│   │   └── logger.py            # 로그 기록 모듈
│   ├── core/
│   │   ├── config.py            # 설정값 불러오기 (.env)
│   │   └── chroma_client.py     # ChromaDB 클라이언트
│   ├── models/
│   │   └── schemas.py           # Pydantic 스키마 정의
│   └── example_docs/
│       └── faq.txt              # 스마트스토어 FAQ 문서
├── chroma_db/                   # 벡터 DB 저장 디렉토리
├── chat_log.csv                 # 질의응답 로그 저장 파일
├── requirements.txt
└── README.md


## 설치 방법

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows는 venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt
