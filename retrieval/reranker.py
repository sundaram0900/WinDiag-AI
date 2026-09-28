from sentence_transformers import CrossEncoder


# ============================================================
# LOAD RERANKER
# ============================================================

reranker = CrossEncoder(
    "Qwen/Qwen3-Reranker-0.6B"
)


# ============================================================
# RERANK DOCUMENTS
# ============================================================

def rerank_documents(query, documents, top_k=5):

    pairs = [
        (query, document.page_content)
        for document in documents
    ]

    scores = reranker.predict(pairs)

    scored_documents = list(
        zip(scores, documents)
    )

    scored_documents.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return scored_documents[:top_k]