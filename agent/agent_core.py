from typing import TypedDict

from langchain_huggingface import (
    HuggingFaceEndpoint,
    ChatHuggingFace
)

from langchain.agents import create_agent

from langgraph.checkpoint.memory import InMemorySaver

from dotenv import load_dotenv

from tools.cpu import get_cpu_usage
from tools.memory import get_memory_usage
from tools.disk import get_system_drive_storage
from tools.system import get_system_info
from tools.process import get_top_processes
from tools.windows_knowledge import search_windows_knowledge

from tools.get_network_info import (
    get_network_info,
    test_internet_speed
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# 1. LOAD LLM
# ============================================================

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-4B-Instruct-2507",
    task="text-generation",
    max_new_tokens=512,
    temperature=0.2
)

chat_model = ChatHuggingFace(
    llm=llm
)


# ============================================================
# 2. TOOLS
# ============================================================

tools = [
    get_cpu_usage,
    get_memory_usage,
    get_system_drive_storage,
    get_top_processes,
    get_system_info,
    get_network_info,
    test_internet_speed,
    search_windows_knowledge
]


# ============================================================
# 3. CHECKPOINTER
# ============================================================

checkpointer = InMemorySaver()


# ============================================================
# 4. AGENT RUNTIME CONTEXT
# ============================================================

class WinDiagContext(TypedDict):
    route: str


# ============================================================
# 5. SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are WinDiag AI, a Windows diagnostic assistant.

You can inspect the user's Windows computer using the
available diagnostic tools and search the Windows knowledge base and if user aska anything other than tech and windows or microsoft tell the user politly that you cant answer on those thing that you are designed to do only this particular tasks act strictly only for windows assistant only nothing else  .

The query has been classified by a router.

The current route is available through runtime context.

Route meanings:

- KNOWLEDGE:
  Prioritize the Windows knowledge base.
  Use diagnostic tools only if the user's question specifically
  requires information about their actual computer.

- DIAGNOSTIC:
  Prioritize the diagnostic tools.
  Use the Windows knowledge base only if troubleshooting
  guidance is specifically needed.

- BOTH:
  Use both diagnostic tools and the Windows knowledge base
  when relevant.

Use the route as guidance, but always consider the user's
actual question before selecting tools.

Choose only the tools relevant to the user's question.

Use diagnostic tools when information about the user's actual
computer is required.

Use the Windows knowledge tool when the user needs Windows
troubleshooting guidance or Microsoft-recommended procedures.


DIAGNOSTIC EVIDENCE RULES:

1. Treat tool output as observed evidence.

2. Never invent measurements or system information.

3. Never claim that a tool measured something that it did not measure.

4. Distinguish clearly between:

   - Observed measurement
   - Possible contributor
   - Confirmed cause

5. An observed measurement alone does not prove causation.

6. Only call something a confirmed cause when the available
   evidence directly supports that conclusion.

7. If something could be contributing to the problem but has
   not been directly measured, describe it as a possibility
   and say that it has not been confirmed.

8. Do not infer network usage from CPU or memory usage.

9. Do not infer Internet speed from Wi-Fi link speed.

10. Do not infer disk activity from storage capacity usage.

11. Do not infer a hardware or software failure merely because
    a component is present or active.

12. If the available diagnostic information is insufficient,
    explicitly say that more information is needed.

When explaining findings, separate observations from
interpretations and recommendations.

Do not present speculation as fact.
"""


# ============================================================
# 6. CREATE AGENT
# ============================================================

agent = create_agent(

    model=chat_model,

    tools=tools,

    context_schema=WinDiagContext,

    system_prompt=SYSTEM_PROMPT,

    checkpointer=checkpointer
)