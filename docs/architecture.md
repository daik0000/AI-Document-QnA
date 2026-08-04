# AI Document Q&A - Kiến trúc Full-stack chi tiết

Dự án: hệ thống cho phép user upload tài liệu (PDF/DOCX/TXT), backend xử lý và index nội dung, sau đó user có thể "chat" hỏi đáp dựa trên nội dung tài liệu đó (RAG - Retrieval Augmented Generation), có trích dẫn nguồn.

---

## 1. Kiến trúc tổng quan

```
┌─────────────┐      HTTPS/REST       ┌──────────────────┐
│   Frontend  │ ───────────────────►  │   FastAPI Backend │
│  (React/    │ ◄─────────────────── │   (Python)         │
│   Next.js)  │      JSON / SSE       └────────┬──────────┘
└─────────────┘                                │
                                                │
                ┌───────────────┬───────────────┼────────────────┐
                │               │               │                │
                ▼               ▼               ▼                ▼
        ┌──────────────┐ ┌────────────┐ ┌─────────────┐ ┌───────────────┐
        │    MySQL     │ │ Vector DB  │ │ File Storage│ │  AI Provider   │
        │ (users, docs,│ │ (Chroma /  │ │ (local disk │ │ (Gemini/OpenAI │
        │  chat, meta) │ │  pgvector) │ │  hoặc S3)   │ │  API)          │
        └──────────────┘ └────────────┘ └─────────────┘ └───────────────┘
```

**Nguyên tắc tách trách nhiệm (giống production thật):**
- **MySQL**: dữ liệu có cấu trúc, quan hệ rõ ràng (user, document metadata, lịch sử chat) - cần transaction, cần query chuẩn SQL.
- **Vector DB**: chỉ lưu embedding vectors + text chunk để tìm kiếm ngữ nghĩa (semantic search). Tách riêng vì đây là loại truy vấn hoàn toàn khác (similarity search, không phải relational query).
- **File Storage**: file gốc không nên nhét vào MySQL (blob field làm chậm DB) - lưu path/URL trong MySQL, file thật để ngoài.
- **AI Provider**: gọi qua API, không tự train model - đây là cách 99% công ty làm ở giai đoạn ứng dụng (không phải nghiên cứu).

---

## 2. Tech stack

| Layer | Công nghệ | Lý do chọn |
|---|---|---|
| Frontend | React (Vite) + TailwindCSS | Nhẹ, nhanh setup, dễ demo. Next.js cũng ok nếu bạn muốn SSR |
| Backend | FastAPI + Pydantic | Đúng yêu cầu JD, async tốt cho việc gọi AI API (I/O-bound) |
| ORM | SQLAlchemy 2.0 (async) + Alembic | Migration chuẩn, tránh viết raw SQL tay |
| DB quan hệ | MySQL 8 | Đúng yêu cầu JD |
| Vector DB | ChromaDB (local, dễ) hoặc pgvector (nếu muốn gộp vào Postgres) | Free, dễ chạy local, đủ cho demo/portfolio |
| AI Embedding | Gemini `text-embedding-004` hoặc OpenAI `text-embedding-3-small` | Free quota tốt (Gemini), rẻ (OpenAI) |
| AI Chat/LLM | Gemini 2.x Flash hoặc GPT-4o-mini | Nhanh, rẻ, đủ chất lượng cho demo |
| Auth | JWT (python-jose) + bcrypt hash password | Chuẩn REST API, không session-based |
| File parsing | PyPDF2/pdfplumber (PDF), python-docx (Word) | Extract text |
| Realtime response | Server-Sent Events (SSE) hoặc WebSocket | Để trả lời AI theo kiểu "streaming" như ChatGPT - điểm cộng lớn khi demo |
| Containerize | Docker + docker-compose | Chạy đồng bộ MySQL + backend + (Chroma nếu cần) chỉ với 1 lệnh |
| Deploy Backend | Railway / Render | Free tier, có MySQL đi kèm |
| Deploy Frontend | Vercel / Netlify | Free, tự động CI/CD từ GitHub |

---

## 3. Cấu trúc thư mục Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py                 # khởi tạo FastAPI app, mount routers
│   ├── config.py                # đọc biến môi trường (.env)
│   ├── database.py              # SQLAlchemy engine, session
│   │
│   ├── models/                  # SQLAlchemy models (bảng MySQL)
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── chat_session.py
│   │   └── chat_message.py
│   │
│   ├── schemas/                 # Pydantic schemas (request/response)
│   │   ├── user.py
│   │   ├── document.py
│   │   └── chat.py
│   │
│   ├── routers/                 # API endpoints, chia theo domain
│   │   ├── auth.py
│   │   ├── documents.py
│   │   └── chat.py
│   │
│   ├── services/                # business logic thực sự nằm ở đây
│   │   ├── auth_service.py
│   │   ├── document_service.py  # extract text, chunking
│   │   ├── embedding_service.py # gọi AI để tạo embedding
│   │   ├── vector_store.py      # giao tiếp với ChromaDB
│   │   └── rag_service.py       # ghép retrieval + generation
│   │
│   ├── core/
│   │   ├── security.py          # JWT, hash password
│   │   └── dependencies.py      # get_current_user, get_db
│   │
│   └── utils/
│       └── text_splitter.py     # chia văn bản thành chunks
│
├── alembic/                     # migration scripts
├── tests/                       # unit test (pytest)
├── requirements.txt
├── Dockerfile
└── .env.example
```
---

## 4. Thiết kế Database (MySQL)

```sql
-- Người dùng
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tài liệu đã upload
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,      -- đường dẫn lưu file thật (local/S3)
    file_type VARCHAR(50),                  -- pdf, docx, txt
    status VARCHAR(50) DEFAULT 'processing', -- processing / ready / failed
    num_chunks INT DEFAULT 0,
    vector_collection_name VARCHAR(255),    -- tên collection trong ChromaDB tương ứng
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Phiên chat (mỗi document có thể có nhiều phiên hỏi đáp)
CREATE TABLE chat_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    document_id INT NOT NULL,
    title VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- Từng tin nhắn trong phiên chat
CREATE TABLE chat_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,          -- 'user' hoặc 'assistant'
    content TEXT NOT NULL,
    source_chunks JSON,                  -- lưu lại chunk nào được dùng để trả lời (trích dẫn)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);
```

---

## 5. Luồng xử lý (Data Flow) - đây là phần quan trọng nhất để hiểu RAG

### 5.1. Luồng Upload tài liệu

```
1. User upload file (PDF) qua frontend
2. Backend nhận file → lưu vào storage → tạo record trong MySQL (status='processing')
3. Background task (dùng FastAPI BackgroundTasks hoặc Celery nếu muốn nâng cao):
   a. Extract text từ PDF (pdfplumber)
   b. Chia text thành chunks nhỏ (~500-800 tokens/chunk, overlap ~50-100 tokens)
   c. Với mỗi chunk → gọi Embedding API → nhận vector (mảng số thực ~768 hoặc 1536 chiều)
   d. Lưu (chunk_text, vector, metadata) vào ChromaDB
   e. Update MySQL: status='ready', num_chunks=N
4. Frontend poll hoặc dùng WebSocket để biết khi nào document sẵn sàng để chat
```

### 5.2. Luồng Hỏi đáp (Query/Chat) - đây chính là "RAG"

```
1. User gửi câu hỏi qua chat UI
2. Backend nhận câu hỏi → gọi Embedding API để biến câu hỏi thành vector
3. Query vào ChromaDB: tìm top-k (thường k=3-5) chunks có vector gần nhất
   với vector câu hỏi (cosine similarity)
4. Ghép các chunk tìm được thành "context"
5. Tạo prompt gửi cho LLM, dạng:

   ---
   Bạn là trợ lý trả lời câu hỏi dựa trên tài liệu được cung cấp.
   Chỉ dùng thông tin trong CONTEXT dưới đây để trả lời. Nếu không có
   thông tin liên quan, hãy nói rõ là không tìm thấy.

   CONTEXT:
   {chunk_1}
   {chunk_2}
   {chunk_3}

   CÂU HỎI: {user_question}
   ---

6. Gọi LLM API (Gemini/OpenAI) với prompt trên → nhận câu trả lời
7. (Nâng cao) Stream response về frontend theo từng token qua SSE
8. Lưu câu hỏi + câu trả lời + source_chunks vào MySQL (bảng chat_messages)
9. Trả về frontend: câu trả lời + trích dẫn "nguồn: đoạn X, trang Y"
```

---

## 6. Danh sách API endpoints

```
POST   /auth/register              Đăng ký
POST   /auth/login                 Đăng nhập, trả JWT token
GET    /auth/me                    Lấy thông tin user hiện tại

POST   /documents/upload           Upload tài liệu mới
GET    /documents                  Danh sách tài liệu của user
GET    /documents/{id}             Chi tiết 1 tài liệu (status, num_chunks...)
DELETE /documents/{id}             Xóa tài liệu (xóa cả vector collection liên quan)

POST   /chat/sessions              Tạo phiên chat mới cho 1 document
GET    /chat/sessions/{doc_id}     Lấy danh sách phiên chat của 1 document
POST   /chat/sessions/{id}/message Gửi câu hỏi, nhận câu trả lời (có thể SSE streaming)
GET    /chat/sessions/{id}/history Lấy lịch sử chat của phiên
```

---

## 7. Frontend - cấu trúc & UI chính

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx        # danh sách documents
│   │   ├── DocumentDetail.jsx   # xem status, chat với document
│   ├── components/
│   │   ├── UploadBox.jsx        # drag & drop file
│   │   ├── ChatWindow.jsx       # giao diện chat kiểu ChatGPT
│   │   ├── MessageBubble.jsx    # hiển thị tin nhắn + nguồn trích dẫn
│   │   └── DocumentCard.jsx
│   ├── api/
│   │   └── client.js            # axios instance, gắn JWT token vào header
│   ├── context/
│   │   └── AuthContext.jsx      # quản lý trạng thái đăng nhập
│   └── App.jsx
```

---
> Tài liệu này mô tả kiến trúc dự định của toàn bộ hệ thống. Xem `README.md` để biết phần nào đã triển khai thực tế tính đến thời điểm hiện tại.