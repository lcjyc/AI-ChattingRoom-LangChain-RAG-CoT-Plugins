from langchain_core.tools import tool
from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()  # 讀取 .env 中的 SERPAPI_API_KEY

@tool
def web_search(query: str) -> str:
    """
    使用 SerpAPI 搜尋網頁，回傳前 3 筆搜尋摘要。
    每筆包含標題、摘要與連結。
    """
    search = GoogleSearch({
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY")
    })

    results = search.get_dict()
    organic_results = results.get("organic_results", [])

    if not organic_results:
        return "can't find any search results"

    top_two = organic_results[:3]
    formatted = []

    for i, result in enumerate(top_two, start=1):
        title = result.get("title", "No tiltle")
        snippet = result.get("snippet", "No snippet")
        link = result.get("link", "No link")
        formatted.append(f"{i}. {title} - {snippet} ({link})")

    return "\n\n".join(formatted)

