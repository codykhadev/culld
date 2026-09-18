from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import UPLOAD_DIR
from app.db import init_db
from app.routers import analyze, results, upload

UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Photo Culling Assistant API")

# Frontend runs on a different port (Vite dev server), so CORS must be explicit.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(analyze.router)
app.include_router(upload.router)
app.include_router(results.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
