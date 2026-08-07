from fastapi import FastAPI
from app.routers import auth, documents, chat

app = FastAPI(title="AI Document Q&A")

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/health")
def health():
    return {"status": "ok"}