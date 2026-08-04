from fastapi import FastAPI
app = FastAPI(title="AI Document Q&A")

@app.get("/health")
def health():
    return {"status": "ok"}