"""
Literature knowledge store using Qdrant.

Owner: [ASSIGN TEAMMATE]
"""

import re
from dataclasses import dataclass
from uuid import UUID, uuid4, uuid5, NAMESPACE_DNS

import tiktoken
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
    Modifier,
    PointStruct,
    Prefetch,
    FusionQuery,
    Fusion,
)

from src.config import settings
from src.rag.embeddings import EmbeddingService, SparseEmbeddingService


@dataclass
class Document:
    """A document in the literature store."""

    id: UUID
    title: str
    content: str
    source: str  # File path or URL
    metadata: dict


@dataclass
class DocumentChunk:
    """A chunk of a document for embedding."""

    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    metadata: dict


@dataclass
class RetrievalResult:
    """Result from a retrieval query."""

    chunk: DocumentChunk
    score: float
    document_title: str


class LiteratureStore:
    """
    Vector store for literature/papers using Qdrant.

    Handles:
    - Document ingestion and chunking
    - Embedding storage (dense + sparse for hybrid search)
    - Hybrid similarity search with DBSF fusion
    """

    COLLECTION_NAME = "literature"
    DENSE_VECTOR_NAME = "dense"
    SPARSE_VECTOR_NAME = "sparse"

    def __init__(self):
        """Initialize the literature store."""
        if settings.qdrant_url:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
            )
        else:
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
        self.dense_embeddings = EmbeddingService()
        self.sparse_embeddings = SparseEmbeddingService()
        self._tokenizer = tiktoken.get_encoding("cl100k_base")
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create the collection if it doesn't exist."""
        collections = self.client.get_collections()
        if self.COLLECTION_NAME not in [c.name for c in collections.collections]:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config={
                    self.DENSE_VECTOR_NAME: VectorParams(
                        size=self.dense_embeddings.dimension,
                        distance=Distance.COSINE,
                    )
                },
                sparse_vectors_config={
                    self.SPARSE_VECTOR_NAME: SparseVectorParams(
                        modifier=Modifier.IDF,
                    )
                },
            )

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self._tokenizer.encode(text))

    def _chunk_markdown(
        self,
        document: Document,
        max_tokens: int = 512,
        overlap_tokens: int = 50,
    ) -> list[DocumentChunk]:
        """
        Split markdown document into chunks.

        Primary split: H1 headings (# )
        Secondary split: Token limit with overlap

        Args:
            document: Document to chunk
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Overlap between chunks when splitting by token limit

        Returns:
            List of document chunks
        """
        content = document.content
        chunks = []
        chunk_index = 0

        # Split on H1 headings (# at start of line)
        h1_pattern = r"(?=^# )"
        sections = re.split(h1_pattern, content, flags=re.MULTILINE)

        # Filter empty sections
        sections = [s.strip() for s in sections if s.strip()]

        for section in sections:
            section_tokens = self._count_tokens(section)

            if section_tokens <= max_tokens:
                # Section fits in one chunk
                chunks.append(
                    DocumentChunk(
                        id=uuid5(document.id, str(chunk_index)),
                        document_id=document.id,
                        content=section,
                        chunk_index=chunk_index,
                        metadata={
                            **document.metadata,
                            "source": document.source,
                            "title": document.title,
                        },
                    )
                )
                chunk_index += 1
            else:
                # Section too large, split by token limit with overlap
                sub_chunks = self._split_by_tokens(
                    section, max_tokens, overlap_tokens
                )
                for sub_chunk in sub_chunks:
                    chunks.append(
                        DocumentChunk(
                            id=uuid5(document.id, str(chunk_index)),
                            document_id=document.id,
                            content=sub_chunk,
                            chunk_index=chunk_index,
                            metadata={
                                **document.metadata,
                                "source": document.source,
                                "title": document.title,
                            },
                        )
                    )
                    chunk_index += 1

        return chunks

    def _split_by_tokens(
        self,
        text: str,
        max_tokens: int,
        overlap_tokens: int,
    ) -> list[str]:
        """
        Split text into chunks by token count with overlap.

        Args:
            text: Text to split
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of overlapping tokens between chunks

        Returns:
            List of text chunks
        """
        tokens = self._tokenizer.encode(text)
        chunks = []
        start = 0

        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunks.append(self._tokenizer.decode(chunk_tokens))

            if end >= len(tokens):
                break

            # Move start forward, keeping overlap
            start = end - overlap_tokens

        return chunks

    def ingest_document(self, document: Document) -> int:
        """
        Ingest a document into the store.

        Args:
            document: The document to ingest

        Returns:
            Number of chunks created
        """
        # Chunk the document
        chunks = self._chunk_markdown(document)

        if not chunks:
            return 0

        # Generate embeddings
        chunk_texts = [chunk.content for chunk in chunks]
        dense_vectors = self.dense_embeddings.embed_batch(chunk_texts)
        sparse_vectors = self.sparse_embeddings.embed_batch(chunk_texts)

        # Create points for Qdrant
        points = []
        for i, chunk in enumerate(chunks):
            points.append(
                PointStruct(
                    id=chunk.id,
                    vector={
                        self.DENSE_VECTOR_NAME: dense_vectors[i],
                        self.SPARSE_VECTOR_NAME: sparse_vectors[i],
                    },
                    payload={
                        "document_id": str(chunk.document_id),
                        "content": chunk.content,
                        "chunk_index": chunk.chunk_index,
                        **chunk.metadata,
                    },
                )
            )

        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

        return len(chunks)

    def ingest_file(self, file_path: str) -> Document:
        """
        Ingest a file (PDF, Markdown, etc.) into the store.

        Args:
            file_path: Path to the file

        Returns:
            The created Document
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract title from first H1 or filename
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.split("/")[-1]

        document = Document(
            id=uuid4(),
            title=title,
            content=content,
            source=file_path,
            metadata={"file_type": file_path.split(".")[-1]},
        )

        self.ingest_document(document)
        return document

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        """
        Search for relevant document chunks using hybrid search.

        Combines dense (semantic) and sparse (BM25 keyword) search
        with DBSF fusion.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of retrieval results
        """
        # Generate query embeddings
        dense_vector = self.dense_embeddings.embed(query)
        sparse_vector = self.sparse_embeddings.query_embed(query)

        # Hybrid search with DBSF fusion
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            prefetch=[
                Prefetch(
                    query=sparse_vector,
                    using=self.SPARSE_VECTOR_NAME,
                    limit=20,
                ),
                Prefetch(
                    query=dense_vector,
                    using=self.DENSE_VECTOR_NAME,
                    limit=20,
                ),
            ],
            query=FusionQuery(fusion=Fusion.DBSF),
            limit=top_k,
            with_payload=True,
        )

        # Convert to RetrievalResult
        retrieval_results = []
        for point in results.points:
            payload = point.payload
            chunk = DocumentChunk(
                id=UUID(str(point.id)),
                document_id=UUID(payload.get("document_id", str(uuid4()))),
                content=payload.get("content", ""),
                chunk_index=payload.get("chunk_index", 0),
                metadata={
                    k: v
                    for k, v in payload.items()
                    if k not in ["document_id", "content", "chunk_index", "title"]
                },
            )
            retrieval_results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=point.score,
                    document_title=payload.get("title", "Unknown"),
                )
            )

        return retrieval_results
