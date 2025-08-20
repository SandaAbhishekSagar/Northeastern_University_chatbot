
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import chromadb

router = APIRouter()

class DocumentUpload(BaseModel):
    documents: List[str]
    metadatas: List[Dict[str, Any]]
    ids: List[str]

@router.post("/upload-documents")
async def upload_documents(data: DocumentUpload):
    try:
        from services.shared.database import get_chroma_client, get_collection
        
        # Get or create documents collection
        try:
            collection = get_collection('documents')
        except:
            client = get_chroma_client()
            collection = client.create_collection(name="documents")
        
        # Add documents
        collection.add(
            documents=data.documents,
            metadatas=data.metadatas,
            ids=data.ids
        )
        
        return {"status": "success", "uploaded": len(data.ids)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
