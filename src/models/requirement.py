"""
Requirement graph data models.

This module contains models for representing the hierarchical breakdown
of a hypothesis into atomic, solvable requirements using a graph structure
that allows shared nodes (deduplication).

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
    A single requirement node in the requirement graph.

    Graph structure allows:
    - Multiple parents (via deduplication)
    - Shared atomic nodes across branches
    - Level-based organization for bottom-up solving

    Attributes:
        id: Unique identifier
        parent_ids: IDs of parent requirements (empty for root)
        content: Description of what needs to be achieved
        level: Depth in the graph (0 = root)
        status: Current status in the workflow
        is_shared: Whether this node is shared (has multiple parents)
        solution_id: Reference to solution (if solved)
    """

    id: UUID = Field(default_factory=uuid4)
    parent_ids: list[UUID] = Field(default_factory=list)
    content: str
    level: int = 0
    status: RequirementStatus = RequirementStatus.PENDING
    is_shared: bool = False
    solution_id: UUID | None = None


class RequirementGraph(BaseModel):
    """
    The complete requirement graph for a hypothesis.

    Maintains all nodes in a flat registry with level-based organization.
    Atomic nodes can be shared across multiple parents through deduplication.

    Attributes:
        root_id: ID of the root requirement (level 0)
        nodes: Flat registry of all nodes by ID
        children_map: Parent -> Children mapping for explicit relationships
        levels: Level-based indexing for bottom-up traversal
        total_nodes: Total number of requirements
        atomic_count: Number of atomic (leaf) requirements
        shared_count: Number of deduplicated (shared) nodes
        max_depth: Maximum depth of the graph
    """

    root_id: UUID
    nodes: dict[UUID, Requirement] = Field(default_factory=dict)
    children_map: dict[UUID, list[UUID]] = Field(default_factory=dict)
    levels: dict[int, list[UUID]] = Field(default_factory=dict)

    total_nodes: int = 0
    atomic_count: int = 0
    shared_count: int = 0
    max_depth: int = 0

    def add_node(self, node: Requirement) -> None:
        """
        Add a node to the graph.

        Args:
            node: Requirement node to add
        """
        self.nodes[node.id] = node

        if node.level not in self.levels:
            self.levels[node.level] = []
        self.levels[node.level].append(node.id)

        if node.id not in self.children_map:
            self.children_map[node.id] = []

        self.total_nodes += 1
        self.max_depth = max(self.max_depth, node.level)

    def add_child(self, parent_id: UUID, child: Requirement) -> None:
        """
        Add a new child to a parent node.

        Creates the child node and establishes the parent-child relationship.

        Args:
            parent_id: ID of the parent requirement
            child: New child requirement to add
        """
        if parent_id not in child.parent_ids:
            child.parent_ids.append(parent_id)

        self.add_node(child)

        if parent_id not in self.children_map:
            self.children_map[parent_id] = []
        self.children_map[parent_id].append(child.id)

    def link_existing_child(self, parent_id: UUID, existing_child_id: UUID) -> None:
        """
        Link a parent to an existing node (deduplication).

        Used when a semantically equivalent requirement already exists.
        The existing node becomes shared across multiple parents.

        Args:
            parent_id: ID of the parent requirement
            existing_child_id: ID of the existing child to link
        """
        existing = self.nodes.get(existing_child_id)
        if not existing:
            return

        if parent_id not in existing.parent_ids:
            existing.parent_ids.append(parent_id)
            existing.is_shared = True
            self.shared_count += 1

        if parent_id not in self.children_map:
            self.children_map[parent_id] = []
        if existing_child_id not in self.children_map[parent_id]:
            self.children_map[parent_id].append(existing_child_id)

    def get_node(self, node_id: UUID) -> Requirement | None:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_root(self) -> Requirement:
        """Get the root requirement."""
        return self.nodes[self.root_id]

    def get_children(self, node_id: UUID) -> list[Requirement]:
        """
        Get all children of a node.

        Args:
            node_id: ID of the parent node

        Returns:
            List of child requirements
        """
        child_ids = self.children_map.get(node_id, [])
        return [self.nodes[cid] for cid in child_ids if cid in self.nodes]

    def get_parents(self, node_id: UUID) -> list[Requirement]:
        """
        Get all parents of a node.

        Args:
            node_id: ID of the child node

        Returns:
            List of parent requirements
        """
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.nodes[pid] for pid in node.parent_ids if pid in self.nodes]

    def get_atomic_requirements(self) -> list[Requirement]:
        """
        Return all atomic (leaf) requirements.

        Atomic requirements have no children and are the base units for solving.

        Returns:
            List of atomic requirements
        """
        atomic = []
        for node in self.nodes.values():
            children = self.children_map.get(node.id, [])
            if not children:
                atomic.append(node)
        self.atomic_count = len(atomic)
        return atomic

    def get_unsolved_atomic(self) -> list[Requirement]:
        """Return atomic requirements that haven't been solved yet."""
        return [
            req for req in self.get_atomic_requirements()
            if req.status != RequirementStatus.SOLVED
        ]

    def get_level_nodes(self, level: int) -> list[Requirement]:
        """
        Get all nodes at a specific level.

        Args:
            level: The level to retrieve (0 = root)

        Returns:
            List of requirements at that level
        """
        node_ids = self.levels.get(level, [])
        return [self.nodes[nid] for nid in node_ids if nid in self.nodes]


# Keep RequirementTree as alias for backwards compatibility
RequirementTree = RequirementGraph
