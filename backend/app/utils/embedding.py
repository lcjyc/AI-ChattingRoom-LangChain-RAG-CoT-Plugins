import os
from typing import List, Literal

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings

def get_embeddings(model: Literal["openai", "ollama"] = "openai"):
    if model == "openai":
        return OpenAIEmbeddings()  # 可接收 openai_api_key from env
    elif model == "ollama":
        return OllamaEmbeddings(model="nomic-embed-text")
    else:
        raise ValueError(f"Unsupported embedding model: {model}")

def build_vectorstore(
    docs: List[Document],
    model: Literal["openai", "ollama"] = "openai"
) -> FAISS:
    embeddings = get_embeddings(model)
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore
