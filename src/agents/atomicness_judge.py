"""
Atomicness Judge Agent.

This agent evaluates whether a requirement is atomic (cannot be broken down further).
Multiple instances are used for majority voting.

Owner: [ASSIGN TEAMMATE]
"""

from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.models.requirement import Requirement

SYSTEM_PROMPT = """You are an Atomicness Judge Agent.

Your sole responsibility is to determine if a requirement is ATOMIC.

A requirement is ATOMIC if:
1. It cannot be meaningfully broken down into smaller sub-requirements
2. It has a single, clear deliverable or outcome
3. It can be solved independently without solving other requirements first
4. A single approach or method can address it completely

A requirement is NOT ATOMIC if:
1. It contains multiple distinct goals or outcomes
2. It uses words like "and", "also", or lists multiple items
3. It requires multiple different methods or approaches
4. It could be clearly split into independent parts

Output Format (JSON):
{
    "is_atomic": true/false,
    "reasoning": "explanation of your judgment",
    "suggestion": "if not atomic, how it could be split"
}
"""


class AtomicnessJudgment(BaseModel):
    """Result of atomicness judgment."""

    is_atomic: bool
    reasoning: str
    suggestion: str | None = None


class AtomicnessJudgeAgent(BaseAgent):
    """
    Judges whether a requirement is atomic.

    Input: Single Requirement
    Output: AtomicnessJudgment with verdict and reasoning
    """

    def __init__(self, instance_id: int = 1):
        super().__init__(
            name=f"atomicness_judge_{instance_id}",
            system_prompt=SYSTEM_PROMPT,
        )
        self.instance_id = instance_id

    async def execute(self, requirement: Requirement) -> AtomicnessJudgment:
        """
        Judge if the requirement is atomic.

        Args:
            requirement: The requirement to evaluate

        Returns:
            AtomicnessJudgment with verdict
        """
        # TODO: Implement judgment logic
        # 1. Format the requirement for the LLM
        # 2. Get LLM response
        # 3. Parse into AtomicnessJudgment

        # Placeholder implementation
        return AtomicnessJudgment(
            is_atomic=False,
            reasoning="TODO: Implement LLM-based judgment",
        )
