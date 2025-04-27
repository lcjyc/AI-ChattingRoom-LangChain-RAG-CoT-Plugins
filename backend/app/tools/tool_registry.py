from tools.web_search_tool import web_search
from tools.code_interpreter_tool import code_interpreter
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.utilities.arxiv import ArxivAPIWrapper

# 註冊工具字典
TOOL_REGISTRY = {
    "web_search": web_search,
    "code_interpreter": code_interpreter,
    "wikipedia": WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),
    "arxiv": ArxivQueryRun(api_wrapper=ArxivAPIWrapper()),
}
