"""
Measles AI Sentinel — FastAPI Backend
Run: uvicorn backend.main:app --reload --port 8000
"""
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.routes import router

app = FastAPI(
    title="Measles AI Sentinel API",
    description="AI-Powered Measles Outbreak Intelligence & Detection System",
    version="1.0.0"
)

# Allow frontend to call backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routes
app.include_router(router, prefix="/api")

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Measles AI Sentinel"}
