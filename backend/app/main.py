from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.rag.chain import get_rag_chain
from pydantic import BaseModel
from typing import List, Optional

from contextlib import asynccontextmanager

# Global chain variable
rag_chain = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_chain
    print("Initializing RAG Chain...")
    try:
        rag_chain = get_rag_chain()
        print("RAG Chain initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize RAG Chain: {e}")
        # We can choose to raise or just log. Raising prevents startup.
        raise e
    yield
    # Cleanup if needed
    print("Shutting down...")

app = FastAPI(title="RAG AI Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://rag-implementation-seven.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

@app.get("/")
async def root():
    return {"message": "RAG AI Agent API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG Chain not initialized")
    
    # Run the chain asynchronously if possible, or sync in threadpool
    # chain.invoke is sync.
    
    result = rag_chain.invoke(
        {"input": request.query},
        config={"configurable": {"session_id": request.session_id}}
    )
    
    # Initial assumption on result structure, success depends on chain definition
    answer = result.get("answer", "")
    sources = []
    if "context" in result:
        for doc in result["context"]:
            sources.append(doc.metadata.get("source", "unknown"))
            
    return ChatResponse(answer=answer, sources=list(set(sources)))

from fastapi import UploadFile, File
import shutil
import os
from app.rag.ingestion import ingest_documents

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global rag_chain
    try:
        # Save file to backend/data
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # backend/app -> backend
        project_root = os.path.dirname(current_dir)
        data_path = os.path.join(project_root, "data")
        
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            
        file_path = os.path.join(data_path, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Re-run ingestion
        ingest_documents()
        
        # Re-initialize chain
        rag_chain = get_rag_chain()
        
        return {"message": f"Successfully uploaded {file.filename} and processed documents."}
    except ValueError as ve:
        # Catch the specific empty text error
        # Cleanup the useless file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # backend/app -> backend
        project_root = os.path.dirname(current_dir)
        data_path = os.path.join(project_root, "data")
        
        if not os.path.exists(data_path):
            return {"files": []}
            
        files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
        # exclude .gitkeep if present, optional
        files = [f for f in files if f != ".gitkeep"]
        
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    global rag_chain
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        data_path = os.path.join(project_root, "data")
        file_path = os.path.join(data_path, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
            # Re-run ingestion to update vector store
            ingest_documents()
            
            # Re-initialize chain
            rag_chain = get_rag_chain()
            
            return {"message": f"Deleted {filename}"}
        else:
             raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
