import json

from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate

from langchain_huggingface import (
    HuggingFaceEndpoint,
    ChatHuggingFace
)

from agent.response_schema import DiagnosticResponse


load_dotenv()


# ============================================================
# 1. LOAD MODEL
# ============================================================

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-4B-Instruct-2507",
    task="text-generation",
    max_new_tokens=512,
    temperature=0
)

chat_model = ChatHuggingFace(
    llm=llm
)


# ============================================================
# 2. FORMATTER PROMPT
# ============================================================

formatter_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are the structured response component of WinDiag AI.

Convert the diagnostic information into the required JSON structure.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

{{
    "observed": [],
    "possible_contributors": [],
    "confirmed_findings": [],
    "recommendations": []
}}

Rules:

1. observed:
   Include only facts directly supported by the provided information.

2. possible_contributors:
   Include possible factors that may contribute to the problem.
   Do not present them as confirmed causes.

3. confirmed_findings:
   Include only findings directly supported by the evidence.

4. recommendations:
   Provide relevant next steps based on the information.

5. Never invent measurements.

6. Never claim a cause is confirmed unless the evidence directly
   establishes it.

7. If there are no confirmed causes, use an empty list.

8. Do not include text outside the JSON.
"""
    ),
    (
        "human",
        """
User's request:
{question}

Diagnostic information:
{information}
"""
    )
])


# ============================================================
# 3. FORMAT RESPONSE
# ============================================================

def format_response(question: str, information: str) -> DiagnosticResponse:

    response = (formatter_prompt | chat_model).invoke({
        "question": question,
        "information": information
    })

    content = response.content.strip()


    # --------------------------------------------------------
    # Remove accidental markdown fences
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
            f"Formatter returned invalid JSON:\n{content}"
        ) from error


    # --------------------------------------------------------
    # Validate with Pydantic
    # --------------------------------------------------------

    return DiagnosticResponse.model_validate(data)

# ============================================================
# 4. TEST FORMATTER
# ============================================================

if __name__ == "__main__":

    question = "My laptop is slow."

    information = """
    CPU usage: 12.5%

    RAM usage: 79.2%
    Total RAM: 15.68 GB
    Available RAM: 3.26 GB

    System drive C: 84.7% used

    Top processes:
    PyCharm64.exe: 10.93% memory
    python.exe: 8.86% memory
    ChatGPT Classic.exe: 2.95% memory
    """

    result = format_response(
        question,
        information
    )

    print("\nStructured Response:")
    print(result)

    print("\nObserved:")
    for item in result.observed:
        print("-", item)

    print("\nPossible Contributors:")
    for item in result.possible_contributors:
        print("-", item)

    print("\nConfirmed Findings:")
    for item in result.confirmed_findings:
        print("-", item)

    print("\nRecommendations:")
    for item in result.recommendations:
        print("-", item)