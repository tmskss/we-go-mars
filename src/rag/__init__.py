"""
RAG (Retrieval-Augmented Generation) module.

Handles literature storage, embedding generation, and context retrieval.
"""

from src.rag.literature_store import LiteratureStore
from src.rag.embeddings import EmbeddingService, SparseEmbeddingService
from src.rag.retrieval import RetrievalService

__all__ = [
    "LiteratureStore",
    "EmbeddingService",
    "SparseEmbeddingService",
    "RetrievalService",
]
