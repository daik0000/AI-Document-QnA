from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.services import document_service


def create_session(db: Session, user_id: int, document_id: int, title: str | None) -> ChatSession:
    doc = document_service.get_document_by_id(db, user_id, document_id)  # tự raise 404 nếu không phải của user

    if doc.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document chưa sẵn sàng để chat (status hiện tại: {doc.status})",
        )

    session = ChatSession(
        user_id=user_id,
        document_id=document_id,
        title=title or doc.filename,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_by_id(db: Session, user_id: int, session_id: int) -> ChatSession:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )
    return session


def get_sessions_by_document(db: Session, user_id: int, document_id: int) -> list[ChatSession]:
    document_service.get_document_by_id(db, user_id, document_id)   # 404 nếu document không phải của user
    return (
        db.query(ChatSession)
        .filter(ChatSession.document_id == document_id, ChatSession.user_id == user_id)
        .all()
    )


def get_history(db: Session, user_id: int, session_id: int) -> list[ChatMessage]:
    session = get_session_by_id(db, user_id, session_id)
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
        .all()
    )
