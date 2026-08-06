import numpy as np

from google import genai
from google.genai import types
from app.config import settings 

_client = genai.Client(api_key=settings.gemini_api_key)

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768

def embed_documents(text: list[str]) -> list[list[float]]:

    """
    Tao embedding cho danh sach cac van ban (documents) su dung model Gemini Embedding.
    Args:
        text (list[str]): Danh sach cac van ban can tao embedding.
    Returns:
        list[list[float]]: Danh sach cac embedding tuong ung voi moi van ban.
    """

    result = _client.models.embed_content(
        model = EMBEDDING_MODEL,
        contents = text,
        config = types.EmbedContentConfig(
            task_type = "RETRIEVAL_DOCUMENT",
            output_dimensionality = EMBEDDING_DIMENSION
        ),
    )

    return [_normalize_vector(e.values) for e in result.embeddings]

def embed_query(text: str) -> list[float]:
    """
    Tao embedding cho mot truy van (query) 
    Args:
        text (str): Truy van can tao embedding.
    Returns:
        list[float]: Embedding tuong ung voi truy van.
    """

    result = _client.models.embed_content(
        model = EMBEDDING_MODEL,
        contents = [text],
        config = types.EmbedContentConfig(
            task_type = "RETRIEVAL_QUERY",
            output_dimensionality = EMBEDDING_DIMENSION
        ),
    )

    return _normalize_vector(result.embeddings[0].values)

def _normalize_vector(vector: list[float]) -> list[float]:
    """
    Chuan hoa vector ve do dai 1.
    gemini-embedding-001 yeu cau tu chuan hoa khi dung output_dimension. Do do, can chuan hoa vector truoc khi tra ve.
    Args:
        vector (list[float]): Vector can chuan hoa.
    Returns:
        list[float]: Vector da chuan hoa.
    """
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return (vector / norm).tolist()