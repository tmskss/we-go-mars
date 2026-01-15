"""
Proposer Agent with Tree of Thoughts.

This agent generates solution candidates using Tree of Thoughts (ToT)
reasoning for exploring multiple solution paths.

Owner: [ASSIGN TEAMMATE]
"""

from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.models.requirement import Requirement
from src.models.solution import Solution, SolutionSource

SYSTEM_PROMPT = """You are a Solution Proposer Agent using Tree of Thoughts reasoning.

Your responsibility is to generate high-quality solutions for atomic requirements.

Tree of Thoughts Process:
1. Generate N different initial approaches (branches)
2. For each approach, explore D levels deep
3. At each level, evaluate and prune unpromising branches
4. Return the best solution path with full reasoning chain

Guidelines:
- Consider multiple approaches before committing
- Evaluate each step for validity and promise
- Build on the provided context from literature
- Show your reasoning chain explicitly

Output Format (JSON):
{
    "reasoning_tree": {
        "branches": [
            {
                "approach": "description",
                "steps": ["step1", "step2", ...],
                "evaluation": "why this is promising/not"
            }
        ]
    },
    "best_solution": {
        "content": "the solution",
        "reasoning_chain": ["step1", "step2", ...],
        "confidence": 0.0-1.0
    }
}
"""


class ReasoningBranch(BaseModel):
    """A single branch in the Tree of Thoughts."""

    approach: str
    steps: list[str]
    evaluation: str
    score: float = 0.0


class ReasoningTree(BaseModel):
    """The full reasoning tree."""

    branches: list[ReasoningBranch]
    selected_branch_index: int


class ProposerOutput(BaseModel):
    """Output from the proposer agent."""

    reasoning_tree: ReasoningTree
    solution: Solution


class ProposerInput(BaseModel):
    """Input for proposer agent."""

    requirement: Requirement
    context: str = ""
    num_branches: int = 3
    depth: int = 3


class ProposerAgent(BaseAgent[ProposerInput, ProposerOutput]):
    """
    Generates solutions using Tree of Thoughts reasoning.

    Input: Atomic requirement + context
    Output: ProposerOutput with solution and reasoning tree
    """

    def __init__(self, instance_id: int = 1):
        super().__init__(
            name=f"proposer_{instance_id}",
            instructions=SYSTEM_PROMPT,
        )
        self.instance_id = instance_id

    async def execute(self, input_data: ProposerInput) -> ProposerOutput:
        """
        Generate a solution using Tree of Thoughts.

        Args:
            input_data: ProposerInput containing requirement, context, and ToT parameters

        Returns:
            ProposerOutput with solution and reasoning tree
        """
        # TODO: Implement Tree of Thoughts logic
        # 1. Generate N initial approaches
        # 2. For each approach, expand D levels
        # 3. Evaluate and score each branch
        # 4. Select best branch
        # 5. Return solution with reasoning chain

        # Placeholder implementation
        placeholder_solution = Solution(
            requirement_id=input_data.requirement.id,
            content="TODO: Implement ToT solution generation",
            reasoning_chain=["Step 1: Analyze", "Step 2: Generate", "Step 3: Refine"],
            source=SolutionSource.NOVEL,
            confidence=0.5,
        )

        return ProposerOutput(
            reasoning_tree=ReasoningTree(branches=[], selected_branch_index=0),
            solution=placeholder_solution,
        )
