from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from typing import Any


def get_thought_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "你是一位善於思考的AI助手，請根據以下資料，對問題進行邏輯推理。"),
        ("system", "資料如下：\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])


def get_final_answer_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "以下是你對問題的邏輯推理：\n{thought}"),
        ("human", "請根據這些推理，給出最終答案。")
    ])


def get_rag_cot_chain(llm_step1: Any, llm_step2: Any, retriever: Any, use_cot: bool = True):
    """組合成 LCEL 雙階段 RAG + CoT chain，支援 chat_history"""

    format_docs = lambda docs: "\n\n".join([doc.page_content for doc in docs])

    # 第一步：RAG -> 推理（CoT）
    step1_chain = RunnableParallel({
        "context": (lambda x: x["question"]) | retriever | format_docs,
        "question": (lambda x: x["question"]),
        "chat_history": (lambda x: x["chat_history"]),
    }) | get_thought_prompt() | llm_step1 | StrOutputParser()

    # 第二步：推理輸出 -> 最終答案
    step2_chain = RunnableParallel({
        "thought": step1_chain,
        "chat_history": (lambda x: x["chat_history"]),
    }) | get_final_answer_prompt() | llm_step2 | StrOutputParser()

    if not use_cot:
        return step2_chain

    return RunnableParallel({
        "thought": step1_chain,
        "final_answer": step2_chain
    })
