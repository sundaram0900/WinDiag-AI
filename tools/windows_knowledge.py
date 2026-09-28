from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_huggingface import (
    ChatHuggingFace,
    HuggingFaceEmbeddings,
    HuggingFaceEndpoint,
)
from langchain.tools import ToolRuntime

from retrieval.reranker import rerank_documents


load_dotenv()


# ============================================================
# Models
# ============================================================

embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-4B-Instruct-2507",
    task="text-generation",
    max_new_tokens=256,
    temperature=0.1,
)

chat_model = ChatHuggingFace(
    llm=llm
)


# ============================================================
# Vector store
# ============================================================

vector_store = Chroma(
    collection_name="winddiag_knowledge",
    embedding_function=embeddings,
    persist_directory="../vector_store",
)


# ============================================================
# Query rewriter
# ============================================================

rewrite_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """Rewrite the user's latest question into a standalone
question using the conversation context.

Preserve the original meaning.
Do not answer the question.
Do not add information that is not present in the conversation.
If the question is already standalone, return it unchanged.
Return only the rewritten question."""
    ),
    (
        "human",
        """Conversation:
{conversation}

Latest question:
{question}"""
    ),
])

rewriter = rewrite_prompt | chat_model


# ============================================================
# Convert agent messages into conversation text
# ============================================================

def format_conversation(messages):
    """Convert agent messages into text for the query rewriter."""

    conversation = []

    for message in messages:

        if message.type == "human":
            role = "User"

        elif message.type == "ai":
            role = "WinDiag AI"

        else:
            continue

        if message.content:
            conversation.append(
                f"{role}: {message.content}"
            )

    return "\n\n".join(conversation)


# ============================================================
# Windows knowledge tool
# ============================================================

@tool
def search_windows_knowledge(
    query: str,
    runtime: ToolRuntime,
) -> str:
    """
    Search the Windows troubleshooting knowledge base.

    Use this tool for Windows troubleshooting guidance and
    Microsoft-recommended troubleshooting steps.
    """

    # Get conversation from the agent's current state
    messages = runtime.state.get(
        "messages",
        []
    )

    conversation = format_conversation(
        messages
    )

    # Rewrite the query using conversation context
    rewritten_query = rewriter.invoke({
        "conversation": conversation,
        "question": query,
    }).content.strip()

    # Retrieve candidate documents
    documents = vector_store.similarity_search(
        rewritten_query,
        k=10,
    )

    # Rerank candidates
    reranked = rerank_documents(
        rewritten_query,
        documents,
        top_k=5,
    )

    # Format retrieved knowledge
    result = "\n\n---\n\n".join(
        f"SOURCE: {document.metadata.get('source', 'Unknown')}\n"
        f"CATEGORY: {document.metadata.get('category', 'Unknown')}\n"
        f"CONTENT:\n{document.page_content}"
        for _, document in reranked
    )

    # Temporary debugging
    print("\n[Knowledge Tool]")
    print("Query:", query)

    print("\nConversation:")
    print(conversation)

    print("\nRewritten:")
    print(rewritten_query)

    return result