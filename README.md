# AI-Document-QnA
Ứng dụng cho phép upload tài liệu (PDF/txt) -> hỏi đáp dựa trên nội dung tài liệu đó (kiểu mini RAG).

## Chức năng cốt lõi

- Auth đơn giản (đăng ký/đăng nhập, JWT) - lưu user trong MySQL.
- Upload file -> lưu metadata vào MySQL, lưu file vào local/S3.
- Chia nhỏ (chunk) văn bản -> tạo embedding -> lưu vào Vector DB.
- Endpoint hỏi đáp: nhận câu hỏi -> tìm đoạn liên quan trong Vector DB -> gọi Gemini/OpenAI API -> trả lời có trích dẫn nguồn.
- Lưu lịch sử chat vào MySQL

**Stack:** FastAPI, MySQL (SQLAlchemy + Alembic để migrate), ChromaDB, Gemini API.