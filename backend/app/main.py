from fastapi import FastAPI
from app.routers import auth, documents, chat

from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

app = FastAPI(title="AI Document Q&A")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://ai-document-qna.vercel.app"],
    allow_credentials=True, # credentials are allowed to be sent in cross-origin requests
    allow_methods=["*"], # allow all HTTP methods (GET, POST, PUT, DELETE, etc.) in cross-origin requests
    allow_headers=["*"], # allow all headers in cross-origin requests
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)

from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exception_handlers import http_exception_handler, unhandled_exception_handler

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

@app.get("/health")
def health():
    return {"status": "ok"}