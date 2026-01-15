"""
Literature knowledge store using Qdrant.

Owner: [ASSIGN TEAMMATE]
"""

from dataclasses import dataclass
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from src.config import settings
from src.rag.embeddings import EmbeddingService


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

    id: str
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
    - Embedding storage
    - Similarity search
    """

    COLLECTION_NAME = "literature"

    def __init__(self):
        """Initialize the literature store."""
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self.embeddings = EmbeddingService()
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create the collection if it doesn't exist."""
        # TODO: Implement collection creation
        # collections = self.client.get_collections()
        # if self.COLLECTION_NAME not in [c.name for c in collections.collections]:
        #     self.client.create_collection(
        #         collection_name=self.COLLECTION_NAME,
        #         vectors_config=VectorParams(
        #             size=1536,
        #             distance=Distance.COSINE,
        #         ),
        #     )
        pass

    async def ingest_document(self, document: Document) -> int:
        """
        Ingest a document into the store.

        Args:
            document: The document to ingest

        Returns:
            Number of chunks created
        """
        # TODO: Implement document ingestion
        # 1. Chunk the document
        # 2. Generate embeddings for each chunk
        # 3. Store in Qdrant

        raise NotImplementedError("Implement document ingestion")

    async def ingest_file(self, file_path: str) -> Document:
        """
        Ingest a file (PDF, Markdown, etc.) into the store.

        Args:
            file_path: Path to the file

        Returns:
            The created Document
        """
        # TODO: Implement file ingestion
        # 1. Read and parse file
        # 2. Extract text and metadata
        # 3. Create Document and ingest

        raise NotImplementedError("Implement file ingestion")

    async def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        """
        Search for relevant document chunks.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of retrieval results
        """
        # TODO: Implement search
        # 1. Embed the query
        # 2. Search Qdrant
        # 3. Return results

        raise NotImplementedError("Implement search")

    def _chunk_document(
        self,
        document: Document,
        chunk_size: int = 512,
        overlap: int = 50,
    ) -> list[DocumentChunk]:
        """
        Split document into chunks for embedding.

        Args:
            document: Document to chunk
            chunk_size: Target chunk size in tokens
            overlap: Overlap between chunks

        Returns:
            List of document chunks
        """
        # TODO: Implement chunking
        # Consider using tiktoken for token counting

        raise NotImplementedError("Implement document chunking")
