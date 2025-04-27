import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler

load_dotenv()

def get_llm(model_name: str = "openai", stream: bool = False):
    if model_name == "openai":
        if stream:
            callback = AsyncIteratorCallbackHandler()
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY"),
                streaming=True,
                callbacks=[callback],
            )
            return llm, callback
        else:
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
            return llm, None
    elif model_name == "ollama":
        if stream:
            callback = AsyncIteratorCallbackHandler()
            llm = ChatOllama(
                model="llama3.2",
                streaming=True,
                callbacks=[callback],
            )
            return llm, callback
        else:
            llm = ChatOllama(model="llama3.2")
            return llm, None
    else:
        raise ValueError("Unsupported model")

