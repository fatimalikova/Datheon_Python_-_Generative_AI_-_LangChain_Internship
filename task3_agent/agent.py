import time

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GOOGLE_API_KEY, MODEL
from task3_agent.tools import TOOLS

TOOLS_BY_NAME = {t.name: t for t in TOOLS}
SYSTEM = (
    "You are a research agent. Use tools when needed: web_search for current facts, "
    "calculator for any arithmetic, read_file for local files. "
    "Before calling a tool, briefly explain your reasoning. Finish with a clear final answer."
)


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content)
    return str(content)


def _invoke_with_retry(llm, messages):
    for wait in (2, 5, 10, 20):
        try:
            return llm.invoke(messages)
        except Exception as e:
            print(f"Server məşğuldur ({type(e).__name__}), {wait} saniyə gözləyirəm...")
            time.sleep(wait)
    return llm.invoke(messages)


def run_agent(question: str, max_steps: int = 8):
    llm = ChatGoogleGenerativeAI(
        model=MODEL, google_api_key=GOOGLE_API_KEY, temperature=0
    ).bind_tools(TOOLS)

    messages = [SystemMessage(content=SYSTEM), HumanMessage(content=question)]

    for step in range(1, max_steps + 1):
        ai = _invoke_with_retry(llm, messages)
        messages.append(ai)

        thought = _text(ai.content).strip()
        if not ai.tool_calls:
            print(f"\n✅ Final Answer:\n{thought}\n")
            return thought

        if thought:
            print(f"\n[Step {step}] 💭 Thought: {thought}")

        for call in ai.tool_calls:
            print(f"[Step {step}] 🔧 Action: {call['name']}({call['args']})")
            observation = TOOLS_BY_NAME[call["name"]].invoke(call["args"])
            print(f"[Step {step}] 👁 Observation: {str(observation)[:400]}")
            messages.append(ToolMessage(content=str(observation), tool_call_id=call["id"]))

    print("Max steps reached.")


if __name__ == "__main__":
    print("Agent hazırdır. Çıxmaq üçün 'exit' yaz.\n")
    while True:
        q = input("Sual: ").strip()
        if q.lower() in {"exit", "quit", ""}:
            break
        run_agent(q)