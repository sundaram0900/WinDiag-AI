from langchain_huggingface import HuggingFaceEmbeddings



from sklearn.metrics.pairwise import cosine_similarity

texts = [
    "My laptop is running very slowly",
    "My computer has poor performance",
    "My PC feels sluggish and takes a long time to respond",
    "How do I cook pasta?"
]

embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)

# Create document vectors
vectors = embeddings.embed_documents(texts)

# Our user's question
query = "My laptop is extremely slow"

# Convert the question into a vector
query_vector = embeddings.embed_query(query)

print("Query vector dimension:", len(query_vector))

# Compare query vector against all document vectors
similarities = cosine_similarity(
    [query_vector],
    vectors
)[0]
print(similarities
)

print("\nQuery:", query)

for i, score in enumerate(similarities):
    print(f"Text {i + 1}: {score:.4f} -> {texts[i]}")