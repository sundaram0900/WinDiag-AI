from langchain_huggingface import (
    HuggingFaceEmbeddings,
    HuggingFaceEndpoint,
    ChatHuggingFace
)

from dotenv import load_dotenv

from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate

from retrieval.reranker import rerank_documents


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
# 3. CREATE LLM
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
# 4. QUERY REWRITER
# ============================================================

rewrite_prompt = ChatPromptTemplate.from_messages([
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

rewriter = rewrite_prompt | chat_model


# ============================================================
# 5. RETRIEVE CANDIDATE DOCUMENTS
# ============================================================

def retrieve_documents(query):

    documents = vector_store.similarity_search(
        query,
        k=10
    )

    return documents


# ============================================================
# 6. RETRIEVE + RERANK
# ============================================================

def retrieve_and_rerank(query):

    documents = retrieve_documents(query)

    reranked_documents = rerank_documents(
        query,
        documents,
        top_k=5
    )

    return [
        document
        for score, document in reranked_documents
    ]


# ============================================================
# 7. FORMAT DOCUMENTS
# ============================================================

def format_docs(docs):

    return "\n\n".join(
        document.page_content
        for document in docs
    )


# ============================================================
# 8. ANSWER PROMPT
# ============================================================

answer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are WinDiag AI, a Windows troubleshooting assistant.

Answer the user's latest question using the provided
Windows troubleshooting context.

Use the conversation when necessary to understand
the user's question.

If the context does not contain enough information
to answer the question, say that the available
knowledge is insufficient.

If the question is not related to Windows OS,
tell the user that you can only help with Windows.

Do not invent troubleshooting steps.

Do not assume that a possible cause is a confirmed cause.

Context:

{context}

Conversation:

{conversation}
"""
    ),
    (
        "human",
        "{question}"
    )
])


# ============================================================
# 9. CONVERSATIONAL RAG FUNCTION
# ============================================================

def answer_question(conversation, question):

    # ----------------------------------------
    # Rewrite the question
    # ----------------------------------------

    rewrite_response = rewriter.invoke({
        "conversation": conversation,
        "question": question
    })

    rewritten_query = rewrite_response.content.strip()

    print("\n[Rewritten Query]")
    print(rewritten_query)


    # ----------------------------------------
    # Retrieve + rerank using rewritten query
    # ----------------------------------------

    documents = retrieve_and_rerank(
        rewritten_query
    )


    # ----------------------------------------
    # Convert documents into context
    # ----------------------------------------

    context = format_docs(documents)


    # ----------------------------------------
    # Generate final answer
    # ----------------------------------------

    response = (
        answer_prompt
        | chat_model
    ).invoke({
        "context": context,
        "conversation": conversation,
        "question": question
    })


    return response.content


# ============================================================
# 10. TEST CONVERSATION
# ============================================================

conversation = ""


# ------------------------------------------------------------
# FIRST QUESTION
# ------------------------------------------------------------

question1 = "My Wi-Fi is not working."

answer1 = answer_question(
    conversation,
    question1
)

print("\n================ WIN DIAG AI ================\n")

print("User:", question1)

print("\nWinDiag AI:", answer1)


# ------------------------------------------------------------
# ADD FIRST TURN TO CONVERSATION
# ------------------------------------------------------------

conversation += f"""
User: {question1}
WinDiag AI: {answer1}
"""


# ------------------------------------------------------------
# SECOND QUESTION
# ------------------------------------------------------------

question2 = "What should I check first?"

answer2 = answer_question(
    conversation,
    question2
)

print("\nUser:", question2)

print("\nWinDiag AI:", answer2)