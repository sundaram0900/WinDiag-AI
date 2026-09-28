from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)


vector_store = Chroma(
    collection_name="winddiag_knowledge",
    embedding_function=embeddings,
    persist_directory="../vector_store"
)

query = "What is the capital of France?"
results = vector_store.similarity_search_with_score(
    query,
    k=5
)

threshold = 1.0

for result, score in results:

    if score <= threshold:
        print("\nKEEP")
        print("Score:", score)
        print("Category:", result.metadata.get("category"))
        print("Content:")
        print(result.page_content[:300])

    else:
        print("\nREJECT")
        print("Score:", score)
