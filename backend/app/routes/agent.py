from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from langchain_core.runnables import RunnableConfig
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.runnables import RunnableWithMessageHistory

from utils.embedding import build_vectorstore
from utils.loader import load_file
from memory.file_memory import get_memory
from tools.tool_registry import TOOL_REGISTRY
from prompt.rag_prompt import format_docs

router = APIRouter()

from langchain_core.prompts import PromptTemplate

REACT_PROMPT = PromptTemplate.from_template(
"""You are a smart assistant that can use the following tools to solve problems:

{tools}

When answering, please strictly follow the format below :

Question: The user's question
Thought: Think about what to do next.
Action: The name of the action to take, from [{tool_names}]
Action Input: The input to the action
Observation: The result of the action
Final Answer: The final answer to the original question.

⚠️ Important Rules:
- Do not add words like "choose" or "use" before the tool name.
- The tool name must **exactly match** one of the listed tools.
- Only use the specified sections (Thought / Action / Action Input / Observation / Final Answer) — no extra text or explanation.

Begin!

Question: {input}
{agent_scratchpad}
""")

@router.post("/agent")
async def agent_ask(
    request: Request,
):
    body = await request.json()
    question = body.get("question")
    model = body.get("model", "openai")
    use_rag = body.get("use_rag", False)
    use_cot = body.get("use_cot", False)
    plugin_detail = body.get("plugin_detail", [])
    selected_files = body.get("selected_files", [])

    # --- 1. Init LLM ---
    if model == "openai":
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", streaming=True)
    elif model == "ollama":
        llm = ChatOllama(model="llama3.2", streaming=True)
    else:
        raise ValueError("Unsupported model")

    # --- 2. Tool 選擇 ---
    selected_tools: list[Tool] = []
    for item in plugin_detail:
        if item.get("enable"):
            tool = TOOL_REGISTRY.get(item["tool_name"])
            if tool:
                selected_tools.append(tool)

    # --- 3. 建立 Agent ---
    agent = create_react_agent(llm=llm, tools=selected_tools,prompt=REACT_PROMPT)
    agent_executor = AgentExecutor(agent=agent, tools=selected_tools, verbose=True,handle_parsing_errors=True,streaming=True,max_iterations=10)

    # --- 4. Optional RAG ---
    retriever = None
    rag_context_str = ""
    if use_rag and selected_files:
        all_docs: list[Document] = []
        for file_id in selected_files:
            all_docs.extend(load_file(file_id))

        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(all_docs)
        vectorstore = build_vectorstore(chunks, model=model)
        retriever = vectorstore.as_retriever()

        rag_context = retriever.invoke(question)
        rag_context_str = format_docs(rag_context)

        if rag_context_str:
            agent_input = f"以下是相關資料：\n{rag_context_str}\n\n問題：{question}"
        else:
            agent_input = question
    else:
         agent_input = question         

    # --- 6. 記憶 ---
    session_id = request.headers.get("X-Session-ID")
    final_chain = RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: get_memory(session_id),
        input_messages_key="input",
        history_messages_key="chat_history"
    )

    # --- 7. Streaming 回傳 ---
    
    async def format_stream(stream):
       for chunk in stream:
        print("[DEBUG] Agent chunk:", chunk)
        # 只抓最後的回答文字（final_output）
        if "output" in chunk:
            text = chunk["output"]
            yield f"{text.strip()}\n\n"   # 清除前後空白、轉成 str，然後組成 SSE 格式   
    
    config = RunnableConfig(configurable={"session_id": session_id})
    stream = final_chain.stream({"input": agent_input}, config=config)
    return StreamingResponse(format_stream(stream), media_type="text/event-stream")
