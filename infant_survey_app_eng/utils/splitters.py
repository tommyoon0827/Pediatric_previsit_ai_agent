
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_text_splitter(chunk_size: int = 800, chunk_overlap: int = 120):
    # Split into 800 characters, overlapping 120 characters to maintain context.
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
