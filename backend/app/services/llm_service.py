from google import genai

from app.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)

CHAT_MODEL = "gemini-2.5-flash"

def generate_answer(prompt: str) -> str:
    """
    Su dung GenAI de tao cau tra loi cho prompt duoc cung cap.
    Args:
        prompt (str): Prompt can tao cau tra loi.
    
    Returns:
        str: Cau tra loi duoc tao ra tu GenAI.
    """
    response = _client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
    )
    return response.text