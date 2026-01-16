"""
Requirement store for semantic deduplication using Qdrant.

Stores decomposed requirements with embeddings for similarity search
during the decomposition phase. Supports level-based filtering to
enforce the crossover constraint (only match at level l for level l+1).

Owner: [ASSIGN TEAMMATE]
"""

from dataclasses import dataclass
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)

from src.config import settings
from src.rag.embeddings import EmbeddingService
from src.models.requirement import Requirement


@dataclass
class RequirementCandidate:
    """A candidate requirement for deduplication."""

    requirement_id: UUID
    content: str
    level: int
    score: float


class RequirementStore:
    """
    Vector store for requirement deduplication.

    Features:
    - Dense embeddings for semantic similarity
    - Level-based filtering (critical: only match same level)
    - Top-k candidate retrieval for LLM decision
    """

    COLLECTION_NAME = "requirements"
    DENSE_VECTOR_NAME = "dense"

    def __init__(self):
        """Initialize the requirement store."""
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
        self.embeddings = EmbeddingService()
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create the collection if it doesn't exist."""
        collections = self.client.get_collections()
        collection_exists = self.COLLECTION_NAME in [c.name for c in collections.collections]

        if not collection_exists:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config={
                    self.DENSE_VECTOR_NAME: VectorParams(
                        size=self.embeddings.dimension,
                        distance=Distance.COSINE,
                    )
                },
            )

            # Create payload index for level field (required for filtering)
            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="level",
                field_schema=PayloadSchemaType.INTEGER,
            )

    def clear(self) -> None:
        """Clear all requirements (for new decomposition session)."""
        try:
            self.client.delete_collection(self.COLLECTION_NAME)
        except Exception:
            pass
        self._ensure_collection()

    def add_requirement(self, requirement: Requirement) -> None:
        """
        Add a requirement to the store.

        Args:
            requirement: Requirement to index
        """
        embedding = self.embeddings.embed(requirement.content)

        point = PointStruct(
            id=str(requirement.id),
            vector={self.DENSE_VECTOR_NAME: embedding},
            payload={
                "requirement_id": str(requirement.id),
                "content": requirement.content,
                "level": requirement.level,
            },
        )

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point],
        )

    def add_requirements_batch(self, requirements: list[Requirement]) -> None:
        """
        Add multiple requirements in batch.

        Args:
            requirements: List of requirements to index
        """
        if not requirements:
            return

        contents = [r.content for r in requirements]
        embeddings = self.embeddings.embed_batch(contents)

        points = [
            PointStruct(
                id=str(req.id),
                vector={self.DENSE_VECTOR_NAME: embeddings[i]},
                payload={
                    "requirement_id": str(req.id),
                    "content": req.content,
                    "level": req.level,
                },
            )
            for i, req in enumerate(requirements)
        ]

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

    def find_similar(
        self,
        content: str,
        level: int,
        top_k: int = 5,
        score_threshold: float = 0.75,
    ) -> list[RequirementCandidate]:
        """
        Find similar requirements at a specific level.

        CRITICAL: Only searches within the specified level for deduplication.
        This enforces the crossover constraint - when decomposing level l,
        can only match existing nodes at level l+1.

        Args:
            content: New requirement content to match
            level: Level to search (MUST match target level for new requirement)
            top_k: Number of candidates to return
            score_threshold: Minimum similarity score

        Returns:
            List of candidate requirements for LLM decision
        """
        query_embedding = self.embeddings.embed(content)

        # Filter by level - critical constraint for crossover
        level_filter = Filter(
            must=[
                FieldCondition(
                    key="level",
                    match=MatchValue(value=level),
                )
            ]
        )

        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_embedding,
            using=self.DENSE_VECTOR_NAME,  # Specify which named vector to use
            query_filter=level_filter,
            limit=top_k,
            with_payload=True,
            score_threshold=score_threshold,
        )

        candidates = []
        for point in results:
            candidates.append(
                RequirementCandidate(
                    requirement_id=UUID(point.payload["requirement_id"]),
                    content=point.payload["content"],
                    level=point.payload["level"],
                    score=point.score,
                )
            )

        return candidates
