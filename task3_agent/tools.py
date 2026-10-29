import ast
import operator
from pathlib import Path

from ddgs import DDGS
from langchain_core.tools import tool

DATA_DIR = Path(__file__).parent / "data"

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.FloorDiv: operator.floordiv,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


@tool
def web_search(query: str) -> str:
    """Search the web (DuckDuckGo) for up-to-date information."""
    try:
        results = DDGS().text(query, max_results=5)
    except Exception as e:
        return f"Search failed: {e}"
    return "\n\n".join(f"{r['title']}\n{r['body']}\n{r['href']}" for r in results) or "No results."


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression, e.g. '(12.5 * 4) / 3 + 2**5'."""
    try:
        return str(_eval(ast.parse(expression, mode="eval").body))
    except Exception as e:
        return f"Calculator error: {e}"


@tool
def read_file(filename: str) -> str:
    """Read a local text file from the agent's data folder by file name."""
    path = DATA_DIR / Path(filename).name  # blocks path traversal
    if not path.exists():
        available = ", ".join(p.name for p in DATA_DIR.glob("*")) or "none"
        return f"File not found. Available files: {available}"
    return path.read_text(encoding="utf-8")[:4000]


TOOLS = [web_search, calculator, read_file]