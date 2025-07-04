"""
Purge all non-Northeastern universities and their documents from ChromaDB.
Run this script from the project root.
"""
from services.shared.chroma_service import ChromaService

KEEP_DOMAIN = "northeastern.edu"

cs = ChromaService()

# 1. Get all universities
universities = cs.get_all_universities()

# 2. Find Northeastern university IDs
northeastern_univ_ids = [u.id for u in universities if KEEP_DOMAIN in u.base_url]
print(f"[INFO] Keeping {len(northeastern_univ_ids)} Northeastern university(ies):")
for u in universities:
    if u.id in northeastern_univ_ids:
        print(f"  - {u.name} ({u.base_url})")

# 3. Delete all other universities
for u in universities:
    if u.id not in northeastern_univ_ids:
        print(f"[DELETE] Removing university: {u.name} ({u.base_url})")
        cs.delete_university(u.id)

# 4. Get all documents
all_docs = cs.search_documents(query="", n_results=10000)
print(f"[INFO] Found {len(all_docs)} total documents.")

# 5. Delete documents not belonging to Northeastern
removed = 0
for doc, _ in all_docs:
    if doc.university_id not in northeastern_univ_ids:
        print(f"[DELETE] Removing document: {doc.title} (university_id={doc.university_id})")
        cs.delete_document(doc.id)
        removed += 1

print(f"[DONE] Removed {removed} documents not related to Northeastern.")
print("[OK] Database now contains only Northeastern University data.") 