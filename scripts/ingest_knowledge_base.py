#!/usr/bin/env python3
"""
Script to ingest all markdown files from the data directory into the RAG knowledge base.

This script:
1. Recursively finds all .md files in the data directory
2. Chunks them using markdown-aware splitting (H1 headers + token-based)
3. Generates dense (OpenAI) and sparse (BM25) embeddings
4. Uploads to Qdrant literature collection with hybrid search support

Usage:
    python scripts/ingest_knowledge_base.py
    python scripts/ingest_knowledge_base.py --data-dir /path/to/data
    python scripts/ingest_knowledge_base.py --batch-size 5 --skip-existing
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse

from rag.literature_store import LiteratureStore, Document
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class KnowledgeBaseIngester:
    """Handles batch ingestion of markdown files into the RAG system."""

    def __init__(self, data_dir: str = "data", skip_existing: bool = False):
        """
        Initialize the ingester.

        Args:
            data_dir: Root directory containing markdown files
            skip_existing: If True, skip files that are already in the knowledge base
        """
        self.data_dir = Path(data_dir)
        self.skip_existing = skip_existing
        self.store = LiteratureStore()

        # Validate data directory exists
        if not self.data_dir.exists():
            raise ValueError(f"Data directory not found: {self.data_dir}")

        logger.info(f"Initialized ingester for directory: {self.data_dir}")
        logger.info(f"Qdrant host: {settings.qdrant_host}:{settings.qdrant_port}")

    def find_markdown_files(self) -> list[Path]:
        """
        Recursively find all markdown files in the data directory.

        Returns:
            List of Path objects for each .md file found
        """
        md_files = list(self.data_dir.rglob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")
        return sorted(md_files)  # Sort for consistent ordering

    def get_existing_documents(self) -> set[str]:
        """
        Get the set of document sources already in the knowledge base.

        Returns:
            Set of source paths (relative to data directory)
        """
        if not self.skip_existing:
            return set()

        try:
            # Scroll through all documents to get their sources
            # Note: This could be optimized with a dedicated query if needed
            existing_sources = set()

            # Query a batch to check if collection exists and has data
            result = self.store.client.scroll(
                collection_name="literature",
                limit=100,
                with_payload=True,
            )

            points, next_offset = result
            while points:
                for point in points:
                    if point.payload and "source" in point.payload:
                        existing_sources.add(point.payload["source"])

                # Check if there are more points
                if next_offset is None:
                    break

                result = self.store.client.scroll(
                    collection_name="literature",
                    offset=next_offset,
                    limit=100,
                    with_payload=True,
                )
                points, next_offset = result

            logger.info(f"Found {len(existing_sources)} existing documents in knowledge base")
            return existing_sources

        except Exception as e:
            logger.warning(f"Could not check existing documents: {e}")
            return set()

    def ingest_file(self, file_path: Path) -> tuple[bool, Optional[int]]:
        """
        Ingest a single markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            Tuple of (success, num_chunks)
        """
        try:
            # Get relative path for source tracking
            relative_path = file_path.relative_to(self.data_dir.parent)
            source = str(relative_path)

            logger.info(f"Ingesting: {source}")

            # Use the existing ingest_file method from LiteratureStore
            document = self.store.ingest_file(str(file_path))

            # Count chunks by checking how many were ingested
            # The ingest_file method returns the Document object
            # We need to count chunks that were created
            chunks = self.store._chunk_markdown(document)
            num_chunks = len(chunks)

            logger.info(f"  ✓ Successfully ingested {num_chunks} chunks from {file_path.name}")
            return True, num_chunks

        except Exception as e:
            logger.error(f"  ✗ Failed to ingest {file_path.name}: {e}")
            return False, None

    def ingest_all(self, batch_size: int = 10) -> dict:
        """
        Ingest all markdown files in the data directory.

        Args:
            batch_size: Number of files to process before logging progress

        Returns:
            Dictionary with ingestion statistics
        """
        files = self.find_markdown_files()

        if not files:
            logger.warning("No markdown files found to ingest")
            return {
                "total_files": 0,
                "ingested": 0,
                "skipped": 0,
                "failed": 0,
                "total_chunks": 0,
            }

        # Get existing documents if skip_existing is enabled
        existing_sources = self.get_existing_documents()

        stats = {
            "total_files": len(files),
            "ingested": 0,
            "skipped": 0,
            "failed": 0,
            "total_chunks": 0,
        }

        logger.info(f"\n{'='*60}")
        logger.info(f"Starting ingestion of {len(files)} files")
        logger.info(f"{'='*60}\n")

        for idx, file_path in enumerate(files, 1):
            # Check if file already exists in knowledge base
            relative_path = str(file_path.relative_to(self.data_dir.parent))

            if self.skip_existing and relative_path in existing_sources:
                logger.info(f"[{idx}/{len(files)}] Skipping (already exists): {file_path.name}")
                stats["skipped"] += 1
                continue

            # Ingest the file
            success, num_chunks = self.ingest_file(file_path)

            if success:
                stats["ingested"] += 1
                stats["total_chunks"] += num_chunks or 0
            else:
                stats["failed"] += 1

            # Log progress every batch_size files
            if idx % batch_size == 0:
                logger.info(f"\n--- Progress: {idx}/{len(files)} files processed ---\n")

        # Final summary
        logger.info(f"\n{'='*60}")
        logger.info("INGESTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total files found:    {stats['total_files']}")
        logger.info(f"Successfully ingested: {stats['ingested']}")
        logger.info(f"Skipped (existing):   {stats['skipped']}")
        logger.info(f"Failed:               {stats['failed']}")
        logger.info(f"Total chunks created: {stats['total_chunks']}")
        logger.info(f"{'='*60}\n")

        return stats


def main():
    """Main entry point for the ingestion script."""
    parser = argparse.ArgumentParser(
        description="Ingest markdown files into the RAG knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest all files from default data directory
  python scripts/ingest_knowledge_base.py

  # Ingest from custom directory
  python scripts/ingest_knowledge_base.py --data-dir /path/to/docs

  # Skip files that are already in the knowledge base
  python scripts/ingest_knowledge_base.py --skip-existing

  # Process in smaller batches with custom batch size
  python scripts/ingest_knowledge_base.py --batch-size 5
        """,
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Root directory containing markdown files (default: data)",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of files to process before logging progress (default: 10)",
    )

    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files that are already ingested in the knowledge base",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be ingested without actually ingesting them",
    )

    args = parser.parse_args()

    try:
        # Initialize ingester
        ingester = KnowledgeBaseIngester(
            data_dir=args.data_dir,
            skip_existing=args.skip_existing,
        )

        # Dry run mode - just list files
        if args.dry_run:
            files = ingester.find_markdown_files()
            logger.info(f"\nDRY RUN: Would ingest {len(files)} files:")
            for file_path in files:
                relative_path = file_path.relative_to(ingester.data_dir.parent)
                logger.info(f"  - {relative_path}")
            return 0

        # Perform actual ingestion
        stats = ingester.ingest_all(batch_size=args.batch_size)

        # Return exit code based on results
        if stats["failed"] > 0:
            logger.warning(f"Completed with {stats['failed']} failures")
            return 1
        else:
            logger.info("All files ingested successfully!")
            return 0

    except KeyboardInterrupt:
        logger.warning("\n\nIngestion interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"\n\nFatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
