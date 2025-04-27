from typing import Literal,Optional
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from utils.loader import load_file
from utils.embedding import get_embeddings

def load_and_split(file_path: str) -> list[Document]:
    docs = load_file(file_path)
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(docs)


def create_vectorstore_from_file(
    file_path: str,
    embed_type: Literal["openai", "ollama"] = "openai",
    save_path: Optional[str] = None,
) -> FAISS:
    docs = load_and_split(file_path)
    embeddings = get_embeddings(embed_type)
    db = FAISS.from_documents(docs, embeddings)
    if save_path:
        db.save_local(save_path)
    return db
