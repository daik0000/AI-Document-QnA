from sqlalchemy.orm import Session
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.services import embedding_service, vector_store, llm_service
from app.models.document import Document
TOP_K = 5

PROMPT_TEMPLATE = """
Bạn là trợ lý trả lời câu hỏi dựa trên tài liệu được cung cấp.
Chỉ dùng thông tin trong CONTEXT dưới đây để trả lời. Nếu không có thông tin liên quan, hãy nói rõ là không tìm thấy.

CONTEXT:
{context}

CÂU HỎI: {question}
"""

def _build_promt(context_chunks: list[str], question: str) -> str:
    """
    Xây dựng prompt dựa trên các chunk của tài liệu và câu hỏi.
    Args:
        context_chunks (list[str]): Danh sách các chunk của tài liệu.
        question (str): Câu hỏi cần trả lời.
    
    Returns:
        str: Prompt được xây dựng.
    """
    context = "\n\n---\n\n".join(context_chunks)
    return PROMPT_TEMPLATE.format(context=context, question=question)

def ask_question_stream(db: Session, session: ChatSession, question: str):
    doc = db.query(Document).filter(Document.id == session.document_id).first()

    query_vector = embedding_service.embed_query(question)
    results = vector_store.query_top_k(doc.vector_collection_name, query_vector, k=TOP_K)
    chunks = results["documents"][0]
    distances = results["distances"][0]
    prompt = _build_promt(chunks, question)

    source_chunks = [
        {"text": chunk, "distance": round(dist, 4)}
        for chunk, dist in zip(chunks, distances)
    ]

    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=question,
    )

    db.add(user_msg)
    db.commit()

    full_answer = ""
    for piece in llm_service.generate_answer_stream(prompt):
        full_answer += piece
        yield {
            "type": "chunk",
            "text": piece,
       }

    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=full_answer,
        source_chunks=source_chunks
    )

    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

def ask_question(db: Session, session: ChatSession, question: str) -> ChatMessage:
    """
    Trả lời câu hỏi dựa trên các chunk của tài liệu được lưu trong session.
    Args:
        db (Session): Phiên làm việc của cơ sở dữ liệu.
        session (ChatSession): Phiên chat hiện tại.
        question (str): Câu hỏi cần trả lời.
    
    Returns:
        ChatMessage: Tin nhắn chứa câu trả lời được tạo ra từ GenAI.
    """

    doc = db.query(Document).filter(Document.id == session.document_id).first()

    query_vector = embedding_service.embed_query(question)
    results = vector_store.query_top_k(doc.vector_collection_name, query_vector, k=TOP_K)

    chunks = results["documents"][0]
    distances = results["distances"][0]

    prompt = _build_promt(chunks, question)
    answer_text = llm_service.generate_answer(prompt)

    source_chunks = [
        {"text": chunk, "distance": round(dist, 4)}
        for chunk, dist in zip(chunks, distances)
    ]

    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=question,
    )

    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer_text,
        source_chunks=source_chunks
    )

    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg