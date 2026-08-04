from fastapi import FastAPI
from app.routers import auth, documents

app = FastAPI(title="AI Document Q&A")

app.include_router(auth.router)
app.include_router(documents.router)

@app.get("/health")
def health():
    return {"status": "ok"}