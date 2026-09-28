from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()


client = InferenceClient(
    provider="auto"
)


text = "My laptop is extremely slow"


embedding = client.feature_extraction(
    text,
    model="Qwen/Qwen3-Embedding-0.6B"
)


print("Embedding type:", type(embedding))
print("Embedding shape:", embedding.shape)
print("Embedding dimension:", embedding.shape[-1])
print("First 5 values:", embedding[0][:5])