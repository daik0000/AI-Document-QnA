from google import genai

from app.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)

CHAT_MODEL = "gemini-2.5-flash"

def generate_answer_stream(prompt: str):
    for chunk in _client.models.generate_content_stream(
        model=CHAT_MODEL,
        contents=prompt,
    ):
        if chunk.text:
            yield chunk.text # ham yield se tra ve tung doan van ban duoc tao ra tu GenAI, cho phep trinh duyet hoac ung dung nhan du lieu theo tung phan nho thay vi phai doi cho den khi toan bo cau tra loi duoc tao ra.

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