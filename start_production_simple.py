#!/usr/bin/env python3
"""
Simple Production Startup Script
Uses Railway volumes for persistent ChromaDB storage
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def check_chromadb_connection():
    """Check ChromaDB connection with Railway volume"""
    try:
        from services.shared.database import get_chroma_client, init_db
        
        # Test connection
        client = get_chroma_client()
        
        # Initialize collections
        init_db()
        
        # Test a simple query
        from services.shared.database import get_collection
        collection = get_collection('documents')
        result = collection.get()
        
        doc_count = len(result.get('ids', [])) if result else 0
        print(f"✅ ChromaDB connected successfully - {doc_count} documents available")
        
        # If no documents exist, create sample data
        if doc_count == 0:
            print("📝 No documents found, creating sample Northeastern data...")
            create_sample_northeastern_data()
            
            # Check again after creating sample data
            result = collection.get()
            doc_count = len(result.get('ids', [])) if result else 0
            print(f"✅ Sample data created - {doc_count} documents now available")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")
        print("💡 This is normal for first deployment - data will be created automatically")
        return True  # Allow startup even if no data exists

def create_sample_northeastern_data():
    """Create sample Northeastern University data"""
    try:
        from services.shared.database import get_chroma_client, get_collection
        
        client = get_chroma_client()
        
        # Sample Northeastern University documents
        sample_documents = [
            {
                "content": "Northeastern University is a private research university in Boston, Massachusetts. Founded in 1898, it offers undergraduate and graduate programs across nine colleges and schools.",
                "metadata": {"source": "university_overview", "title": "About Northeastern University"}
            },
            {
                "content": "Northeastern's co-op program is one of the largest and most innovative in the world. Students alternate between academic study and full-time professional experience, gaining up to 18 months of work experience before graduation.",
                "metadata": {"source": "coop_program", "title": "Co-op Program"}
            },
            {
                "content": "Admission to Northeastern University is competitive. The university considers academic performance, standardized test scores, extracurricular activities, and personal essays. The acceptance rate varies by program.",
                "metadata": {"source": "admissions", "title": "Admissions Information"}
            },
            {
                "content": "Northeastern offers over 200 undergraduate and graduate programs across various disciplines including engineering, business, health sciences, arts and sciences, computer science, and more.",
                "metadata": {"source": "academics", "title": "Academic Programs"}
            },
            {
                "content": "The university has multiple campuses including the main campus in Boston, as well as locations in Charlotte, Seattle, San Francisco, Toronto, and London for global learning opportunities.",
                "metadata": {"source": "campuses", "title": "Campus Locations"}
            },
            {
                "content": "Northeastern's research focuses on areas like health, security, and sustainability. The university receives over $200 million annually in research funding and has numerous research centers and institutes.",
                "metadata": {"source": "research", "title": "Research and Innovation"}
            },
            {
                "content": "Student life at Northeastern includes over 400 student organizations, Division I athletics, cultural events, and various campus activities. The university promotes diversity and inclusion.",
                "metadata": {"source": "student_life", "title": "Student Life"}
            },
            {
                "content": "Tuition and fees at Northeastern vary by program and level. The university offers financial aid, scholarships, and payment plans to help students afford their education.",
                "metadata": {"source": "financial", "title": "Tuition and Financial Aid"}
            },
            {
                "content": "Northeastern's career services help students with job placement, resume building, interview preparation, and networking opportunities. The co-op program provides valuable career experience.",
                "metadata": {"source": "career_services", "title": "Career Services"}
            },
            {
                "content": "The university has a strong alumni network with over 300,000 graduates worldwide. Alumni work in various industries and often help current students with networking and career opportunities.",
                "metadata": {"source": "alumni", "title": "Alumni Network"}
            }
        ]
        
        # Get or create documents collection
        try:
            collection = get_collection('documents')
        except:
            collection = client.create_collection(name="documents")
        
        # Prepare data for ChromaDB
        documents = [doc["content"] for doc in sample_documents]
        metadatas = [doc["metadata"] for doc in sample_documents]
        ids = [f"sample_{i}" for i in range(len(sample_documents))]
        
        # Add documents to collection
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Created {len(sample_documents)} sample documents")
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Start the production server with Railway volume storage"""
    
    # Check ChromaDB connection
    check_chromadb_connection()
    
    # Get configuration from environment variables
    port = int(os.environ.get("PORT", 8001))
    host = os.environ.get("HOST", "0.0.0.0")
    workers = int(os.environ.get("WORKERS", 1))
    log_level = os.environ.get("LOG_LEVEL", "info")
    
    print(f"🚀 Starting Enhanced GPU Chatbot in production mode...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"👥 Workers: {workers}")
    print(f"📝 Log Level: {log_level}")
    print(f"💾 Using Railway volume for persistent storage")
    
    # Import the FastAPI app
    try:
        from services.chat_service.enhanced_gpu_api import app
        print("✅ Enhanced GPU API imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Enhanced GPU API: {e}")
        print("💡 Make sure all dependencies are installed")
        sys.exit(1)
    
    # Start the server
    uvicorn.run(
        "services.chat_service.enhanced_gpu_api:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        access_log=True,
        reload=False,  # Disable reload in production
        server_header=False,  # Security: don't expose server info
        date_header=False,    # Security: don't expose date info
    )

if __name__ == "__main__":
    main() 