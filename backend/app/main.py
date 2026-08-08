from fastapi import FastAPI
from app.routers import auth, documents, chat

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Document Q&A")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True, # credentials are allowed to be sent in cross-origin requests
    allow_methods=["*"], # allow all HTTP methods (GET, POST, PUT, DELETE, etc.) in cross-origin requests
    allow_headers=["*"], # allow all headers in cross-origin requests
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/health")
def health():
    return {"status": "ok"}