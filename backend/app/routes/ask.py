from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse,PlainTextResponse
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig, RunnablePassthrough
from llm_provider import get_llm
from utils.loader import load_file
from utils.embedding import build_vectorstore
from prompt.rag_prompt import format_docs
from chains.cot_chain import get_cot_chain
from chains.rag_cot_chain import get_rag_cot_chain
from memory.file_memory import get_memory
from langchain_core.runnables import RunnableWithMessageHistory
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, AIMessage
from langchain.schema import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    model: str = "ollama"
    use_rag: bool = False
    use_cot: bool = False
    selected_files: List[str] = []

@router.post("/ask")
async def ask(request: Request, body: AskRequest):
    # --- 1. Init LLM ---
    llm, streaming_handler = get_llm(model_name=body.model, stream=not body.use_cot)

    # --- 2. 建立 Chain ---
    rag_chain = None

    docs: list[Document] = []
    if body.selected_files:
        for file_path in body.selected_files:
            docs += load_file(file_path)

    if docs:
        from langchain.text_splitter import CharacterTextSplitter
        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        vectorstore = build_vectorstore(chunks, model=body.model)
        retriever = vectorstore.as_retriever()
    else:
        retriever = None

    if body.use_cot and body.use_rag:
        rag_chain = get_rag_cot_chain(llm_step1=llm, llm_step2=llm, retriever=retriever, use_cot=True)
    elif body.use_cot:
        rag_chain = get_cot_chain(llm_step1=llm, llm_step2=llm)
    elif body.use_rag:
        retriever_chain = retriever | format_docs
        chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert assistant. Please answer the user's question based solely on the provided information. Do not make up any information. If the answer cannot be found in the provided data, reply with 'I don't know'."),
        ("system", "Reference Information:\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
        rag_chain = (
            RunnablePassthrough.assign(context=lambda x: retriever_chain.invoke(x["question"]))
            | chat_prompt
            | llm
            | StrOutputParser()
        )
    else:
        simple_prompt = ChatPromptTemplate.from_messages([
       ("system", "You are a professional assistant. Please answer the user's questions. Remember the previous conversation and reply coherently."),
       MessagesPlaceholder(variable_name="chat_history"),
      ("human", "{question}")
    ])
        rag_chain = (
            simple_prompt
            | llm
            | StrOutputParser()
        )

    # --- 3. 建立記憶機制 ---
    session_id = request.headers.get("X-Session-ID")

    def get_session_history(session_id:str):
        return get_memory(session_id) 

    memory_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )

    session_input = {"question": body.question}
    config = RunnableConfig(
        callbacks=[streaming_handler] if not body.use_cot else [],
        configurable={"session_id": session_id}
    )

    # --- 4. CoT 模式：invoke，一次性回傳 ---
    if body.use_cot:
        result = memory_chain.invoke(session_input, config=config)
        if isinstance(result, dict):
            output = ""
            if "thought" in result:
                output += f"[Thought]\n{result['thought']}\n\n"
            if "final_answer" in result:
                output += f"[Final Answer]\n{result['final_answer']}\n"
        
            memory = get_memory(session_id)
            memory.add_messages([
            HumanMessage(content=body.question),
            AIMessage(content=output)
            ])

            return PlainTextResponse(output)

        else:
           memory = get_memory(session_id)
           memory.add_messages([
            HumanMessage(content=body.question),
            AIMessage(content=str(result))
           ])
           return PlainTextResponse(str(result))

    # --- 5. 非 CoT 模式：StreamingResponse ---
    async def format_stream_output(stream_result):
        for chunk in stream_result:
            yield str(chunk)

    stream = memory_chain.stream(session_input, config=config)
    return StreamingResponse(format_stream_output(stream), media_type="text/event-stream")
