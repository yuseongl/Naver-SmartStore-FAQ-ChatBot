import os

from dotenv import load_dotenv

load_dotenv()

OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPEN_AI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

# 기본 질문 응답 파일 경로
DOC_PATH = os.getenv("DOC_PATH", "chroma_db/faq.txt")

# 로그 파일 경로
LOG_PATH = "chat_log.csv"

# embedding.py 관련 설정
MAX_TOKENS = 8000
CHUNK_SIZE = 7000
ENBEDDING_MODEL = "text-embedding-3-small"
RERANKING_MODEL = "BAAI/bge-reranker-base"

# chroma_client.py 관련 설정정
TITLE_COLLECTION_NAME = "qa_title"
FULL_COLLECTION_NAME = "qa_full"
CHROMA_DIR = "chroma_db"
EMBEDDING_CACHE_PATH = "docs/final_result_embedded.pkl"

# Redis 설정
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
SESSION_KEY_PREFIX = "chat:session:"
MAX_SESSION_LENGTH = 5  # 최대 세션 길이
