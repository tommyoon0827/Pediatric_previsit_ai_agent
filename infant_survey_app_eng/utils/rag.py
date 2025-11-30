
from typing import Optional, List

def build_rag_chain(vs, llm=None, k: int = 4):
    # Use GPT-4o-mini by default if LLM is not provided
    if llm is None:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    def ask(query: str) -> dict:
        # 1. Find 4 similar documents (k=4).
        docs = vs.similarity_search(query, k=k)
        # 2. Combine found document contents into one text.
        context = "\\n\\n".join([d.page_content for d in docs])

        # 3. Construct the prompt (Context + Question)
        prompt = f\"\"\"You are a pediatric questionnaire assistant agent.
        Based on the context below, kindly answer the user's question in English.

        [Context]
        {context}

        [Question]
        {query}
        \"\"\"
        # 4. Request answer from AI.
        resp = llm.invoke(prompt)

        # 5. Return result (Answer + Source snippets)
        return {
            "answer": resp.content if hasattr(resp, "content") else str(resp),
            "context_snippets": [d.page_content[:500] for d in docs]
        }
    return ask
