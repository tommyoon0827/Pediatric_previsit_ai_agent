
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from utils.splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.prompts import ChatPromptTemplate
import glob, os

VS_DIR = "data/vectorstore"
DOC_DIR = "data/docs"

SYSTEM = """
You are a pediatric guide assistant. Answer accurately and concisely in English based on the provided documents.
Do not infer information not present in the documents; prioritize general safety rules and recommendations to visit a hospital.
"""

QA_TMPL = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "Question: {question}\nReference:\n{context}\nAnswer based on the reference.")
])

def ensure_vectorstore():
    os.makedirs(VS_DIR, exist_ok=True)
    if not os.listdir(VS_DIR):
        docs = []
        for p in glob.glob(os.path.join(DOC_DIR, "**/*"), recursive=True):
            try:
                lp = p.lower()
                if lp.endswith(".pdf"): docs.extend(PyPDFLoader(p).load())
                elif lp.endswith(".docx"): docs.extend(Docx2txtLoader(p).load())
                elif lp.endswith(".txt"): docs.extend(TextLoader(p, encoding="utf-8").load())
            except Exception as e:
                print(f"Failed to load document {p}: {e}")

        if docs:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunks = splitter.split_documents(docs)
            vs = Chroma.from_documents(chunks, embedding=OpenAIEmbeddings(), persist_directory=VS_DIR)
            vs.persist()

def get_rag_chain():
    ensure_vectorstore()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    vs = Chroma(persist_directory=VS_DIR, embedding_function=OpenAIEmbeddings())
    retriever = vs.as_retriever(search_kwargs={"k": 3})

    def _invoke(inputs):
        question = inputs.get("question","")
        docs = retriever.get_relevant_documents(question) if vs else []
        context = "\n\n".join(d.page_content[:1200] for d in docs) if docs else "No documents"
        prompt = QA_TMPL.format_messages(question=question, context=context)
        out = llm.invoke(prompt)
        return {"answer": out.content, "sources": [getattr(d, "metadata", {}) for d in docs]}

    return type("RAGChain", (), {"invoke": staticmethod(_invoke)})
