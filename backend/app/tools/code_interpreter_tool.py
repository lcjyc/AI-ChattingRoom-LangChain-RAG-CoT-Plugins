from langchain.tools import tool
import io, sys, contextlib

@tool
def code_interpreter(code: str) -> str:
    """
    執行 Python 程式碼，回傳 stdout 結果或表達式的輸出值。
    支援單行表達式 (eval) 或多行程式碼 (exec)。
    """
    try:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            try:
                # 嘗試先用 eval（適合像 2 + 2、"Hello".upper()）
                result = eval(code, {})
                if result is not None:
                    print(result)
            except SyntaxError:
                # eval 不行就 fallback 用 exec（適合多行、定義函數、賦值等）
                exec(code, {})
        return buffer.getvalue().strip()
    except Exception as e:
        return f"Error: {str(e)}"
