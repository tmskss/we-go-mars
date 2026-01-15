"""
Embedding generation service.

Owner: [ASSIGN TEAMMATE]
"""

from openai import OpenAI

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

    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # TODO: Implement embedding generation
        # response = self.client.embeddings.create(
        #     model=self.model,
        #     input=text,
        # )
        # return response.data[0].embedding

        raise NotImplementedError("Implement embedding generation")

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        # TODO: Implement batch embedding
        # response = self.client.embeddings.create(
        #     model=self.model,
        #     input=texts,
        # )
        # return [item.embedding for item in response.data]

        raise NotImplementedError("Implement batch embedding")
