"""
Embedding generation service.

Owner: [ASSIGN TEAMMATE]
"""

from openai import OpenAI
from fastembed import SparseTextEmbedding
from qdrant_client.models import SparseVector

from src.config import settings


class EmbeddingService:
    """
    Service for generating text embeddings using OpenAI.

    Uses text-embedding-3-small by default for cost efficiency.
    """

    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize the embedding service.

        Args:
            model: The embedding model to use
        """
        self.model = model
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.dimension = 1536  # Default for text-embedding-3-small

    def embed(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]


class SparseEmbeddingService:
    """
    Service for generating BM25 sparse embeddings using FastEmbed.

    Used for keyword-based retrieval in hybrid search.
    """

    def __init__(self):
        """Initialize the sparse embedding service with BM25 model."""
        self.model = SparseTextEmbedding(model_name="Qdrant/bm25")

    def embed(self, text: str) -> SparseVector:
        """
        Generate sparse embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            SparseVector with indices and values
        """
        embedding = list(self.model.embed([text]))[0]
        return SparseVector(
            indices=embedding.indices.tolist(),
            values=embedding.values.tolist(),
        )

    def embed_batch(self, texts: list[str]) -> list[SparseVector]:
        """
        Generate sparse embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of SparseVector objects
        """
        if not texts:
            return []
        embeddings = list(self.model.embed(texts))
        return [
            SparseVector(
                indices=emb.indices.tolist(),
                values=emb.values.tolist(),
            )
            for emb in embeddings
        ]

    def query_embed(self, text: str) -> SparseVector:
        """
        Generate sparse embedding optimized for queries.

        Args:
            text: Query text to embed

        Returns:
            SparseVector with indices and values
        """
        embedding = list(self.model.query_embed(text))[0]
        return SparseVector(
            indices=embedding.indices.tolist(),
            values=embedding.values.tolist(),
        )
