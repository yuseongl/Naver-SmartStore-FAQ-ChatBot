from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    OPENAI_API_KEY: str
    DOC_PATH: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    # 로그 파일 경로
    LOG_PATH: str = "chat_log.csv"

    # embedding.py 관련 설정
    MAX_TOKENS: int = 8000
    CHUNK_SIZE: int = 7000
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    RERANKING_MODEL: str = "BAAI/bge-reranker-base"
    EMBEDDING_CONCURRENCY: int = 5  # 임베딩 동시 처리 수

    # chroma_client.py 관련 설정정
    TITLE_COLLECTION_NAME: str = "qa_title"
    FULL_COLLECTION_NAME: str = "qa_full"
    CHROMA_DIR: str = "chroma_db"
    EMBEDDING_CACHE_PATH: str = "docs/final_result_embedded.pkl"

    # Redis 설정
    SESSION_KEY_PREFIX: str = "chat:session:"
    MAX_SESSION_LENGTH: int = 5  # 최대 세션 길이
