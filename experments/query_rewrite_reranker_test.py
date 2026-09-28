from langchain_huggingface import (
    HuggingFaceEmbeddings,
    HuggingFaceEndpoint,
    ChatHuggingFace
)

from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv

from retrieval.reranker import rerank_documents

load_dotenv()


# ============================================================
# 1. EMBEDDINGS
# ============================================================

embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)


# ============================================================
# 2. CHROMA
# ============================================================

vector_store = Chroma(
    collection_name="winddiag_knowledge",
    embedding_function=embeddings,
    persist_directory="../vector_store"
)


# ============================================================
# 3. QUERY REWRITER
# ============================================================

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

If the latest question is already standalone,
return it unchanged.

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

rewriter = prompt | chat_model


# ============================================================
# 4. CONVERSATION
# ============================================================

conversation = """
User: My Wi-Fi is not working.

WinDiag AI: You should first check whether Wi-Fi is enabled
and whether other devices can connect to the network.
"""

question = "What should I check first?"


# ============================================================
# 5. REWRITE
# ============================================================

response = rewriter.invoke({
    "conversation": conversation,
    "question": question
})

rewritten_query = response.content.strip()


# ============================================================
# 6. ORIGINAL QUERY → CHROMA → RERANKER
# ============================================================

original_documents = vector_store.similarity_search(
    question,
    k=10
)

original_reranked = rerank_documents(
    question,
    original_documents,
    top_k=5
)


# ============================================================
# 7. REWRITTEN QUERY → CHROMA → RERANKER
# ============================================================

rewritten_documents = vector_store.similarity_search(
    rewritten_query,
    k=10
)

rewritten_reranked = rerank_documents(
    rewritten_query,
    rewritten_documents,
    top_k=5
)


# ============================================================
# 8. DISPLAY RESULTS
# ============================================================

print("\n================ QUERY + RERANKER TEST ================\n")

print("Original question:")
print(question)

print("\nRewritten question:")
print(rewritten_query)


print("\n\n================ ORIGINAL → RERANKER ================\n")

for i, (score, document) in enumerate(
    original_reranked,
    1
):
    print(f"\n--- RESULT {i} ---")
    print("Reranker score:", score)
    print("Category:",
          document.metadata.get("category"))
    print("Source:",
          document.metadata.get("source"))
    print("Content:")
    print(document.page_content[:500])


print("\n\n================ REWRITTEN → RERANKER ================\n")

for i, (score, document) in enumerate(
    rewritten_reranked,
    1
):
    print(f"\n--- RESULT {i} ---")
    print("Reranker score:", score)
    print("Category:",
          document.metadata.get("category"))
    print("Source:",
          document.metadata.get("source"))
    print("Content:")
    print(document.page_content[:500])