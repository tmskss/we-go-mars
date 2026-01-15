"""
Requirement Decomposer Agent.

This agent breaks down high-level requirements into a tree structure,
recursively decomposing until reaching atomic requirements.

Owner: [ASSIGN TEAMMATE]
"""

from src.agents.base import BaseAgent
from src.models.hypothesis import Hypothesis
from src.models.requirement import Requirement, RequirementTree

SYSTEM_PROMPT = """You are a Requirement Decomposition Agent specialized in breaking down complex research goals.

Your responsibilities:
1. Take high-level requirements and break them into sub-requirements
2. Continue decomposition until requirements are atomic (independently solvable)
3. Ensure each requirement is clear, specific, and actionable

Guidelines for decomposition:
- Each atomic requirement should be solvable without depending on sibling solutions
- Maintain clear parent-child relationships
- Aim for 2-4 children per parent requirement
- Stop decomposing when a requirement is specific enough to have a single, clear solution

Output Format (JSON):
{
    "requirement": "description of the requirement",
    "children": [
        {"requirement": "sub-requirement 1", "children": [...]},
        {"requirement": "sub-requirement 2", "children": [...]}
    ]
}
"""


class RequirementDecomposerAgent(BaseAgent):
    """
    Decomposes requirements into a hierarchical tree structure.

    Input: Hypothesis with context
    Output: RequirementTree with all requirements
    """

    def __init__(self):
        super().__init__(
            name="requirement_decomposer",
            system_prompt=SYSTEM_PROMPT,
        )

    async def execute(self, hypothesis: Hypothesis) -> RequirementTree:
        """
        Decompose the hypothesis into a requirement tree.

        Args:
            hypothesis: The refined hypothesis with context

        Returns:
            RequirementTree with hierarchical requirements
        """
        # TODO: Implement decomposition logic
        # 1. Generate root requirements from hypothesis
        # 2. Recursively decompose each requirement
        # 3. Build the tree structure
        # 4. Return for judge evaluation

        root = Requirement(
            content=f"Solve: {hypothesis.refined_text or hypothesis.original_text}",
            level=0,
        )

        # TODO: Replace with actual LLM-based decomposition
        return RequirementTree(root=root, total_nodes=1, max_depth=0)

    async def decompose_single(self, requirement: Requirement) -> list[Requirement]:
        """
        Decompose a single requirement into children.

        Args:
            requirement: The requirement to decompose

        Returns:
            List of child requirements
        """
        # TODO: Implement single requirement decomposition
        raise NotImplementedError
