import pickle
import re
import chromadb
from core.config import CHROMA_DIR, TITLE_COLLECTION_NAME, FULL_COLLECTION_NAME
from services.embedding import get_all_embeddings_async

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

title_collection = None
full_collection = None

def clean_context(text: str) -> str:
    """
    불필요한 UI 문구 ('도움말이 도움이 되었나요?'부터 '도움말 닫기'까지) 제거.
    """
    pattern = r"(위 도움말이 도움이 되었나요\?.*?도움말 닫기|별점\d점|소중한 의견.*?보내기)"
    cleaned = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
    # 특수문자 제거
    cleaned = re.sub(r'\xa0|▶|》|>|\[.*?\]', ' ', cleaned)  # 공백, 괄호 제거
    cleaned = re.sub(r'바로\s*가기|self\s*입점\s*체크|접속해\s*주세요|클릭해\s*주세요', '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # · 또는 줄바꿈 기준으로 분할
    chunks = re.split(r'·|\n', cleaned)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks

async def get_chroma_collections():
    """
    Initialize and return the title and full QA Chroma collections.
    """
    global title_collection, full_collection
    title_collection = chroma_client.get_or_create_collection(name=TITLE_COLLECTION_NAME)
    full_collection = chroma_client.get_or_create_collection(name=FULL_COLLECTION_NAME)

    if title_collection.count() == 0 or full_collection.count() == 0:
        with open("docs/final_result.pkl", "rb") as f:
            doc_text = pickle.load(f)

        qa_pairs = [
            (clean_context(q.strip()), clean_context(a.strip()))
            for q, a in doc_text.items()
            if q.strip() and a.strip()
        ]

        ids = [f"qa_{i}" for i in range(len(qa_pairs))]
        titles = [q[0] for q, _ in qa_pairs]
        full_texts = [f"Q: {q}\nA: {a}" for q, a in qa_pairs]

        title_embeddings = await get_all_embeddings_async(titles)
        full_embeddings = await get_all_embeddings_async(full_texts)

        title_collection.add(documents=titles, embeddings=title_embeddings, ids=ids)
        full_collection.add(documents=full_texts, embeddings=full_embeddings, ids=ids)

    return [title_collection, full_collection]
