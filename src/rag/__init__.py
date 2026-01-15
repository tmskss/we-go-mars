"""
RAG (Retrieval-Augmented Generation) module.

Handles literature storage, embedding generation, and context retrieval.
"""

from src.rag.literature_store import LiteratureStore, RetrievalResult
from src.rag.embeddings import EmbeddingService, SparseEmbeddingService

__all__ = [
    "LiteratureStore",
    "RetrievalResult",
    "EmbeddingService",
    "SparseEmbeddingService",
]
