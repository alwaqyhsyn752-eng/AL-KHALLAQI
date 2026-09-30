"""Tool registry."""
from typing import Any, Awaitable, Callable, Dict


TOOLS: Dict[str, Dict[str, Any]] = {}


def register(name: str, description: str,
             func: Callable[..., Awaitable[Any]]) -> None:
    TOOLS[name] = {"name": name, "description": description, "func": func}


def get_tool(name: str):
    return TOOLS.get(name)


def list_tools():
    return [{"name": t["name"], "description": t["description"]}
            for t in TOOLS.values()]


async def run_tool(name: str, **kwargs):
    t = get_tool(name)
    if not t:
        return {"error": f"unknown tool: {name}"}
    try:
        return await t["func"](**kwargs)
    except Exception as e:
        return {"error": f"{name} failed: {e}"}
