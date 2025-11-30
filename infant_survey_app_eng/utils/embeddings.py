
from typing import Optional
def get_embeddings(provider: str = "openai", model: Optional[str] = None):
    provider = (provider or "openai").lower()
    if provider == "openai":
        # Use OpenAI's paid model (High performance)
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=model or "text-embedding-3-small")
    elif provider in ("hf", "huggingface"):
        # Free model (Uses local computer resources)
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=model or "sentence-transformers/all-MiniLM-L6-v2")
    else:
        raise ValueError(f"Unknown embeddings provider: {provider}")
