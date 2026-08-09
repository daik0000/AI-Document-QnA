from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatSessionCreate, ChatSessionOut, MessageCreate, MessageOut
from app.services import chat_service, rag_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionOut, status_code=201)
def create_session(
    data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.create_session(db, current_user.id, data.document_id, data.title)


@router.get("/sessions/{document_id}", response_model=list[ChatSessionOut])
def list_sessions(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.get_sessions_by_document(db, current_user.id, document_id)


@router.post("/sessions/{session_id}/message", response_model=MessageOut)
def send_message(
    session_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = chat_service.get_session_by_id(db, current_user.id, session_id)
    return rag_service.ask_question(db, session, data.question)

@router.post("/sessions/{session_id}/message/stream")
def send_message_stream(
    session_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = chat_service.get_session_by_id(db, current_user.id, session_id)

    def event_generator():
        for event in rag_service.ask_question_stream(db, session, data.question):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/sessions/{session_id}/history", response_model=list[MessageOut])
def get_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.get_history(db, current_user.id, session_id)