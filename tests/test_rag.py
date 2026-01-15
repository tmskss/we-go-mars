"""
Tests for the RAG (Retrieval-Augmented Generation) module.

Tests cover:
- Embedding generation (dense and sparse)
- Markdown chunking
- Document ingestion
- Hybrid search with DBSF fusion
"""

import os
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from src.rag.embeddings import EmbeddingService, SparseEmbeddingService
from src.rag.literature_store import Document, LiteratureStore


class TestEmbeddingService:
    """Tests for the dense embedding service."""

    @pytest.fixture
    def service(self):
        return EmbeddingService()

    def test_embed_single(self, service):
        """Test embedding a single text."""
        text = "This is a test sentence about Mars exploration."
        embedding = service.embed(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 1536  # text-embedding-3-small dimension
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_batch(self, service):
        """Test batch embedding multiple texts."""
        texts = [
            "First document about space.",
            "Second document about research.",
            "Third document about AI.",
        ]
        embeddings = service.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(e) == 1536 for e in embeddings)

    def test_embed_batch_empty(self, service):
        """Test batch embedding with empty list."""
        embeddings = service.embed_batch([])
        assert embeddings == []


class TestSparseEmbeddingService:
    """Tests for the BM25 sparse embedding service."""

    @pytest.fixture
    def service(self):
        return SparseEmbeddingService()

    def test_embed_single(self, service):
        """Test sparse embedding a single text."""
        text = "This is a test sentence about Mars exploration."
        embedding = service.embed(text)

        assert hasattr(embedding, "indices")
        assert hasattr(embedding, "values")
        assert len(embedding.indices) == len(embedding.values)
        assert len(embedding.indices) > 0  # Should have some tokens

    def test_embed_batch(self, service):
        """Test batch sparse embedding."""
        texts = [
            "First document about space.",
            "Second document about research.",
        ]
        embeddings = service.embed_batch(texts)

        assert len(embeddings) == 2
        assert all(hasattr(e, "indices") for e in embeddings)

    def test_query_embed(self, service):
        """Test query-optimized sparse embedding."""
        query = "What is Mars exploration?"
        embedding = service.query_embed(query)

        assert hasattr(embedding, "indices")
        assert len(embedding.indices) > 0


class TestLiteratureStore:
    """Tests for the literature store with hybrid search."""

    @pytest.fixture
    def store(self):
        return LiteratureStore()

    def test_chunk_markdown_simple(self, store):
        """Test chunking a simple markdown document."""
        doc = Document(
            id=uuid4(),
            title="Test Document",
            content="# Section One\n\nContent for section one.\n\n# Section Two\n\nContent for section two.",
            source="test.md",
            metadata={},
        )

        chunks = store._chunk_markdown(doc)

        assert len(chunks) == 2
        assert "Section One" in chunks[0].content
        assert "Section Two" in chunks[1].content

    def test_chunk_markdown_no_headings(self, store):
        """Test chunking document without H1 headings."""
        doc = Document(
            id=uuid4(),
            title="No Headings",
            content="Just some plain text content without any markdown headings.",
            source="test.md",
            metadata={},
        )

        chunks = store._chunk_markdown(doc)

        assert len(chunks) == 1
        assert chunks[0].content == doc.content.strip()

    def test_ingest_document(self, store):
        """Test ingesting a document into the store."""
        doc = Document(
            id=uuid4(),
            title="Test Ingestion",
            content="# Test\n\nThis is a test document for ingestion.",
            source="test.md",
            metadata={"type": "test"},
        )

        num_chunks = store.ingest_document(doc)

        assert num_chunks >= 1

    def test_search_returns_results(self, store):
        """Test that search returns results after ingestion."""
        # First ingest a document
        doc = Document(
            id=uuid4(),
            title="Mars Research",
            content="# Mars Exploration\n\nMars is the fourth planet from the Sun. "
            "It is often called the Red Planet due to its reddish appearance.",
            source="mars.md",
            metadata={},
        )
        store.ingest_document(doc)

        # Search for it
        results = store.search("What color is Mars?", top_k=3)

        assert len(results) > 0
        assert results[0].score > 0
        assert "Mars" in results[0].chunk.content or "Mars" in results[0].document_title


class TestReadmeIngestion:
    """Test ingesting the actual README.md file."""

    @pytest.fixture
    def store(self):
        return LiteratureStore()

    def test_ingest_readme(self, store):
        """Test ingesting the project README.md."""
        readme_path = Path(__file__).parent.parent / "README.md"

        if not readme_path.exists():
            pytest.skip("README.md not found")

        doc = store.ingest_file(str(readme_path))

        assert doc.title == "We Go Mars"
        assert doc.source == str(readme_path)

    def test_search_readme_content(self, store):
        """Test searching for content from README after ingestion."""
        readme_path = Path(__file__).parent.parent / "README.md"

        if not readme_path.exists():
            pytest.skip("README.md not found")

        # Ingest the README
        store.ingest_file(str(readme_path))

        # Search for specific content
        results = store.search("multi-agent orchestration", top_k=5)

        assert len(results) > 0
        # Should find content about multi-agent systems
        found_relevant = any(
            "agent" in r.chunk.content.lower() or "orchestration" in r.chunk.content.lower()
            for r in results
        )
        assert found_relevant, "Should find content about agents/orchestration"

    def test_search_readme_hybrid(self, store):
        """Test hybrid search combines semantic and keyword matching."""
        readme_path = Path(__file__).parent.parent / "README.md"

        if not readme_path.exists():
            pytest.skip("README.md not found")

        store.ingest_file(str(readme_path))

        # Search with a semantic query
        results = store.search("how to install the project", top_k=5)

        assert len(results) > 0
        # Should find setup/installation content
        found_setup = any(
            "pip" in r.chunk.content.lower()
            or "install" in r.chunk.content.lower()
            or "setup" in r.chunk.content.lower()
            for r in results
        )
        assert found_setup, "Hybrid search should find installation instructions"


if __name__ == "__main__":
    # Run a quick manual test
    print("Initializing LiteratureStore...")
    store = LiteratureStore()

    print("\nIngesting README.md...")
    readme_path = Path(__file__).parent.parent / "README.md"
    doc = store.ingest_file(str(readme_path))
    print(f"Ingested: {doc.title}")

    print("\nSearching for 'multi-agent orchestration'...")
    results = store.search("multi-agent orchestration", top_k=3)
    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} (score: {r.score:.3f}) ---")
        print(f"Title: {r.document_title}")
        print(f"Content: {r.chunk.content[:200]}...")

    print("\nSearching for 'how to install'...")
    results = store.search("how to install the project", top_k=3)
    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} (score: {r.score:.3f}) ---")
        print(f"Title: {r.document_title}")
        print(f"Content: {r.chunk.content[:200]}...")
