from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, Request
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.document import DocumentOut
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentOut, status_code=201)
@limiter.limit("5/minute")  # Giới hạn số lượng request upload tài liệu trong 1 phút
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), # File(...) indicates that this endpoint expects a file upload. The file parameter will be populated with the uploaded file.
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path, file_type = await document_service.save_uploaded_file(file, current_user.id)
    doc = document_service.create_document_from_upload(db, current_user.id, file.filename, file_path, file_type)
    background_tasks.add_task(document_service.process_document, doc)

    return doc

@router.get("", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return document_service.get_documents_by_user(db, current_user.id)


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return document_service.get_document_by_id(db, current_user.id, document_id)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document_service.delete_document(db, current_user.id, document_id)