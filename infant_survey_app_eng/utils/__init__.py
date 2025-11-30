
try:
    # Relative import (.splitters)
    from .splitters import get_text_splitter
    from .embeddings import get_embeddings
    from .vectorstore import get_vectorstore, ensure_faiss_index
    from .rag import build_rag_chain
except ImportError:
    # Absolute import (for testing)
    from splitters import get_text_splitter
    from embeddings import get_embeddings
    from vectorstore import get_vectorstore, ensure_faiss_index
    from rag import build_rag_chain
