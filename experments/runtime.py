from dotenv import load_dotenv

from langchain_huggingface import (
    HuggingFaceEndpoint,
    ChatHuggingFace
)

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver


load_dotenv()


# ============================================================
# MODEL
# ============================================================

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-4B-Instruct-2507",
    task="text-generation",
    max_new_tokens=256,
    temperature=0.2
)

chat_model = ChatHuggingFace(
    llm=llm
)


# ============================================================
# TEST TOOL
# ============================================================

@tool
def test_tool(query: str, runtime: ToolRuntime) -> str:
    """
    Inspect the current agent conversation state.

    Use this tool when the user explicitly asks to inspect
    the current conversation state.
    """

    print("\n==============================================")
    print("TOOL WAS CALLED")
    print("==============================================")

    print("\n[Query received by tool]")
    print(query)

    print("\n[Agent state]")
    print(runtime.state)

    return "The tool successfully accessed the agent state."


# ============================================================
# CHECKPOINT
# ============================================================

checkpointer = InMemorySaver()


# ============================================================
# AGENT
# ============================================================

agent = create_agent(
    model=chat_model,
    tools=[test_tool],
    checkpointer=checkpointer
)


config = {
    "configurable": {
        "thread_id": "runtime-test"
    }
}


# ============================================================
# FIRST MESSAGE
# ============================================================

agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "My Wi-Fi is not working."
            }
        ]
    },
    config=config
)


# ============================================================
# SECOND MESSAGE
# ============================================================

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Use test_tool right now."
            }
        ]
    },
    config=config
)


# ============================================================
# FINAL RESPONSE
# ============================================================

print("\n==============================================")
print("FINAL RESPONSE")
print("==============================================")

print(result["messages"][-1].content)