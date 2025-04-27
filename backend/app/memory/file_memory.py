from langchain_community.chat_message_histories import FileChatMessageHistory
import os

def get_memory(session_id: str):
    os.makedirs("history_store", exist_ok=True)
    file_path = os.path.join("history_store", f"{session_id}.json")
    return FileChatMessageHistory(file_path)
