#!/usr/bin/env python3
"""
Upload existing ChromaDB data to Railway deployment
Simple solution using Railway's volume storage
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def upload_data_to_railway():
    """Upload data to Railway deployment via API"""
    
    # Get Railway URL from environment or user input
    railway_url = os.environ.get("RAILWAY_URL")
    if not railway_url:
        railway_url = input("Enter your Railway app URL (e.g., https://your-app.up.railway.app): ").strip()
    
    if not railway_url:
        print("❌ Railway URL is required")
        return False
    
    # Remove trailing slash
    railway_url = railway_url.rstrip('/')
    
    try:
        # Test connection
        print(f"🔗 Testing connection to {railway_url}...")
        response = requests.get(f"{railway_url}/health/enhanced", timeout=10)
        
        if response.status_code == 200:
            print("✅ Railway app is running")
        else:
            print(f"⚠️  Railway app responded with status {response.status_code}")
            print("💡 Make sure your Railway app is deployed and running")
            return False
            
    except Exception as e:
        print(f"❌ Could not connect to Railway app: {e}")
        print("💡 Make sure your Railway app is deployed and accessible")
        return False
    
    # Get local ChromaDB data
    try:
        import chromadb
        from chromadb.config import Settings
        
        local_data_path = project_root / "chroma_data"
        print(f"📁 Reading local ChromaDB data from {local_data_path}")
        
        local_client = chromadb.PersistentClient(
            path=str(local_data_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get documents collection
        collection = local_client.get_collection(name="documents")
        local_data = collection.get()
        
        if not local_data.get('ids') or len(local_data['ids']) == 0:
            print("⚠️  No documents found in local ChromaDB")
            return False
        
        documents = local_data.get('documents', [])
        metadatas = local_data.get('metadatas', [])
        ids = local_data.get('ids', [])
        
        print(f"📊 Found {len(documents)} documents to upload")
        
        # Upload data to Railway
        print("🔄 Uploading data to Railway...")
        
        # Prepare data for upload
        upload_data = {
            "documents": documents,
            "metadatas": metadatas,
            "ids": ids
        }
        
        # Upload in batches
        batch_size = 50
        total_uploaded = 0
        
        for i in range(0, len(documents), batch_size):
            batch_data = {
                "documents": documents[i:i+batch_size],
                "metadatas": metadatas[i:i+batch_size] if metadatas else [{}] * min(batch_size, len(documents) - i),
                "ids": ids[i:i+batch_size]
            }
            
            try:
                response = requests.post(
                    f"{railway_url}/upload-documents",
                    json=batch_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    uploaded_count = len(batch_data['ids'])
                    total_uploaded += uploaded_count
                    print(f"✅ Uploaded batch {i//batch_size + 1}: {uploaded_count} documents")
                else:
                    print(f"❌ Failed to upload batch {i//batch_size + 1}: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error uploading batch {i//batch_size + 1}: {e}")
                continue
        
        print(f"\n🎉 Upload completed!")
        print(f"📊 Total documents uploaded: {total_uploaded}")
        print(f"🌐 Data is now available in your Railway deployment")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_upload_endpoint():
    """Create a temporary upload endpoint for Railway"""
    print("🔧 Creating upload endpoint for Railway...")
    
    # Create a simple upload endpoint
    upload_endpoint_code = '''
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
'''
    
    # Save to a temporary file
    upload_file = project_root / "temp_upload_endpoint.py"
    with open(upload_file, 'w') as f:
        f.write(upload_endpoint_code)
    
    print("✅ Created temporary upload endpoint")
    print("💡 Add this to your Railway app to enable data upload")
    print(f"📁 File saved as: {upload_file}")
    
    return True

if __name__ == "__main__":
    print("🚀 Railway Data Upload Tool")
    print("=" * 50)
    
    # Check if Railway URL is set
    if not os.environ.get("RAILWAY_URL"):
        print("💡 Set RAILWAY_URL environment variable for automatic upload")
        print("   Example: $env:RAILWAY_URL='https://your-app.up.railway.app'")
    
    # Create upload endpoint first
    create_upload_endpoint()
    
    # Try to upload data
    print("\n" + "=" * 50)
    success = upload_data_to_railway()
    
    if success:
        print("\n🎯 Upload successful! Your Railway app now has your data.")
        print("💡 You can now remove the temporary upload endpoint")
    else:
        print("\n❌ Upload failed. Please check the errors above.")
        print("💡 Make sure your Railway app is running and accessible") 