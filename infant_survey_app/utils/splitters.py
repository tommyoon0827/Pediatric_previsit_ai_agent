
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_text_splitter(chunk_size: int = 800, chunk_overlap: int = 120):
    # 800글자씩 자르되, 문맥 유지를 위해 120글자는 겹치게 자릅니다.
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
