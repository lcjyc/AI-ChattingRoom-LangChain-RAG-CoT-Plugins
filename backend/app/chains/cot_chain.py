from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import Any


def get_thought_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "你是一位善於邏輯推理的 AI 助手，請依據歷史對話與提問逐步推理。"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])


def get_final_answer_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "你已完成對問題的推理，以下是你的思考過程："),
        ("human", "{thought}"),
        ("system", "請根據這些推理內容，給出最終明確的答案。")
    ])


def get_cot_chain(llm_step1: Any, llm_step2: Any):
    """組合成 LCEL 雙階段 Chain of Thought chain，支援 chat_history"""

    # 第一步：思考與推理
    step1_chain = RunnableParallel({
        "question": RunnablePassthrough(),
        "chat_history": RunnablePassthrough()
    }) | get_thought_prompt() | llm_step1 | StrOutputParser()

    # 第二步：產出最終答案
    step2_chain = RunnableParallel({
        "thought": step1_chain
    }) | get_final_answer_prompt() | llm_step2 | StrOutputParser()

    # 返回兩階段 Chain 結果（thought + final_answer）
    return RunnableParallel({
        "thought": step1_chain,
        "final_answer": step2_chain
    })
