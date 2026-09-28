from langchain_huggingface import (
    HuggingFaceEndpoint,
    ChatHuggingFace
)

from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv

load_dotenv()


llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-4B-Instruct-2507",
    task="text-generation",
    max_new_tokens=256,
    temperature=0.1
)

chat_model = ChatHuggingFace(
    llm=llm
)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a query rewriting assistant for WinDiag AI.

Rewrite the user's latest question into a standalone
question that can be understood without the conversation.

Keep the original meaning.

Do not answer the question.

Return only the rewritten question.
"""
    ),
    (
        "human",
        """
Conversation:

{conversation}

Latest question:

{question}
"""
    )
])


chain = prompt | chat_model


conversation = """
User: My Wi-Fi is not working.
WinDiag AI: You should first check whether Wi-Fi is enabled
and whether other devices can connect to the network.
"""

question = "How can I free up storage space on Windows?"

response = chain.invoke({
    "conversation": conversation,
    "question": question
})


print("\n================ QUERY REWRITER ================\n")

print("Original question:")
print(question)

print("\nRewritten question:")
print(response.content)