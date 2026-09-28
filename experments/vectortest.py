from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

texts = [
    "My laptop is running very slowly",
    "My computer has poor performance",
    "My PC feels sluggish and takes a long time to respond",
    "How do I cook pasta?"
]

# Embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)

# Create vector database
vector_store = Chroma(
    collection_name="test_collection",
    embedding_function=embeddings,
    persist_directory="../vector_store"
)

# Add documents
vector_store.add_texts(texts)

print("Documents added to Chroma.")

# Search
query = "My laptop is extremely slow"

results = vector_store.similarity_search_with_score(
    query,
    k=3
)

print("\nSearch results:")

for result, score in results:
    print("Score:", score)
    print("Text:", result.page_content)
    print()