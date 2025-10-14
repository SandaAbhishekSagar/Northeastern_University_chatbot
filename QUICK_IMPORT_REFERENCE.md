# 🚀 Quick Import Reference

## One-Line Commands

### Import JSON
```bash
python bulk_import.py --json your_file.json
```

### Import CSV
```bash
python bulk_import.py --csv your_file.csv
```

### Import TXT
```bash
python bulk_import.py --txt your_file.txt
```

### Import Directory
```bash
python bulk_import.py --directory ./your_folder --recursive
```

---

## File Format Requirements

### JSON
```json
[{"content": "Required field", "title": "Optional", "source_url": "Optional"}]
```

### CSV
```csv
content,title,source_url
"Required field","Optional","Optional"
```

### TXT
Any plain text file (entire file becomes one document)

---

## Common Options

```bash
# Different university
--university "Harvard" --url "https://harvard.edu"

# Custom CSV columns
--title-col "name" --content-col "text" --url-col "link"

# Multiple files at once
--json file1.json --csv file2.csv
```

---

## Quick Test

```bash
# Test with example files
python bulk_import.py --json example_data_json.json
python bulk_import.py --csv example_data.csv
python bulk_import.py --txt example_data.txt
```

---

## Verify Import

```bash
# Check document count
python -c "from services.shared.chroma_service import chroma_service; print(f'Documents: {chroma_service.get_collection_count(\"documents\"):,}')"
```

---

## Need Help?

```bash
python bulk_import.py --help
```

See **BULK_IMPORT_GUIDE.md** for detailed documentation.

