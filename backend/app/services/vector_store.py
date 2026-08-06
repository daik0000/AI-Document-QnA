import chromadb
from pathlib import Path

CHROMA_PATH = Path("chroma_db")
_client = chromadb.PersistentClient(path=CHROMA_PATH)

def get_collection(collection_name: str):
    """
    Lay collection tuong ung voi ten collection. Neu collection chua ton tai, se tao moi.
    Args:
        collection_name (str): Ten collection can lay.
    Returns:
        Collection: Collection tuong ung voi ten collection.
    """
    return _client.get_or_create_collection(name=collection_name)

def add_chunks(
        collection_name: str,
        chunks: list[str],
        embeddings: list[list[float]],
) -> None:
    """
    Them cac chunk va embedding tuong ung vao collection.
    Args:
        collection_name (str): Ten collection can them chunk.
        chunks (list[str]): Danh sach cac chunk can them.
        embeddings (list[list[float]]): Danh sach cac embedding tuong ung voi moi chunk.
    
    Returns:
        None
    """
    collection = get_collection(collection_name)
    ids = [f"chunk_{i}" for i in range(len(chunks))]  # Tao id cho moi chunk
    metadata = [{"chunk_index": i} for i in range(len(chunks))]  # Tao metadata cho moi chunk

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadata
    )

def query_top_k(
        collection_name: str,
        query_embedding: list[float],
        k: int = 5
) -> list[dict]:
    """
    Truy van top-k cac chunk tuong ung voi embedding cua truy van.
    Args:
        collection_name (str): Ten collection can truy van.
        query_embedding (list[float]): Embedding cua truy van.
        k (int): So luong ket qua can lay.
    
    Returns:
        list[dict]: Danh sach cac ket qua tuong ung voi top-k chunk.
    """
    collection = get_collection(collection_name)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    return results["documents"][0]  # Tra ve danh sach cac chunk tuong ung voi top-k

def delete_collection(collection_name: str) -> None:
    """
    Xoa collection tuong ung voi ten collection.
    Args:
        collection_name (str): Ten collection can xoa.
    
    Returns:
        None
    """
    try:
        _client.delete_collection(name=collection_name)
    except Exception as e:
        print(f"[ERROR] Khong the xoa collection {collection_name}: {e}")
        pass