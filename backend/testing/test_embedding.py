from app.services.embedding_service import embed_documents, embed_query

vectors = embed_documents(["This is a test document.", "Another document for embedding."])

print(f"So chieu vector: {len(vectors[0])}")
print(f"Vector cho van ban dau tien: {vectors[0][:5]}")  # In ra 10 gia tri dau tien cua vector

