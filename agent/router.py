from typing import Literal
import json
from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from langchain_huggingface import (
    HuggingFaceEndpoint,
    ChatHuggingFace
)


# ============================================================
# ROUTE SCHEMA
# ============================================================

class QueryRoute(BaseModel):
    route: Literal[
        "KNOWLEDGE",
        "DIAGNOSTIC",
        "BOTH"
    ]


# ============================================================
# MODEL
# ============================================================

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-4B-Instruct-2507",
    task="text-generation",
    max_new_tokens=50,
    temperature=0
)

chat_model = ChatHuggingFace(
    llm=llm
)


# ============================================================
# ROUTER PROMPT
# ============================================================

router_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are the query router for WinDiag AI.

Your job is to classify the user's request into exactly
one of these three routes.

KNOWLEDGE:
Use this when the user wants Windows troubleshooting
guidance, explanations, procedures, or Microsoft-recommended
solutions.

Examples:
- How do I fix Windows Update problems?
- What should I do if Windows is running slowly?
- How can I troubleshoot Wi-Fi problems in Windows?

DIAGNOSTIC:
Use this when the user wants information about the
actual current state of their computer.

Examples:
- How much RAM am I using?
- What is my CPU usage?
- What is my Internet speed?
- What Windows version am I running?

BOTH:
Use this when the user needs both information about
their computer AND Windows troubleshooting guidance.

Examples:
- My laptop is slow. What is causing it and what does
  Microsoft recommend?
- My Wi-Fi is slow. Check my connection and tell me
  what Windows recommends.
- My computer is using a lot of RAM. What could be
  causing it and how can I fix it?

Return ONLY valid JSON.

The JSON must have exactly this format:

{{"route": "KNOWLEDGE"}}

or

{{"route": "DIAGNOSTIC"}}

or

{{"route": "BOTH"}}

Do not include explanations.
Do not include markdown.
Do not include additional fields.
"""
    ),

    (
        "human",
        "{question}"
    )
])


# ============================================================
# ROUTER CHAIN
# ============================================================

router_chain = router_prompt | chat_model


# ============================================================
# ROUTING FUNCTION
# ============================================================

def route_query(question: str) -> QueryRoute:
    """
    Classify a user query into KNOWLEDGE, DIAGNOSTIC,
    or BOTH.

    The LLM produces JSON and Pydantic validates the result.
    """

    response = router_chain.invoke({
        "question": question
    })

    content = response.content.strip()

    print("\nRaw router output:")
    print(content)


    # --------------------------------------------------------
    # Remove accidental markdown code fences
    # --------------------------------------------------------

    if content.startswith("```"):

        content = content.replace(
            "```json",
            ""
        )

        content = content.replace(
            "```",
            ""
        )

        content = content.strip()


    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        data = json.loads(content)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Router returned invalid JSON:\n{content}"
        ) from error


    # --------------------------------------------------------
    # Validate using Pydantic
    # --------------------------------------------------------

    try:

        return QueryRoute.model_validate(data)

    except Exception as error:

        raise ValueError(
            f"Router returned an invalid route:\n{data}"
        ) from error


# ============================================================
# TEST ROUTER
# ============================================================

if __name__ == "__main__":

    questions = [

        "How do I fix Windows Update problems?",

        "How much RAM am I currently using?",

        "My laptop is slow. What is causing it "
        "and what does Microsoft recommend?",

        "What Windows version am I running?",

        "How can I troubleshoot Wi-Fi problems in Windows?",

        "My Wi-Fi is slow. Check my connection and "
        "tell me what Windows recommends."
    ]


    print()
    print("=" * 60)
    print("WIN DIAG AI - QUERY ROUTER TEST")
    print("=" * 60)


    for question in questions:

        print()
        print("-" * 60)

        print("Question:")
        print(question)

        try:

            result = route_query(question)

            print()
            print("Validated Route:")
            print(result.route)

        except Exception as error:

            print()
            print("ERROR:")
            print(error)


    print()
    print("=" * 60)
    print("ROUTER TEST COMPLETE")
    print("=" * 60)