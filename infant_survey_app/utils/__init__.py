
try:
    # 상대 경로 import (.splitters)
    from .splitters import get_text_splitter
    from .embeddings import get_embeddings
    from .vectorstore import get_vectorstore, ensure_faiss_index
    from .rag import build_rag_chain
except ImportError:
    # 절대 경로 import (테스트용)
    from splitters import get_text_splitter
    from embeddings import get_embeddings
    from vectorstore import get_vectorstore, ensure_faiss_index
    from rag import build_rag_chain
