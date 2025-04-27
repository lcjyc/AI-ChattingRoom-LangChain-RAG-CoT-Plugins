from langchain_core.prompts import PromptTemplate

def format_docs(docs):
    """將 Document 陣列格式化成純文字供 Prompt 使用"""
    return "\n\n".join(doc.page_content for doc in docs)
