"""
RAG (Retrieval-Augmented Generation) module.

Handles literature storage, embedding generation, and context retrieval.
"""

from src.rag.literature_store import LiteratureStore, RetrievalResult
from src.rag.embeddings import EmbeddingService, SparseEmbeddingService
from src.rag.requirement_store import RequirementStore, RequirementCandidate

__all__ = [
    "LiteratureStore",
    "RetrievalResult",
    "EmbeddingService",
    "SparseEmbeddingService",
    "RequirementStore",
    "RequirementCandidate",
]
