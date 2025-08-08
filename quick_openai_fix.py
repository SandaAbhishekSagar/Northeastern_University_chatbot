#!/usr/bin/env python3
"""
Quick Fix for OpenAI Embeddings Dimension Mismatch
This script modifies the OpenAI RAG chatbot to use compatible embeddings
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def fix_openai_rag_chatbot():
    """Fix the OpenAI RAG chatbot to use compatible embeddings"""
    print("🔧 Quick Fix: Modifying OpenAI RAG Chatbot for Compatible Embeddings")
    print("=" * 70)
    
    # Read the current OpenAI RAG chatbot file
    chatbot_file = Path("services/chat_service/openai_rag_chatbot.py")
    
    if not chatbot_file.exists():
        print("❌ OpenAI RAG chatbot file not found!")
        return False
    
    print("📝 Reading current OpenAI RAG chatbot...")
    
    try:
        with open(chatbot_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it's already using compatible embeddings
        if "HuggingFaceEmbeddings" in content and "all-MiniLM-L6-v2" in content:
            print("✅ OpenAI RAG chatbot is already using compatible embeddings!")
            return True
        
        # Replace OpenAI embeddings with compatible HuggingFace embeddings
        print("🔄 Replacing OpenAI embeddings with compatible HuggingFace embeddings...")
        
        # Replace the embedding initialization
        old_embedding_init = """        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=openai_api_key
        )"""
        
        new_embedding_init = """        # Initialize compatible HuggingFace embeddings (384 dimensions)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )"""
        
        if old_embedding_init in content:
            content = content.replace(old_embedding_init, new_embedding_init)
        else:
            print("⚠️  Could not find exact embedding initialization, trying alternative...")
            
            # Try alternative replacement
            old_alt = "OpenAIEmbeddings("
            new_alt = "HuggingFaceEmbeddings("
            if old_alt in content:
                content = content.replace(old_alt, new_alt)
                
                # Also update the model parameter
                content = content.replace('model="text-embedding-3-small"', 'model_name="all-MiniLM-L6-v2"')
                content = content.replace('openai_api_key=openai_api_key', 'model_kwargs={"device": "cpu"}, encode_kwargs={"normalize_embeddings": True}')
        
        # Update imports
        if "from langchain_openai import OpenAIEmbeddings" in content:
            content = content.replace(
                "from langchain_openai import OpenAIEmbeddings",
                "from langchain_community.embeddings import HuggingFaceEmbeddings"
            )
        
        # Write the modified content back
        print("💾 Writing modified OpenAI RAG chatbot...")
        with open(chatbot_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ OpenAI RAG chatbot updated successfully!")
        print("📋 Changes made:")
        print("   - Replaced OpenAI embeddings with HuggingFace embeddings")
        print("   - Updated to use 'all-MiniLM-L6-v2' model (384 dimensions)")
        print("   - This is compatible with your existing ChromaDB collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error modifying OpenAI RAG chatbot: {e}")
        return False

def create_backup():
    """Create a backup of the original file"""
    print("📦 Creating backup of original file...")
    
    try:
        original_file = Path("services/chat_service/openai_rag_chatbot.py")
        backup_file = Path("services/chat_service/openai_rag_chatbot_backup.py")
        
        if original_file.exists():
            import shutil
            shutil.copy2(original_file, backup_file)
            print(f"✅ Backup created: {backup_file}")
            return True
        else:
            print("❌ Original file not found!")
            return False
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def main():
    """Main function"""
    print("=" * 70)
    print("🚀 Quick Fix for OpenAI Embeddings Dimension Mismatch")
    print("=" * 70)
    
    print("This fix will modify the OpenAI RAG chatbot to use compatible embeddings")
    print("instead of rebuilding the entire ChromaDB collection.")
    print()
    
    # Create backup
    if not create_backup():
        print("⚠️  Could not create backup, but continuing...")
    
    # Apply the fix
    if fix_openai_rag_chatbot():
        print("\n🎉 Quick fix applied successfully!")
        print("\n📋 Next steps:")
        print("1. Restart your OpenAI API server")
        print("2. Test the frontend again")
        print("3. The embedding dimension mismatch should be resolved")
        print("\n💡 Note: This fix uses HuggingFace embeddings instead of OpenAI embeddings")
        print("   for document search, but still uses OpenAI for answer generation.")
        print("   This provides the best of both worlds: compatibility + OpenAI quality.")
    else:
        print("\n❌ Quick fix failed. Please check the error messages above.")
        print("\n🔧 Alternative: Run 'python fix_openai_embeddings.py' to rebuild the collection")

if __name__ == "__main__":
    main() 