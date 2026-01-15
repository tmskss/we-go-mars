"""
Requirement tree data models.

This is a critical model that represents the hierarchical breakdown
of a hypothesis into atomic, solvable requirements.

Owner: [ASSIGN TEAMMATE]
"""

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RequirementStatus(str, Enum):
    """Status of a requirement in the workflow."""

    PENDING = "pending"  # Not yet processed
    DECOMPOSING = "decomposing"  # Being broken down
    SOLVING = "solving"  # Being solved
    SOLVED = "solved"  # Solution approved
    FAILED = "failed"  # Could not be solved


class Requirement(BaseModel):
    """
    A single requirement in the requirement tree.

    Requirements form a tree structure where:
    - Root: Top-level requirements derived from the hypothesis
    - Composite: Requirements that can be broken down further
    - Atomic: Leaf requirements that are independently solvable

    Attributes:
        id: Unique identifier
        parent_id: ID of parent requirement (None for root)
        content: Description of what needs to be achieved
        level: Depth in the tree (0 = root)
        status: Current status in the workflow
        children: Child requirements (if decomposed)
        solution_id: Reference to solution (if solved)
    """

    id: UUID = Field(default_factory=uuid4)
    parent_id: UUID | None = None
    content: str
    level: int = 0
    status: RequirementStatus = RequirementStatus.PENDING

    # Tree structure
    children: list["Requirement"] = Field(default_factory=list)

    # Solution reference
    solution_id: UUID | None = None


class RequirementTree(BaseModel):
    """
    The complete requirement tree for a hypothesis.

    Attributes:
        root: The root requirement
        total_nodes: Total number of requirements
        atomic_count: Number of atomic requirements
        solved_count: Number of solved requirements
        max_depth: Maximum depth of the tree
    """

    root: Requirement
    total_nodes: int = 0
    atomic_count: int = 0
    solved_count: int = 0
    max_depth: int = 0

    def get_atomic_requirements(self) -> list[Requirement]:
        """Return all atomic requirements in the tree."""
        # TODO: Implement tree traversal to find atomic requirements
        raise NotImplementedError

    def get_unsolved_atomic(self) -> list[Requirement]:
        """Return atomic requirements that haven't been solved yet."""
        # TODO: Implement filtering
        raise NotImplementedError
