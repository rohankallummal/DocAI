from fastapi import UploadFile, Form, HTTPException
from rag_pipeline import RAGPipeline


def register_routes(app, rag: RAGPipeline):
    @app.post("/upload")
    async def upload_pdf(file: UploadFile):
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        pdf_bytes = await file.read()
        
        try:
            num_chunks, model_used, collection_name = rag.ingest_pdf(
                pdf_bytes, 
                file.filename
            )
            
            return {
                "status": "success",
                "file": file.filename,
                "chunks": num_chunks,
                "model": model_used,
                "collection": collection_name
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process PDF: {str(e)}"
            )
    
    @app.post("/query")
    async def query_document(
        question: str = Form(...),
        top_k: int = Form(5)
    ):
        if not question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        if not (1 <= top_k <= 20):
            raise HTTPException(
                status_code=400,
                detail="top_k must be between 1 and 20"
            )
        
        print(f"Question: {question}")
        print(f"Retrieving top {top_k} chunks")
        
        result = rag.query(question, top_k)
        return result
    
    @app.post("/reset")
    async def reset_system():
        rag.reset()
        return {
            "status": "ok",
            "message": "System reset. Upload a new PDF to start again."
        }
    
    @app.get("/health")
    def health_check():
        return {"status": "ok"}
    
    @app.get("/collections")
    def list_collections():
        try:
            collections = rag.qdrant.list_collections()
            return {
                "status": "success",
                "collections": collections,
                "total": len(collections),
                "current_collection": rag.current_collection
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list collections: {str(e)}"
            )