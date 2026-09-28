from langchain_huggingface import (
    HuggingFaceEmbeddings,
    HuggingFaceEndpoint,
    ChatHuggingFace
)
from dotenv import load_dotenv

from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.runnables import RunnablePassthrough
load_dotenv()


# ============================================================
# 1. LOAD THE EMBEDDING MODEL
# ============================================================

embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)


# ============================================================
# 2. CONNECT TO EXISTING CHROMA VECTOR DATABASE
# ============================================================

vector_store = Chroma(
    collection_name="winddiag_knowledge",
    embedding_function=embeddings,
    persist_directory="../vector_store"
)


# ============================================================
# 3. CREATE RETRIEVER
# ============================================================

retriever = vector_store.as_retriever(
    search_kwargs={"k": 5}
)


# ============================================================
# 4. FORMAT RETRIEVED DOCUMENTS
# ============================================================

def format_docs(docs):
    return "\n\n".join(
        document.page_content
        for document in docs
    )


# ============================================================
# 5. CREATE PROMPT
# ============================================================

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are WinDiag AI, a Windows troubleshooting assistant.

Answer the user's question using only the provided Windows
troubleshooting context.

If the context does not contain enough information to answer
the question, say that the available knowledge is insufficient.

If the question is not related to windows os tell that you can only help with windows only.

Do not invent troubleshooting steps.

Context:
{context}
"""
    ),
    (
        "human",
        "{question}"
    )
])


# ============================================================
# 6. CREATE HUGGING FACE LLM
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
# 7. BUILD RAG CHAIN
# ============================================================

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | chat_model
)


# ============================================================
# 8. USER QUERY
# ============================================================

query = "My  laptop is extremely slow"


# ============================================================
# 9. RUN THE COMPLETE RAG PIPELINE
# ============================================================

response = rag_chain.invoke(query)


# ============================================================
# 10. PRINT ANSWER
# ============================================================

print("\n================ WIN DIAG AI ================\n")

print(response.content)