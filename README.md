# AI Document Q&A
 
Hệ thống cho phép user upload tài liệu (PDF/DOCX/TXT), sau đó "chat" hỏi đáp
dựa trên nội dung tài liệu đó (RAG — Retrieval Augmented Generation), có
trích dẫn nguồn.
 
> Project đang trong quá trình xây dựng. Xem tiến độ chi tiết bên dưới.
 
## Kiến trúc
 
Xem chi tiết tại [docs/architecture.md](docs/architecture.md).
 
Tổng quan: FastAPI backend + MySQL (dữ liệu quan hệ) + ChromaDB (vector DB,
semantic search) + Gemini API (embedding, và LLM cho RAG ở giai đoạn sau).
 
## Tiến độ
 
- [x] **Giai đoạn 0** — Khởi tạo repo
- [x] **Giai đoạn 1** — Backend nền tảng: Auth (JWT) + CRUD document metadata
- [x] **Giai đoạn 2** — Upload file, extract text, chunking
- [x] **Giai đoạn 3** — Embedding & Vector DB
- [ ] Giai đoạn 4 — RAG pipeline hoàn chỉnh
- [ ] Giai đoạn 5 — Frontend
- [ ] Giai đoạn 6 — Nâng cấp trải nghiệm (streaming, rate limit...)
- [ ] Giai đoạn 7 — Đóng gói & Deploy

## Tech stack (đã dùng tới hiện tại)
 
- **Backend:** FastAPI + Pydantic
- **ORM:** SQLAlchemy 2.0 + Alembic (migration)
- **Database:** MySQL 8 (chạy qua Docker)
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **Xử lý file:** pdfplumber (PDF), python-docx (DOCX)
- **Embedding:** Gemini API (`gemini-embedding-001`, 768 chiều)
- **Vector DB:** ChromaDB (local, persistent, 1 collection/document)
## Hướng dẫn chạy local
 
### Yêu cầu
- Python 3.11+ (khuyến nghị)
- Docker + Docker Compose
- API key Gemini (miễn phí) — lấy tại [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
### Các bước
 
1. Clone repo:
```bash
   git clone <repo-url>
   cd AI-Document-QnA
```
 
2. Tạo file `.env` ở thư mục gốc (dùng cho MySQL container):
```bash
   cp .env.example .env
   # sửa các giá trị trong .env nếu muốn
```
 
3. Chạy MySQL:
```bash
   docker-compose up -d mysql
```
 
4. Setup backend:
```bash
   cd backend
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
```
 
5. Tạo file `backend/.env`:
```bash
   cp .env.example .env
   # điền DATABASE_URL, JWT_SECRET_KEY, và GEMINI_API_KEY
   # (xem hướng dẫn trong file)
```
 
6. Chạy migration:
```bash
   alembic upgrade head
```
 
7. Chạy server:
```bash
   uvicorn app.main:app --reload
```
 
8. Mở Swagger UI để test API: http://localhost:8000/docs
## API hiện có
 
### Auth
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/auth/register` | Đăng ký tài khoản |
| POST | `/auth/login` | Đăng nhập, nhận JWT token |
| GET | `/auth/me` | Lấy thông tin user hiện tại (cần token) |
 
### Documents
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/documents/upload` | Upload file thật (PDF/DOCX/TXT, tối đa 10MB), tự động extract text + chunking + embedding ở background |
| GET | `/documents` | Danh sách document của user hiện tại |
| GET | `/documents/{id}` | Chi tiết 1 document (404 nếu không phải của bạn) |
| DELETE | `/documents/{id}` | Xóa document (kèm file thật và vector collection tương ứng) |
 
> Toàn bộ endpoint `/documents/*` yêu cầu Authorization header:
> `Bearer <access_token>` lấy từ `/auth/login`.
 
**Về `POST /documents/upload`:**
- Nhận `multipart/form-data`, field `file`.
- Định dạng hỗ trợ: `.pdf`, `.docx`, `.txt`. Kích thước tối đa 10MB.
- Response trả về ngay với `status: "processing"`; việc extract text →
  chunking → tạo embedding → lưu vào ChromaDB chạy nền (background task).
  Gọi lại `GET /documents/{id}` sau vài giây để kiểm tra `status` đã
  chuyển sang `"ready"` (thành công, kèm `num_chunks` > 0) hay `"failed"`
  (lỗi, ví dụ không trích được text) chưa.
- **Giới hạn hiện tại:** chỉ hỗ trợ PDF có lớp text thật (native PDF).
  PDF dạng scan/ảnh sẽ bị đánh dấu `"failed"` vì chưa tích hợp OCR.
- **Chưa có API hỏi đáp (chat)** — việc truy vấn semantic search hiện chỉ
  test được qua script nội bộ, chưa lộ ra endpoint. Sẽ hoàn thiện ở
  Giai đoạn 4.
## Cấu trúc lưu trữ
 
- **File gốc:** `backend/storage/<user_id>/<uuid>.<ext>` — tên file trên
  đĩa là UUID ngẫu nhiên (không dùng tên gốc user đặt) để tránh path
  traversal. Tên file gốc vẫn được lưu lại trong cột `filename` ở DB để
  hiển thị cho người dùng.
- **Vector embedding:** `backend/chroma_data/` — mỗi document có 1
  collection riêng trong ChromaDB (tên lưu ở cột `vector_collection_name`
  trong bảng `documents`), dùng cosine similarity. Bị xóa cùng lúc với
  document khi gọi `DELETE /documents/{id}`.
---