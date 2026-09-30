"""ReAct Agent Loop for AL-KHALLAQI."""
import json
import re
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.prompts.agent_prompt import AGENT_SYSTEM
from app.services.ai.base import ChatMessage
from app.services.ai.router import get_ai
from app.services.agent.tools.registry import list_tools, run_tool


RE_ACTION = re.compile(r"Action\s*:\s*([a-zA-Z_]+)", re.IGNORECASE)
RE_INPUT = re.compile(r"Action\s*Input\s*:\s*(\{.*?\})\s*(?:\n|$)",
                      re.IGNORECASE | re.DOTALL)
RE_THOUGHT = re.compile(r"Thought\s*:\s*(.+?)(?=\nAction|\Z)",
                        re.IGNORECASE | re.DOTALL)


def _parse(text: str) -> Dict[str, Any]:
    thought_m = RE_THOUGHT.search(text)
    action_m = RE_ACTION.search(text)
    input_m = RE_INPUT.search(text)
    thought = thought_m.group(1).strip() if thought_m else ""
    action = action_m.group(1).strip() if action_m else ""
    payload = {}
    if input_m:
        raw = input_m.group(1)
        try:
            payload = json.loads(raw)
        except Exception:
            try:
                payload = json.loads(raw.replace("'", '"'))
            except Exception:
                payload = {"_raw": raw}
    return {"thought": thought, "action": action, "input": payload}


async def run_agent(goal: str, session_id: str = "default",
                    max_steps: Optional[int] = None) -> Dict[str, Any]:
    steps_limit = max_steps or settings.MAX_AGENT_STEPS
    tools = list_tools()
    tools_desc = "\n".join(f"- {t['name']}: {t['description']}" for t in tools)

    system = AGENT_SYSTEM + f"\n\nالأدوات المتاحة:\n{tools_desc}"
    history: List[ChatMessage] = []
    steps: List[Dict[str, Any]] = []
    final_answer = ""
    success = False

    for i in range(1, steps_limit + 1):
        prompt = f"الهدف: {goal}\n\nاستمر في التفكير واستدعاء الأدوات."
        raw = await get_ai().chat(prompt, system=system,
                                  history=history, temperature=0.6)
        parsed = _parse(raw)
        step = {
            "step": i, "thought": parsed["thought"],
            "action": parsed["action"], "action_input": parsed["input"],
            "observation": "", "final": False,
        }

        if parsed["action"].lower() in ("finish", "final", "done"):
            final_answer = parsed["input"].get("answer", "") or parsed["thought"]
            step["final"] = True
            steps.append(step)
            success = True
            break

        if not parsed["action"]:
            steps.append(step)
            history.append(ChatMessage(role="assistant", content=raw))
            history.append(ChatMessage(
                role="user",
                content="لم أفهم الأداة. التزم بالصيغة: Thought/Action/Action Input."))
            continue

        obs = await run_tool(parsed["action"], **parsed["input"])
        obs_str = json.dumps(obs, ensure_ascii=False, default=str)
        if len(obs_str) > 1500:
            obs_str = obs_str[:1500] + "... [truncated]"
        step["observation"] = obs_str
        steps.append(step)

        history.append(ChatMessage(role="assistant", content=raw))
        history.append(ChatMessage(role="user",
                                   content=f"Observation: {obs_str}"))

    if not final_answer:
        final_answer = "أنجزت الخطوات المطلوبة. راجع النتائج أعلاه."
        success = len(steps) > 0

    return {"goal": goal, "steps": steps,
            "final_answer": final_answer, "success": success}
