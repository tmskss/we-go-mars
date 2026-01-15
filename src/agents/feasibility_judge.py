"""
Feasibility Judge Agent.

This agent evaluates whether a requirement is feasible to solve
given the available context and resources.

Owner: [ASSIGN TEAMMATE]
"""

from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.models.requirement import Requirement

SYSTEM_PROMPT = """You are a Feasibility Judge Agent.

Your sole responsibility is to determine if a requirement is FEASIBLE to solve.

A requirement is FEASIBLE if:
1. There is sufficient context/information available to address it
2. It is within the scope of the research domain
3. It does not require resources or data that are unavailable
4. It can be solved with existing knowledge or reasonable research

A requirement is NOT FEASIBLE if:
1. It requires information that cannot be obtained
2. It is too vague or abstract to have a concrete solution
3. It depends on external factors beyond control
4. It contradicts known scientific principles

Output Format (JSON):
{
    "is_feasible": true/false,
    "reasoning": "explanation of your judgment",
    "missing_info": ["list of missing information if not feasible"]
}
"""


class FeasibilityJudgment(BaseModel):
    """Result of feasibility judgment."""

    is_feasible: bool
    reasoning: str
    missing_info: list[str] = []


class FeasibilityJudgeInput(BaseModel):
    """Input for feasibility judge agent."""

    requirement: Requirement
    context: str = ""


class FeasibilityJudgeAgent(BaseAgent[FeasibilityJudgeInput, FeasibilityJudgment]):
    """
    Judges whether a requirement is feasible to solve.

    Input: Requirement + context
    Output: FeasibilityJudgment with verdict and reasoning
    """

    def __init__(self, instance_id: int = 1):
        super().__init__(
            name=f"feasibility_judge_{instance_id}",
            instructions=SYSTEM_PROMPT,
        )
        self.instance_id = instance_id

    async def execute(self, input_data: FeasibilityJudgeInput) -> FeasibilityJudgment:
        """
        Judge if the requirement is feasible.

        Args:
            input_data: FeasibilityJudgeInput containing requirement and context

        Returns:
            FeasibilityJudgment with verdict
        """
        # TODO: Implement judgment logic
        # 1. Format requirement and context for LLM
        # 2. Get LLM response
        # 3. Parse into FeasibilityJudgment

        # Placeholder implementation
        return FeasibilityJudgment(
            is_feasible=True,
            reasoning="TODO: Implement LLM-based judgment",
        )
