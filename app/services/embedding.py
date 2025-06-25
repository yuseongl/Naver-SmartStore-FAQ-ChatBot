import asyncio
import numpy as np
from tqdm.asyncio import tqdm_asyncio
from asyncio import Semaphore
from core.config import MAX_TOKENS, CHUNK_SIZE, ENBEDDING_MODEL

import tiktoken  # 토큰 계산을 위한 모듈

# 비동기 클라이언트 및 설정
semaphore = Semaphore(5)

ENCODING = tiktoken.encoding_for_model(ENBEDDING_MODEL)

# 텍스트의 토큰 수 계산
def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))

# 텍스트를 토큰 기준으로 안전하게 분할
def split_text_into_chunks(text: str, chunk_token_limit: int = CHUNK_SIZE) -> list[str]:
    tokens = ENCODING.encode(text)
    return [ENCODING.decode(tokens[i:i + chunk_token_limit]) for i in range(0, len(tokens), chunk_token_limit)]

# 벡터 정규화
def normalize_vector(vec: list[float]) -> list[float]:
    norm = np.linalg.norm(vec)
    return (np.array(vec) / norm).tolist() if norm != 0 else vec

# 개별 텍스트 또는 분할된 청크들을 비동기로 임베딩
async def get_embedding_with_chunking(text: str, max_retries: int = 3, timeout: int = 10) -> list[float]:
    if count_tokens(text) <= MAX_TOKENS:
        return await get_embedding(text, max_retries, timeout)

    # 청크 분할 후 각 청크 임베딩 → 평균 벡터 반환
    chunks = split_text_into_chunks(text)
    chunk_embeddings = await asyncio.gather(
        *[get_embedding(chunk, max_retries, timeout) for chunk in chunks]
    )
    valid_embeddings = [e for e in chunk_embeddings if e]
    if not valid_embeddings:
        return []

    return list(np.mean(valid_embeddings, axis=0))

# 기본 임베딩 함수
async def get_embedding(text: str, max_retries: int = 3, timeout: int = 10) -> list[float]:
    from api.ask import client
    for attempt in range(1, max_retries + 1):
        try:
            print(text)
            async with semaphore:
                response = await asyncio.wait_for(
                    client.embeddings.create(
                        input=text,
                        model=ENBEDDING_MODEL
                    ),
                    timeout=timeout
                )
                return normalize_vector(response.data[0].embedding)
        except asyncio.TimeoutError:
            print(f"[Timeout] {attempt}/{max_retries}회차 - '{text[:30]}...'")
        except Exception as e:
            print(f"[Exception] {attempt}/{max_retries}회차 - '{text[:30]}...': {e}")
        await asyncio.sleep(2 ** attempt)
    return []

# 전체 텍스트 리스트에 대해 비동기 임베딩 실행
async def get_all_embeddings_async(text_list: list[str]) -> list[list[float]]:
    tasks = [get_embedding_with_chunking(text) for text in text_list]
    results = []

    for future in tqdm_asyncio.as_completed(tasks, total=len(tasks), desc="Embedding"):
        try:
            result = await future
            results.append(result)
        except Exception as e:
            print(f"[Unexpected Error] {e}")
            results.append([])
    return results
