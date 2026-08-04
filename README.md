# AI Document Q&A

Hệ thống cho phép user upload tài liệu (PDF/DOCX/TXT), sau đó "chat" hỏi đáp
dựa trên nội dung tài liệu đó (RAG — Retrieval Augmented Generation), có
trích dẫn nguồn.

> Project đang trong quá trình xây dựng. Xem tiến độ chi tiết bên dưới.

## Kiến trúc

Xem chi tiết tại [docs/architecture.md](docs/architecture.md).

Tổng quan: FastAPI backend + MySQL (dữ liệu quan hệ) + Vector DB (semantic
search, sẽ thêm ở giai đoạn sau) + AI Provider API cho RAG.

## Tiến độ

- [x] **Giai đoạn 0** — Khởi tạo repo
- [x] **Giai đoạn 1** — Backend nền tảng: Auth (JWT) + CRUD document metadata
- [ ] Giai đoạn 2 — Upload file, extract text, chunking
- [ ] Giai đoạn 3 — Embedding & Vector DB
- [ ] Giai đoạn 4 — RAG pipeline hoàn chỉnh
- [ ] Giai đoạn 5 — Frontend
- [ ] Giai đoạn 6 — Nâng cấp trải nghiệm (streaming, rate limit...)
- [ ] Giai đoạn 7 — Đóng gói & Deploy

## Tech stack (đã dùng tới hiện tại)

- **Backend:** FastAPI + Pydantic
- **ORM:** SQLAlchemy 2.0 + Alembic (migration)
- **Database:** MySQL 8 (chạy qua Docker)
- **Auth:** JWT (python-jose) + bcrypt (passlib)

## Hướng dẫn chạy local

### Yêu cầu
- Python 3.11+ (khuyến nghị)
- Docker + Docker Compose

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
   # điền DATABASE_URL và JWT_SECRET_KEY (xem hướng dẫn trong file)
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
| POST | `/documents` | Tạo document record (chưa upload file thật) |
| GET | `/documents` | Danh sách document của user hiện tại |
| GET | `/documents/{id}` | Chi tiết 1 document (404 nếu không phải của bạn) |
| DELETE | `/documents/{id}` | Xóa document |

> Toàn bộ endpoint `/documents/*` yêu cầu Authorization header:
> `Bearer <access_token>` lấy từ `/auth/login`.

---
