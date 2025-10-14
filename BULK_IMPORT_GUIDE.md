# 📚 Bulk Import Guide for Northeastern University Chatbot

## Overview

The `bulk_import.py` script provides a powerful and flexible way to import large amounts of data into your ChromaDB database from various file formats.

## Supported Formats

✅ **JSON** - Structured data with metadata  
✅ **CSV** - Spreadsheet/tabular data  
✅ **TXT** - Plain text documents  
✅ **Directory** - Batch import multiple files at once

---

## Quick Start

### 1️⃣ Import a JSON File

```bash
python bulk_import.py --json example_data_json.json
```

### 2️⃣ Import a CSV File

```bash
python bulk_import.py --csv example_data.csv
```

### 3️⃣ Import a Text File

```bash
python bulk_import.py --txt my_document.txt
```

### 4️⃣ Import Entire Directory

```bash
python bulk_import.py --directory ./data_folder --recursive
```

---

## File Format Specifications

### 📄 JSON Format

**Structure:**
```json
[
  {
    "title": "Document Title",
    "content": "The main content of the document...",
    "source_url": "https://example.edu/page",
    "metadata": {
      "department": "Computer Science",
      "program_type": "undergraduate",
      "custom_field": "value"
    }
  }
]
```

**Required Fields:**
- `content` - The main text content (required)

**Optional Fields:**
- `title` - Document title (defaults to "Document N")
- `source_url` - Original URL or identifier (defaults to auto-generated)
- `metadata` - Dictionary of additional metadata

**Example:**
See `example_data_json.json` for a complete example.

---

### 📊 CSV Format

**Structure:**
```csv
title,content,source_url,field1,field2
"Title","Content...","https://example.edu","value1","value2"
```

**Required Columns:**
- `content` - The main text content

**Optional Columns:**
- `title` - Document title
- `source_url` - Original URL
- Any other columns become metadata automatically

**Custom Column Names:**
```bash
python bulk_import.py --csv data.csv \
  --title-col "document_name" \
  --content-col "text" \
  --url-col "link"
```

**Example:**
See `example_data.csv` for a complete example.

---

### 📝 TXT Format

**Structure:**
Simple plain text files. Each file becomes one document.

**Features:**
- Filename becomes the title (can be overridden)
- Entire file content becomes the document content
- Automatically tracks file size and import metadata

---

## Advanced Usage

### Import for Different University

```bash
python bulk_import.py --json data.json \
  --university "Harvard University" \
  --url "https://www.harvard.edu"
```

### Import Multiple Sources

```bash
# Import JSON and CSV in one command
python bulk_import.py --json data.json --csv more_data.csv
```

### Batch Import from Directory

```bash
# Import all supported files from a directory (non-recursive)
python bulk_import.py --directory ./data

# Import including subdirectories
python bulk_import.py --directory ./data --recursive
```

---

## Data Preparation Tips

### ✅ Best Practices

1. **Clean Your Data**
   - Remove duplicates before import
   - Ensure encoding is UTF-8
   - Validate JSON/CSV format

2. **Organize Content**
   - Group related documents
   - Use meaningful titles
   - Include relevant metadata

3. **Metadata Strategy**
   - Add `department` for categorization
   - Add `program_type` (undergraduate, graduate, etc.)
   - Add `category` for filtering
   - Add `last_updated` dates

4. **Content Quality**
   - Ensure content is meaningful (not just URLs)
   - Break large documents into logical sections
   - Remove HTML tags or formatting artifacts

### ❌ Common Pitfalls to Avoid

- Empty content fields
- Inconsistent data types in CSV
- Special characters without proper encoding
- Extremely large files (>100MB)

---

## Creating Your Data Files

### From Excel/Google Sheets

1. Prepare your data with columns:
   - `title` - Document title
   - `content` - Main text content
   - `source_url` - Original source
   - Additional metadata columns

2. Export as CSV:
   - File → Download → CSV
   - Save with UTF-8 encoding

3. Import:
   ```bash
   python bulk_import.py --csv exported_data.csv
   ```

### From Database Export

**Example: PostgreSQL to JSON**
```sql
COPY (
  SELECT json_agg(row_to_json(t))
  FROM (
    SELECT title, content, url as source_url
    FROM documents
  ) t
) TO '/path/to/export.json';
```

### From Web Scraping

If you have scraped data, format it as JSON:
```python
import json

scraped_data = [
    {
        "title": page.title,
        "content": page.text,
        "source_url": page.url,
        "metadata": {
            "scraped_date": page.date,
            "page_type": page.type
        }
    }
    for page in scraped_pages
]

with open('scraped_data.json', 'w') as f:
    json.dump(scraped_data, f, indent=2)
```

---

## Verification After Import

### Check Document Count

```bash
python -c "from services.shared.chroma_service import chroma_service; print(f'Total documents: {chroma_service.get_collection_count(\"documents\"):,}')"
```

### Search for Imported Documents

```python
from services.shared.chroma_service import chroma_service

# Search for documents
results = chroma_service.search_documents("computer science", n_results=5)

for doc, distance in results:
    print(f"Title: {doc.title}")
    print(f"URL: {doc.source_url}")
    print(f"Distance: {distance}")
    print("-" * 50)
```

### Verify Specific University

```python
from services.shared.chroma_service import chroma_service

# Get documents for specific university
university = chroma_service.get_university_by_name("Northeastern University")
docs = chroma_service.get_all_documents(university_id=university.id, limit=10)

print(f"Found {len(docs)} documents")
for doc in docs[:5]:
    print(f"- {doc.title}")
```

---

## Troubleshooting

### Issue: "No documents imported"
- Check file encoding (must be UTF-8)
- Validate JSON/CSV format
- Ensure `content` field is present and not empty

### Issue: "CSV column not found"
- Use `--title-col`, `--content-col`, `--url-col` to specify column names
- Check for typos in column names

### Issue: "University not created"
- Check database connection
- Ensure ChromaDB is running
- Verify university name doesn't have special characters

### Issue: "Import is slow"
- Normal for large datasets (embeddings generation takes time)
- Consider breaking into smaller batches
- Use batch import feature (imports show progress)

---

## Performance Considerations

**Import Speed:**
- JSON: ~10-50 documents/second
- CSV: ~10-50 documents/second
- TXT: ~5-20 documents/second

**Factors Affecting Speed:**
- Document size
- Number of documents
- Metadata complexity
- System resources

**Optimization Tips:**
- Import during off-peak hours
- Close other applications
- Use SSD storage for ChromaDB

---

## Example Workflows

### Workflow 1: Course Catalog Import

```bash
# 1. Export courses from university system to CSV
# 2. Clean data in Excel
# 3. Save as courses.csv with columns:
#    - title (course name)
#    - content (course description)
#    - source_url (catalog URL)
#    - department
#    - credits

# 4. Import
python bulk_import.py --csv courses.csv
```

### Workflow 2: FAQ Import

```bash
# 1. Create JSON file with Q&A pairs
# 2. Format as:
{
  "title": "Question",
  "content": "Answer",
  "metadata": {"category": "admissions"}
}

# 3. Import
python bulk_import.py --json faq.json
```

### Workflow 3: Multi-Source Import

```bash
# Import from multiple sources in sequence
python bulk_import.py --directory ./admissions_data --recursive
python bulk_import.py --directory ./academic_programs --recursive
python bulk_import.py --json supplemental_info.json
```

---

## Integration with Chatbot

After importing, your documents are immediately available for:
- ✅ Semantic search
- ✅ RAG (Retrieval-Augmented Generation)
- ✅ Q&A responses
- ✅ Enhanced GPU chatbot queries

Test your imports:
```bash
# Start the chatbot
python quick_start_enhanced_gpu.py

# Ask questions about imported content
# Example: "What is the Computer Science program?"
```

---

## Support

For issues or questions:
1. Check error messages in import summary
2. Verify file format matches examples
3. Check `chroma.log` for detailed errors
4. Review ChromaDB status

---

**📊 You're ready to import data! Start with the example files provided:**
- `example_data_json.json` - JSON format example
- `example_data.csv` - CSV format example

```bash
# Try it now!
python bulk_import.py --json example_data_json.json
```

