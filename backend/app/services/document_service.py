from pydoc import doc

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.models.document import Document
from app.services.text_extraction_service import extract_text
from app.utils.text_splitter import split_text_into_chunks
import os
import uuid
from pathlib import Path

# === Defining constants for file handling ===
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}  # Allowed file types for upload
MAX_FILE_SIZE_MB = 10 
STORAGE_DIR = Path("storage") 

def create_document_from_upload(db: Session, user_id: int, original_filename: str, file_path: str, file_type: str) -> Document:
    new_doc = Document(
        user_id=user_id, 
        filename=original_filename, 
        file_path=file_path,
        file_type=file_type,
        status="processing",
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

def validate_file(file: UploadFile) -> str:
    # Check file extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed. Allowed types: {ALLOWED_EXTENSIONS}",
        )

    return ext

async def save_uploaded_file(file: UploadFile, user_id: int) -> tuple[str, str]:
    ext = validate_file(file)

    user_dir = STORAGE_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = user_dir / safe_filename

    content = await file.read()
    print(f"[DEBUG] Read {len(content)} bytes from uploaded file '{file.filename}'")

    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size_mb = file.file.tell() / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the maximum limit of {MAX_FILE_SIZE_MB} MB.",
        )

    with open(file_path, "wb") as f:
        f.write(content)

    return str(file_path), ext


def process_document(document: Document) -> None:
    from app.database import SessionLocal  # Import here to avoid circular imports
    db = SessionLocal()  # Create a new session for background processing   

    try:
        try:
            doc = db.query(Document).filter(Document.id == document.id).first()
            text = extract_text(doc.file_path, doc.file_type)
            chunks = split_text_into_chunks(text)

            doc.num_chunks = len(chunks)
            doc.status = "ready"

        except Exception as e:
            doc.status = "failed"
            print(f"[ERROR] Failed to process document ID {document.id}: {str(e)}")

        pass

    finally:
        db.commit()
        db.close()

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

    file_path = Path(doc.file_path)
    if file_path.exists():
        file_path.unlink()  # delete the file from storage

    db.delete(doc)
    db.commit()