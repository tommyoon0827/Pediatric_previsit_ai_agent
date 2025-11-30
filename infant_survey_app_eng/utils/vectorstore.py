
from typing import List, Optional
from pathlib import Path

def get_vectorstore(texts: List[str], metadatas: Optional[List[dict]] = None,
                    embeddings=None, index_dir: Optional[str] = None):
    try:
        from langchain_community.vectorstores import FAISS
    except ImportError:
        from langchain.vectorstores import FAISS

    # Load existing index if available (Saves time)
    if index_dir and Path(index_dir, "index.faiss").exists():
        return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)

    # Create new if not exists
    vs = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
    if index_dir:
        Path(index_dir).mkdir(parents=True, exist_ok=True)
        vs.save_local(index_dir) # Save to disk
    return vs

def ensure_faiss_index(docs: List[str], metas: Optional[List[dict]] = None,
                       index_dir: str = "storage/faiss/previsit", embeddings=None):
    return get_vectorstore(docs, metas, embeddings, index_dir=index_dir)
