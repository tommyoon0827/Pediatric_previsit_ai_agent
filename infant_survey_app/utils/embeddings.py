
from typing import Optional
def get_embeddings(provider: str = "openai", model: Optional[str] = None):
    provider = (provider or "openai").lower()
    if provider == "openai":
        # OpenAI의 유료 모델 사용 (성능 좋음)
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=model or "text-embedding-3-small")
    elif provider in ("hf", "huggingface"):
        # 무료 모델 (내 컴퓨터 성능 사용)
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=model or "sentence-transformers/all-MiniLM-L6-v2")
    else:
        raise ValueError(f"Unknown embeddings provider: {provider}")
