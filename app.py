from src.embeddings import EmbeddingModel


embedding_model = EmbeddingModel()

text = "A landlord must return the tenant's security deposit according to the applicable rental law."

embedding = embedding_model.embed_text(text)

print("Embedding generated successfully!")
print(f"Embedding dimensions: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")