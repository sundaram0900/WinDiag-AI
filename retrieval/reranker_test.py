from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# -------------------------
# 1. Load embedding model
# -------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)


# -------------------------
# 2. Connect to Chroma
# -------------------------

vector_store = Chroma(
    collection_name="winddiag_knowledge",
    embedding_function=embeddings,
    persist_directory="../vector_store"
)


# -------------------------
# 3. Retrieve candidates
# -------------------------

query = "My laptop is extremely slow"

documents = vector_store.similarity_search(
    query,
    k=10
)

print("Candidates retrieved:", len(documents))

for i, document in enumerate(documents, start=1):
    print(f"\n--- Candidate {i} ---")
    print("Category:", document.metadata.get("category"))
    print("Source:", document.metadata.get("source"))
    print("Content:", document.page_content[:300])


reranker = CrossEncoder(
    "Qwen/Qwen3-Reranker-0.6B"
)

pairs = [
    (query, document.page_content)
    for document in documents
]

scores = reranker.predict(pairs)

scored_documents = list(zip(scores, documents))

scored_documents.sort(
    key=lambda x: x[0],
    reverse=True
)

print("\n\n===== RERANKED RESULTS =====")

for rank, (score, document) in enumerate(
    scored_documents[:5],
    start=1
):
    print(f"\n--- Rank {rank} ---")
    print("Score:", score)
    print("Category:", document.metadata.get("category"))
    print("Source:", document.metadata.get("source"))
    print("Content:", document.page_content[:500])