
import torch
import asyncio
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from core.config import RERANKING_MODEL

# CrossEncoder 로드
reranker = CrossEncoder(
    RERANKING_MODEL, 
    device="cuda" if torch.cuda.is_available() else "cpu"
    )

loop = asyncio.get_event_loop()

_bm25 = None
_corpus = None
_all_docs = None

def _init_bm25(full_collection):
    """
    Initialize BM25 with the corpus.
    """
    global _bm25, _corpus, _all_docs
    if _bm25 is None:
        resp = full_collection.get()
        _all_docs = resp["documents"]
        _corpus = [doc.split() for doc in _all_docs]
        _bm25 = BM25Okapi(_corpus)

async def retrieve_context(query: str, collections: list, top_k: int = 10, top_n: int = 5) -> str:
    """
    Retrieve and rerank relevant context from Chroma collection using a reranker.

    Args:
        query (str): The user's input question.
        collection: Chroma vector DB collection.
        top_k (int): Number of documents to retrieve initially.
        top_n (int): Number of top documents to return after reranking.

    Returns:
        str: Concatenated top_n document texts.
    """
    from . import get_all_embeddings_async
    
    _init_bm25(collections[1])  # Initialize BM25 with the full collection

    # 임베딩으로 top_k 문서 검색
    q_embedding = (await get_all_embeddings_async([query]))[0]
    results = collections[0].query(query_embeddings=[q_embedding], n_results=top_k//2)
    matched_ids = results["ids"][0]  # List[str]
    sem_docs = collections[1].get(ids=matched_ids)["documents"]

    # 1. BM25로 검색
    tokemized_query = query.split()
    bm25_scores = _bm25.get_scores(tokemized_query)
    top_indices = np.argsort(bm25_scores)[-top_k:][::-1]
    bm25_docs = [_all_docs[i] for i in top_indices]
    if not bm25_docs:
        return "No relevant documents found."
    
    combined = []
    for doc in bm25_docs + sem_docs:
        if doc not in combined:
            combined.append(doc)
        if not combined:
            return "No relevant documents found."
    
    # 3. CrossEncoder로 리랭킹킹
    query_doc_pairs = [(query, doc) for doc in combined]
    scores = await loop.run_in_executor(None, reranker.predict, query_doc_pairs)

    # 4. 유사도 기준 상위 top_n 문서 선택
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
    top_docs = [combined[i] for i in top_indices]

    # 5. 최종 문맥 반환
    return "\n\n".join(top_docs)

