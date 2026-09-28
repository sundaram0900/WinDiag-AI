from langchain_huggingface import (
    HuggingFaceEndpoint,
    ChatHuggingFace
)

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# 1. MODEL
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
# 2. CHECKPOINTER
# ============================================================

checkpointer = InMemorySaver()


# ============================================================
# 3. AGENT
# ============================================================

agent = create_agent(
    model=chat_model,
    tools=[],
    system_prompt="""
You are a helpful assistant.

Use previous messages from the current conversation
when answering follow-up questions.
""",
    checkpointer=checkpointer
)


# ============================================================
# 4. FIRST MESSAGE
# ============================================================

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "My laptop has 16 GB of RAM."
            }
        ]
    },
    config={
        "configurable": {
            "thread_id": "user-1"
        }
    }
)


print("\n================ RESPONSE 1 ================\n")

print(result["messages"][-1].content)


# ============================================================
# 5. SECOND MESSAGE
# ============================================================

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What about the CPU?"
            }
        ]
    },
    config={
        "configurable": {
            "thread_id": "user-1"
        }
    }
)


print("\n================ RESPONSE 2 ================\n")

print(result["messages"][-1].content)