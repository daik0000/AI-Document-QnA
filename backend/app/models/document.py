from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=True)          # pdf, docx, txt
    status = Column(String(50), default="processing")       # processing / ready / failed
    num_chunks = Column(Integer, default=0)
    vector_collection_name = Column(String(255), nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    owner = relationship("User", back_populates="documents")