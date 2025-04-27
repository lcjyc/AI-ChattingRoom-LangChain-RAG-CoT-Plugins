from typing import List
from langchain_core.documents import Document
import os

def load_txt(file_path: str) -> List[Document]:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return [Document(page_content=text, metadata={"source": os.path.basename(file_path)})]

def load_pdf(file_path: str) -> List[Document]:
    import fitz  # PyMuPDF
    doc = fitz.open(file_path)
    documents = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        if text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": os.path.basename(file_path),
                        "page": page_num + 1,
                    },
                )
            )
    return documents

def load_csv(file_path: str) -> List[Document]:
    import pandas as pd
    df = pd.read_csv(file_path)
    documents = []
    for index, row in df.iterrows():
        row_text = "\n".join([f"{col}: {row[col]}" for col in df.columns])
        documents.append(
            Document(
                page_content=row_text,
                metadata={"source": os.path.basename(file_path), "row": index + 1},
            )
        )
    return documents

def load_file(file_path: str) -> List[Document]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        return load_txt(file_path)
    elif ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".csv":
        return load_csv(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
