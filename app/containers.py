from asyncio import Semaphore

import chromadb
import redis
import tiktoken
from core import ChromaClient, Logger
from core.config import Settings
from dependency_injector import containers, providers
from openai import AsyncOpenAI
from services import (
    ChatSessionService,
    EmbeddingService,
    OpenAIClient,
    RetrievalService,
    RewriterService,
    prompt_builder,
)
from utils import RejectFilter


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the application.
    This container provides instances of various services used in the application.
    """

    config = providers.Singleton(Settings)

    semaphore = providers.Singleton(Semaphore, config.provided.EMBEDDING_CONCURRENCY)

    GPT_CLIENT = providers.Singleton(AsyncOpenAI, api_key=config.provided.OPENAI_API_KEY)

    ENCODING = providers.Singleton(tiktoken.encoding_for_model, model_name=config.provided.EMBEDDING_MODEL)

    redis_client = providers.Singleton(
        redis.Redis,
        host=config.provided.REDIS_HOST,
        port=config.provided.REDIS_PORT,
        db=config.provided.REDIS_DB,
    )

    chromadb_client = providers.Singleton(
        chromadb.PersistentClient,
        path=config.provided.CHROMA_DIR,
    )

    retriever = providers.Factory(RetrievalService, reranking_model=config.provided.RERANKING_MODEL)

    embedding_service = providers.Factory(
        EmbeddingService,
        client=GPT_CLIENT,
        encoding=ENCODING,
        chunk_size=config.provided.CHUNK_SIZE,
        embedding_model=config.provided.EMBEDDING_MODEL,
        max_tokens=config.provided.MAX_TOKENS,
        semaphore=semaphore,
    )

    chat_session_service = providers.Factory(
        ChatSessionService,
        redis_client=redis_client,
        session_key_prefix=config.provided.SESSION_KEY_PREFIX,
        max_session_length=config.provided.MAX_SESSION_LENGTH,
    )
    rewriter = providers.Factory(RewriterService, client=GPT_CLIENT)

    OpenAIClient = providers.Factory(OpenAIClient, client=GPT_CLIENT)

    prompt_builder = providers.Factory(prompt_builder)

    logger = providers.Factory(Logger, log_path=config.provided.LOG_PATH)

    chroma_client = providers.Singleton(
        ChromaClient,
        chroma_client=chromadb_client,
        title_collection_name=config.provided.TITLE_COLLECTION_NAME,
        full_collection_name=config.provided.FULL_COLLECTION_NAME,
    )

    RejectFilter = providers.Factory(RejectFilter)
