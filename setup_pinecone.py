#!/usr/bin/env python3
"""
Setup Pinecone API key and test connection
"""

import os
import sys
from pathlib import Path

def setup_api_key():
    """Setup Pinecone API key"""
    print("🌲 Pinecone Setup")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file found")
        
        # Read current .env
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if PINECONE_API_KEY exists
        if 'PINECONE_API_KEY=' in content:
            print("✅ PINECONE_API_KEY found in .env")
            
            # Extract current key
            for line in content.split('\n'):
                if line.startswith('PINECONE_API_KEY='):
                    current_key = line.split('=', 1)[1].strip()
                    if current_key and current_key != 'your_pinecone_api_key_here':
                        print(f"🔑 Current API key: {current_key[:10]}...")
                        return current_key
                    break
        
        print("⚠️  PINECONE_API_KEY not set or invalid")
    else:
        print("⚠️  .env file not found")
    
    # Get API key from user
    print("\n📝 Please enter your Pinecone API key:")
    print("   You can get it from: https://app.pinecone.io/")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return None
    
    # Update .env file
    if env_file.exists():
        # Update existing .env
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add PINECONE_API_KEY
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('PINECONE_API_KEY='):
                lines[i] = f'PINECONE_API_KEY={api_key}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'PINECONE_API_KEY={api_key}\n')
        
        with open(env_file, 'w') as f:
            f.writelines(lines)
    else:
        # Create new .env file
        with open(env_file, 'w') as f:
            f.write(f'PINECONE_API_KEY={api_key}\n')
            f.write('OPENAI_API_KEY=your_openai_api_key_here\n')
    
    print("✅ API key saved to .env file")
    return api_key

def test_pinecone_connection(api_key):
    """Test Pinecone connection"""
    print("\n🧪 Testing Pinecone connection...")
    
    try:
        from pinecone import Pinecone
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        
        # List indexes
        indexes = pc.list_indexes()
        print(f"✅ Connected to Pinecone successfully!")
        print(f"📊 Found {len(indexes)} indexes:")
        
        for index in indexes:
            print(f"  - {index.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Pinecone: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Northeastern University Chatbot - Pinecone Setup")
    print("=" * 60)
    
    # Setup API key
    api_key = setup_api_key()
    if not api_key:
        return
    
    # Test connection
    if test_pinecone_connection(api_key):
        print("\n🎉 Pinecone setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run: python scrape_to_pinecone.py")
        print("2. This will scrape Northeastern University websites")
        print("3. Store the data directly in Pinecone")
    else:
        print("\n❌ Pinecone setup failed")
        print("Please check your API key and try again")

if __name__ == "__main__":
    main()
