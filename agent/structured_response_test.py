import json

from dotenv import load_dotenv
from pydantic import ValidationError

from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import (
    HuggingFaceEndpoint,
    ChatHuggingFace
)

from response_schema import DiagnosticResponse


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
# 2. STRUCTURED RESPONSE PROMPT
# ============================================================

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are the response analysis component of WinDiag AI.

Analyze the diagnostic evidence provided by the user.

Return ONLY valid JSON.

The JSON must contain exactly these four fields:

{{
    "observed": [],
    "possible_contributors": [],
    "confirmed_findings": [],
    "recommendations": []
}}

Rules:

1. observed:
   Include only facts directly supported by the provided evidence.

2. possible_contributors:
   Include factors that could contribute to the problem.
   Do not present them as confirmed causes.

3. confirmed_findings:
   Include only causes directly supported by the evidence.
   If no cause is confirmed, return an empty list.

4. recommendations:
   Provide reasonable next steps based on the evidence.

5. Never invent measurements.

6. Never convert a possibility into a confirmed cause.

7. Do not include any text outside the JSON.
"""
    ),
    (
        "human",
        """
User's problem:
{question}

Diagnostic evidence:
{evidence}
"""
    )
])


# ============================================================
# 3. CREATE CHAIN
# ============================================================

chain = prompt | chat_model


# ============================================================
# 4. TEST DATA
# ============================================================

question = "My laptop is slow."

evidence = """
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


# ============================================================
# 5. CALL MODEL
# ============================================================

response = chain.invoke({
    "question": question,
    "evidence": evidence
})


content = response.content.strip()


print("\nRaw model output:")
print(content)


# ============================================================
# 6. PARSE JSON
# ============================================================

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


try:

    data = json.loads(content)

except json.JSONDecodeError as error:

    print("\nERROR: Model did not return valid JSON.")

    raise ValueError(
        f"Invalid JSON returned by model:\n{content}"
    ) from error


# ============================================================
# 7. VALIDATE WITH PYDANTIC
# ============================================================

try:

    result = DiagnosticResponse.model_validate(data)

except ValidationError as error:

    print("\nERROR: Response does not match schema.")

    print(error)

    raise


# ============================================================
# 8. DISPLAY STRUCTURED RESULT
# ============================================================

print("\nStructured Diagnostic Response:")
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