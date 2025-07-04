"""
Reset ChromaDB: Delete all main collections (universities, documents, scrape_logs, chat_sessions, chat_messages).
Run this script from the project root. All data will be lost!
"""
from services.shared.chroma_service import ChromaService
from services.shared.models import COLLECTIONS

cs = ChromaService()

for name in COLLECTIONS.values():
    print(f"[DELETE] Deleting collection: {name}")
    cs.delete_collection(name)

print("[OK] All ChromaDB collections deleted. Database is now empty.") 