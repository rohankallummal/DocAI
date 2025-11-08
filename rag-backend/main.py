from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import (
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS
)
from rag_pipeline import RAGPipeline
from routes import register_routes


app = FastAPI(
    title="RAG System API",
    description="Retrieval-Augmented Generation system for PDF documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)


rag = RAGPipeline()

register_routes(app, rag)

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("RAG System starting up...")
    print(f"Current collection: {rag.current_collection or 'None'}")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("RAG System shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )