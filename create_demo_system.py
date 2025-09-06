#!/usr/bin/env python3
"""
Create a demo system with sample Northeastern University data
"""

import os
import sys
from pathlib import Path

# Add services to path
sys.path.append('services/shared')

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    print("✅ Required modules imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def create_demo_data():
    """Create demo data for Northeastern University"""
    
    demo_documents = [
        {
            'id': 'northeastern_admissions_1',
            'title': 'Undergraduate Admissions - Northeastern University',
            'url': 'https://www.northeastern.edu/admissions/',
            'content': 'Northeastern University offers a comprehensive undergraduate admissions process. We seek students who demonstrate academic excellence, leadership potential, and a commitment to making a positive impact. Our admissions requirements include a completed application, official transcripts, standardized test scores (SAT or ACT), letters of recommendation, and a personal essay. The application deadline for regular decision is January 1st, and early decision applications are due November 1st. We also offer early action with a deadline of November 1st.'
        },
        {
            'id': 'northeastern_coop_1',
            'title': 'Co-op Program - Northeastern University',
            'url': 'https://www.northeastern.edu/co-op/',
            'content': 'Northeastern University\'s co-op program is one of the largest and most innovative in the world. Students alternate between academic study and full-time professional work experience. The program provides students with up to 18 months of professional experience before graduation. Co-op opportunities are available in over 3,000 companies across the United States and internationally. Students typically complete 2-3 co-op experiences during their time at Northeastern, gaining valuable real-world experience and building professional networks.'
        },
        {
            'id': 'northeastern_tuition_1',
            'title': 'Tuition and Financial Aid - Northeastern University',
            'url': 'https://www.northeastern.edu/financial-aid/',
            'content': 'Northeastern University is committed to making education accessible through comprehensive financial aid programs. For the 2024-2025 academic year, undergraduate tuition is $62,000 per year. Room and board costs approximately $17,000 per year. The university offers need-based financial aid, merit scholarships, and work-study programs. Over 80% of students receive some form of financial assistance. Students are encouraged to complete the FAFSA and CSS Profile to be considered for all available aid programs.'
        },
        {
            'id': 'northeastern_housing_1',
            'title': 'Campus Housing - Northeastern University',
            'url': 'https://www.northeastern.edu/housing/',
            'content': 'Northeastern University offers a variety of on-campus housing options for students. First-year students are guaranteed housing and typically live in traditional residence halls. Upperclass students can choose from apartment-style living, suite-style rooms, or traditional residence halls. The university has 15 residence halls across the Boston campus, including the new East Village complex. All residence halls are equipped with modern amenities including high-speed internet, study lounges, and laundry facilities. Housing applications are typically due in early spring for the following academic year.'
        },
        {
            'id': 'northeastern_programs_1',
            'title': 'Academic Programs - Northeastern University',
            'url': 'https://www.northeastern.edu/academics/',
            'content': 'Northeastern University offers over 200 undergraduate and graduate programs across nine colleges and schools. Our most popular programs include Business Administration, Computer Science, Engineering, Health Sciences, and Liberal Arts. The university is known for its experiential learning approach, combining rigorous academics with real-world experience through co-op programs, research opportunities, and global experiences. Students can also pursue interdisciplinary studies and create custom majors to meet their unique academic and career goals.'
        },
        {
            'id': 'northeastern_international_1',
            'title': 'International Students - Northeastern University',
            'url': 'https://www.northeastern.edu/international/',
            'content': 'Northeastern University welcomes international students from over 140 countries. The university provides comprehensive support services including visa assistance, orientation programs, and cultural integration support. International students must demonstrate English proficiency through TOEFL, IELTS, or Duolingo scores. The university offers English language programs for students who need additional language support. International students are eligible for merit-based scholarships and can participate in all university programs including co-op experiences.'
        }
    ]
    
    return demo_documents

def load_demo_data_to_chromadb():
    """Load demo data into ChromaDB"""
    print("📚 Loading demo data to ChromaDB...")
    
    try:
        # Connect to ChromaDB
        client = chromadb.PersistentClient(
            path="chroma_data",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create documents collection
        try:
            collection = client.get_collection(name="documents")
            print("✅ Using existing documents collection")
        except:
            collection = client.create_collection(name="documents")
            print("✅ Created new documents collection")
        
        # Load embedding model
        print("🔄 Loading embedding model...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get demo data
        demo_documents = create_demo_data()
        
        # Prepare data for ChromaDB
        ids = []
        documents_text = []
        metadatas = []
        embeddings = []
        
        for doc in demo_documents:
            ids.append(doc['id'])
            documents_text.append(doc['content'])
            metadatas.append({
                'title': doc['title'],
                'url': doc['url'],
                'source_url': doc['url']
            })
            
            # Generate embedding
            embedding = embedding_model.encode([doc['content']])[0].tolist()
            embeddings.append(embedding)
        
        # Add to ChromaDB
        print("💾 Adding demo documents to ChromaDB...")
        collection.add(
            ids=ids,
            documents=documents_text,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        print(f"✅ Successfully loaded {len(demo_documents)} demo documents to ChromaDB")
        return True
        
    except Exception as e:
        print(f"❌ Error loading demo data: {e}")
        return False

def test_demo_data():
    """Test that the demo data was loaded correctly"""
    print("🧪 Testing demo data...")
    
    try:
        client = chromadb.PersistentClient(
            path="chroma_data",
            settings=Settings(anonymized_telemetry=False)
        )
        
        collection = client.get_collection(name="documents")
        
        # Test query
        results = collection.query(
            query_texts=["Northeastern University admissions"],
            n_results=3
        )
        
        if results['ids'] and results['ids'][0]:
            print(f"✅ Found {len(results['ids'][0])} results for test query")
            
            # Show results
            for i, (doc_id, metadata) in enumerate(zip(results['ids'][0], results['metadatas'][0])):
                print(f"📄 {i+1}. {metadata.get('title', 'No title')}")
                print(f"   URL: {metadata.get('url', 'No URL')}")
                print(f"   ID: {doc_id}")
            
            return True
        else:
            print("❌ No results found for test query")
            return False
            
    except Exception as e:
        print(f"❌ Error testing demo data: {e}")
        return False

def main():
    print("🎓 Creating Demo Northeastern University Chatbot System")
    print("=" * 60)
    
    # Load demo data
    if load_demo_data_to_chromadb():
        # Test the loaded data
        if test_demo_data():
            print("\n🎉 Demo system created successfully!")
            print("✅ ChromaDB contains sample Northeastern University documents")
            print("✅ URLs are properly configured")
            print("✅ Ready to use with the fixed chatbot")
            print("\n💡 The demo system includes information about:")
            print("  • Undergraduate admissions")
            print("  • Co-op program")
            print("  • Tuition and financial aid")
            print("  • Campus housing")
            print("  • Academic programs")
            print("  • International student services")
        else:
            print("\n⚠️  Demo data loaded but test failed")
    else:
        print("\n❌ Demo data loading failed")

if __name__ == "__main__":
    main()
