import asyncio

import numpy as np
import tiktoken  # 토큰 계산을 위한 모듈
from tqdm.asyncio import tqdm_asyncio


class EmbeddingService:
    """
    EmbeddingService는 텍스트 임베딩을 비동기로 처리하는 서비스입니다.
    주어진 텍스트를 토큰 단위로 분할하고, 각 청크를 임베딩하여 평균 벡터를 반환합니다.
    """

    def __init__(self, client, encoding, chunk_size, embedding_model, max_tokens, semaphore=None):
        self.semaphore = semaphore
        self.encoding = encoding
        self.chunk_size = chunk_size
        self.embedding_model = embedding_model
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model(embedding_model)
        self.client = client  # 비동기 클라이언트

    # 텍스트의 토큰 수 계산
    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    # 텍스트를 토큰 기준으로 안전하게 분할
    def split_text_into_chunks(self, text: str, chunk_token_limit: int) -> list[str]:
        tokens = self.encoding.encode(text)
        return [
            self.encoding.decode(tokens[i : i + chunk_token_limit]) for i in range(0, len(tokens), chunk_token_limit)
        ]

    # 벡터 정규화
    def normalize_vector(self, vec: list[float]) -> list[float]:
        norm = np.linalg.norm(vec)
        return (np.array(vec) / norm).tolist() if norm != 0 else vec

    # 개별 텍스트 또는 분할된 청크들을 비동기로 임베딩
    async def get_embedding_with_chunking(self, text: str, max_retries: int = 3, timeout: int = 10) -> list[float]:
        if self.count_tokens(text) <= self.max_tokens:
            embedding = await self.get_embedding(text, max_retries, timeout)
            return embedding

        # 청크 분할 후 각 청크 임베딩 → 평균 벡터 반환
        chunks = self.split_text_into_chunks(text, self.chunk_size)
        chunk_embeddings = await asyncio.gather(*[self.get_embedding(chunk, max_retries, timeout) for chunk in chunks])
        valid_embeddings = [e for e in chunk_embeddings if e]
        if not valid_embeddings:
            return []
        return list(np.mean(valid_embeddings, axis=0))

    # 기본 임베딩 함수
    async def get_embedding(
        self,
        text: str,
        max_retries: int = 3,
        timeout: int = 10,
    ) -> list[float]:
        for attempt in range(1, max_retries + 1):
            try:
                print(text)
                async with self.semaphore:
                    response = await asyncio.wait_for(
                        self.client.embeddings.create(input=text, model=self.embedding_model),
                        timeout=timeout,
                    )
                    return self.normalize_vector(response.data[0].embedding)
            except asyncio.TimeoutError:
                print(f"[Timeout] {attempt}/{max_retries}회차 - '{text[:30]}...'")
            except Exception as e:
                print(f"[Exception] {attempt}/{max_retries}회차 - '{text[:30]}...': {e}")
            await asyncio.sleep(2**attempt)
        return []

    # 전체 텍스트 리스트에 대해 비동기 임베딩 실행
    async def get_all_embeddings_async(self, text_list: list[str]) -> list[list[float]]:
        tasks = [self.get_embedding_with_chunking(text) for text in text_list]
        results = []

        for future in tqdm_asyncio.as_completed(tasks, total=len(tasks), desc="Embedding"):
            try:
                result = await future
                results.append(result)
            except Exception as e:
                print(f"[Unexpected Error] {e}")
                results.append([])
        return results


# EmbeddingService 클래스는 텍스트 임베딩을 비동기로 처리하며, 청크 단위로 분할하여 평균 벡터를 반환합니다.
# 이 클래스는 토큰 수 계산, 텍스트 분할, 벡터 정규화, 개별 청크 임베딩, 전체 텍스트 리스트 임베딩 기능을 제공합니다.
# 비동기 클라이언트와 세마포어를 사용하여 동시성을 유지하며, 오류 발생 시 재시도 로직을 포함합니다.
# 이 서비스는 대규모 텍스트 데이터의 임베딩을 효율적으로 처리할 수 있도록 설계되었습니다.
# 사용자는 이 클래스를 통해 텍스트 임베딩을 간편하게 수행할 수 있습니다.
## 사용 예시:
# embedding_service = EmbeddingService()
# text = "여기에 임베딩할 텍스트를 입력하세요."
# embedding = await embedding_service.get_embedding_with_chunking(text)
# print(embedding)  # 임베딩 벡터 출력
