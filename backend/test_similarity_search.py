from app.database import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.services.embedding_service import embed_query
from app.services.vector_store import query_top_k

DOCUMENT_ID = 18
QUERY = "asdkjfh 12345 .... xyzabc random gibberish text"

db = SessionLocal()
doc = db.query(Document).filter(Document.id == DOCUMENT_ID).first()

if doc is None or doc.status != "ready":
    print("Document chưa sẵn sàng hoặc không tồn tại.")

elif not doc.vector_collection_name:
    print("Document đã ready nhưng chưa có vector_collection_name.")

else:
    query_vector = embed_query(QUERY)
    results = query_top_k(doc.vector_collection_name, query_vector, k=3)
    print(f"\nCâu hỏi: {QUERY}\n")
    for i, (chunk_text, distance) in enumerate(
        zip(results["documents"][0], results["distances"][0])
    ):
        print(f"--- Kết quả {i+1} (distance={distance:.4f}) ---")
        print(chunk_text)
        print()

db.close()