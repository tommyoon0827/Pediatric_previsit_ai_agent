
from typing import Optional, List

def build_rag_chain(vs, llm=None, k: int = 4):
    # LLM이 없으면 기본적으로 GPT-4o-mini를 사용하도록 설정
    if llm is None:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    def ask(query: str) -> dict:
        # 1. 질문과 유사한 문서 4개(k=4)를 찾습니다.
        docs = vs.similarity_search(query, k=k)
        # 2. 찾은 문서 내용을 하나의 텍스트로 합칩니다.
        context = "\n\n".join([d.page_content for d in docs])

        # 3. 프롬프트를 구성합니다. (컨텍스트 + 질문)
        prompt = f"""당신은 소아과 문진 보조 에이전트입니다.
        아래의 컨텍스트를 근거로 사용자 질문에 친절하게 한국어로 답변하세요.

        [컨텍스트]
        {context}

        [질문]
        {query}
        """
        # 4. AI에게 답변을 요청합니다.
        resp = llm.invoke(prompt)

        # 5. 결과 반환 (답변 + 근거 문서)
        return {
            "answer": resp.content if hasattr(resp, "content") else str(resp),
            "context_snippets": [d.page_content[:500] for d in docs]
        }
    return ask
