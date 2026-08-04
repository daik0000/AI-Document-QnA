from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.document import Document
from app.schemas.document import DocumentCreate


def create_document(db: Session, user_id: int, doc_data: DocumentCreate) -> Document:
    new_doc = Document(
        user_id=user_id,
        filename=doc_data.filename,
        file_type=doc_data.file_type,
        file_path=f"storage/{user_id}/{doc_data.filename}",  # giả lập, chưa có file thật
        status="processing",
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


def get_documents_by_user(db: Session, user_id: int) -> list[Document]:
    return db.query(Document).filter(Document.user_id == user_id).all()


def get_document_by_id(db: Session, user_id: int, document_id: int) -> Document:
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user_id)
        .first()
    )
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return doc


def delete_document(db: Session, user_id: int, document_id: int) -> None:
    doc = get_document_by_id(db, user_id, document_id)  # tận dụng lại, tự raise 404 nếu không phải của user này
    db.delete(doc)
    db.commit()