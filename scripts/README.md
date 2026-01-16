# Scripts

Utility scripts for the WE_GO_MARS project.

## Knowledge Base Ingestion

### `ingest_knowledge_base.py`

Batch ingests all markdown files from the data directory into the RAG knowledge base (Qdrant).

**Features:**
- Recursively finds all `.md` files in the data directory
- Chunks documents using markdown-aware splitting (H1 headers + token-based overlap)
- Generates hybrid embeddings (dense OpenAI + sparse BM25)
- Uploads to Qdrant with full metadata tracking
- Progress reporting and error handling
- Support for skipping already-ingested files

**Usage:**

```bash
# Basic usage - ingest all files from data/
python scripts/ingest_knowledge_base.py

# Ingest from custom directory
python scripts/ingest_knowledge_base.py --data-dir /path/to/docs

# Skip files already in the knowledge base (faster re-runs)
python scripts/ingest_knowledge_base.py --skip-existing

# Smaller batch size for more frequent progress updates
python scripts/ingest_knowledge_base.py --batch-size 5

# Dry run to see what would be ingested
python scripts/ingest_knowledge_base.py --dry-run

# Combine options
python scripts/ingest_knowledge_base.py --data-dir data --skip-existing --batch-size 3
```

**Requirements:**
- Qdrant must be running (via `docker-compose up qdrant`)
- OpenAI API key must be set in `.env`
- All dependencies from `pyproject.toml` must be installed

**Output:**
The script provides detailed logging including:
- Files being processed
- Number of chunks created per file
- Progress updates every N files (configurable)
- Final statistics summary (total files, successes, failures, chunks)

**Example Output:**
```
2025-01-16 10:30:00 - INFO - Initialized ingester for directory: data
2025-01-16 10:30:00 - INFO - Qdrant host: localhost:6333
2025-01-16 10:30:00 - INFO - Found 42 markdown files

============================================================
Starting ingestion of 42 files
============================================================

2025-01-16 10:30:01 - INFO - Ingesting: data/README.md
2025-01-16 10:30:03 - INFO -   ✓ Successfully ingested 8 chunks from README.md
2025-01-16 10:30:03 - INFO - Ingesting: data/specs/radiation-shielding/README.md
2025-01-16 10:30:05 - INFO -   ✓ Successfully ingested 12 chunks from README.md
...

============================================================
INGESTION COMPLETE
============================================================
Total files found:    42
Successfully ingested: 42
Skipped (existing):   0
Failed:               0
Total chunks created: 487
============================================================
```

**Error Handling:**
- Individual file failures don't stop the batch process
- Failed files are logged with error details
- Exit code indicates success (0) or failures occurred (1)

**Chunking Strategy:**
Uses the `LiteratureStore._chunk_markdown()` method:
- Primary split on H1 headers (`# Title`)
- Secondary split on token limits (max 512 tokens, 50 token overlap)
- Preserves document metadata and source tracking

**Search After Ingestion:**
Once ingested, documents can be queried using:
- The `RetrieverAgent` in the codebase
- Direct `LiteratureStore.search(query, top_k=5)` calls
- Hybrid search combining semantic similarity (dense) + keyword matching (sparse)
