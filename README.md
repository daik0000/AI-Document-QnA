# AI Document Q&A

Hệ thống cho phép user upload tài liệu (PDF/DOCX/TXT), sau đó "chat" hỏi đáp
dựa trên nội dung tài liệu đó (RAG — Retrieval Augmented Generation), có
trích dẫn nguồn.

> Project đang trong quá trình xây dựng. Xem tiến độ chi tiết bên dưới.

## Demo giao diện

| Đăng nhập | Đăng ký |
|---|---|
| ![Login](docs/screenshots/login.png) | ![Register](docs/screenshots/register.png) |

| Dashboard | Chat hỏi đáp |
|---|---|
| ![Upload](docs/screenshots/dashboard.png) | ![Chat](docs/screenshots/chat.png) |

## Kiến trúc

Xem chi tiết tại [docs/architecture.md](docs/architecture.md).

Tổng quan: React (Vite) frontend + FastAPI backend + MySQL (dữ liệu quan
hệ) + ChromaDB (vector DB, semantic search) + Gemini API (embedding + LLM
cho RAG).

## Tiến độ

- [x] **Giai đoạn 0** — Khởi tạo repo
- [x] **Giai đoạn 1** — Backend nền tảng: Auth (JWT) + CRUD document metadata
- [x] **Giai đoạn 2** — Upload file, extract text, chunking
- [x] **Giai đoạn 3** — Embedding & Vector DB
- [x] **Giai đoạn 4** — RAG pipeline hoàn chỉnh
- [x] **Giai đoạn 5** — Frontend
- [ ] Giai đoạn 6 — Nâng cấp trải nghiệm (streaming, rate limit...)
- [ ] Giai đoạn 7 — Đóng gói & Deploy

## Tech stack

- **Frontend:** React (Vite) + TailwindCSS + React Router + axios
- **Backend:** FastAPI + Pydantic
- **ORM:** SQLAlchemy 2.0 + Alembic (migration)
- **Database:** MySQL 8 (chạy qua Docker)
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **Xử lý file:** pdfplumber (PDF), python-docx (DOCX)
- **Embedding:** Gemini API (`gemini-embedding-001`, 768 chiều)
- **Vector DB:** ChromaDB (local, persistent, 1 collection/document)
- **LLM (sinh câu trả lời):** Gemini API (`gemini-2.5-flash`)

## Hướng dẫn chạy local

### Yêu cầu
- Python 3.11+ (khuyến nghị)
- Node.js 18+ và npm
- Docker + Docker Compose
- API key Gemini (miễn phí) — lấy tại [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Backend

1. Clone repo:
```bash
   git clone <repo-url>
   cd AI-Document-QnA
```

2. Tạo file `.env` ở thư mục gốc (dùng cho MySQL container):
```bash
   cp .env.example .env
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

5. Tạo file `backend/.env`, điền `DATABASE_URL`, `JWT_SECRET_KEY`,
   `GEMINI_API_KEY`:
```bash
   cp .env.example .env
```

6. Chạy migration:
```bash
   alembic upgrade head
```

7. Chạy server:
```bash
   uvicorn app.main:app --reload
```
   Backend chạy tại http://localhost:8000 (Swagger UI tại `/docs`).

### Frontend

Ở 1 terminal khác:
```bash
cd frontend
npm install
npm run dev
```
Frontend chạy tại http://localhost:5173.

> Backend đã bật CORS cho phép origin `http://localhost:5173`. Nếu chạy
> frontend ở cổng khác, cần cập nhật lại `allow_origins` trong
> `backend/app/main.py`.

## Luồng sử dụng

1. Đăng ký tài khoản → đăng nhập
2. Kéo-thả (hoặc chọn) file PDF/DOCX/TXT để upload
3. Chờ trạng thái tự chuyển "Đang xử lý" → "Sẵn sàng" (tự động, không cần
   tải lại trang)
4. Bấm "Chat" trên tài liệu đã sẵn sàng, đặt câu hỏi
5. Xem câu trả lời kèm nguồn trích dẫn (mở rộng để xem đoạn gốc)

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
| DELETE | `/documents/{id}` | Xóa document (kèm file thật, vector collection, và các phiên chat liên quan) |

### Chat (RAG)
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/chat/sessions` | Tạo phiên chat mới cho 1 document (document phải ở status `ready`) |
| GET | `/chat/sessions/{document_id}` | Danh sách phiên chat của 1 document |
| POST | `/chat/sessions/{id}/message` | Gửi câu hỏi, nhận câu trả lời kèm trích dẫn nguồn |
| GET | `/chat/sessions/{id}/history` | Lấy lịch sử hỏi đáp của 1 phiên chat |

> Toàn bộ endpoint `/documents/*` và `/chat/*` yêu cầu Authorization header:
> `Bearer <access_token>`, và đều được kiểm tra quyền sở hữu (user chỉ
> thấy/thao tác được dữ liệu của chính mình).

**Giới hạn hiện tại:**
- Chỉ hỗ trợ PDF có lớp text thật (native PDF); PDF scan/ảnh chưa xử lý
  được (chưa tích hợp OCR).
- PDF trình bày nhiều cột (văn bản hành chính, biểu mẫu...) có thể bị xáo
  trộn thứ tự đoạn văn khi trích xuất do `pdfplumber` đọc theo dòng, không
  nhận diện bố cục cột.
- Mỗi câu hỏi trong 1 phiên chat được xử lý độc lập, chưa giữ ngữ cảnh hội
  thoại nhiều lượt (multi-turn).
- Chưa có streaming response — câu trả lời hiện nguyên cục sau khi LLM xử
  lý xong, không hiện dần từng chữ.

## Cấu trúc lưu trữ

- **File gốc:** `backend/storage/<user_id>/<uuid>.<ext>` — tên file trên
  đĩa là UUID ngẫu nhiên (không dùng tên gốc user đặt) để tránh path
  traversal. Tên file gốc vẫn được lưu lại trong cột `filename` ở DB để
  hiển thị cho người dùng.
- **Vector embedding:** `backend/chroma_data/` — mỗi document có 1
  collection riêng trong ChromaDB, dùng cosine similarity. Bị xóa cùng
  lúc với document khi gọi `DELETE /documents/{id}`.
- **Lịch sử chat:** MySQL, bảng `chat_sessions` và `chat_messages` (kèm
  `source_chunks` dạng JSON để phục vụ trích dẫn nguồn).
- **JWT:** frontend lưu ở `localStorage` (đơn giản, khớp với thiết kế
  backend trả token qua JSON body; đánh đổi là rủi ro XSS cao hơn so với
  httpOnly cookie — có thể nâng cấp sau nếu cần).

---
