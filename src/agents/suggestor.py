"""
Suggestor Agent.

This agent suggests how to refine requirements that failed
atomicness or feasibility checks.

Owner: [ASSIGN TEAMMATE]
"""

from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.models.requirement import Requirement

SYSTEM_PROMPT = """You are a Requirement Refinement Suggestor Agent.

When a requirement fails atomicness or feasibility checks, you suggest how to refine it.

Your responsibilities:
1. Analyze the judge feedback
2. Suggest specific ways to decompose or modify the requirement
3. Ensure suggestions lead to atomic, feasible requirements

Guidelines:
- If not atomic: suggest how to split into smaller parts
- If not feasible: suggest how to make it more concrete or achievable
- Provide 2-3 specific suggestions
- Each suggestion should be actionable

Output Format (JSON):
{
    "analysis": "analysis of why the requirement failed",
    "suggestions": [
        {
            "type": "split" | "modify" | "clarify",
            "description": "what to do",
            "result": "expected outcome"
        }
    ],
    "recommended_action": "the best suggested action"
}
"""


class RefinementSuggestion(BaseModel):
    """A single refinement suggestion."""

    type: str  # "split", "modify", "clarify"
    description: str
    result: str


class SuggestorOutput(BaseModel):
    """Output from the suggestor agent."""

    analysis: str
    suggestions: list[RefinementSuggestion]
    recommended_action: str


class SuggestorAgent(BaseAgent):
    """
    Suggests refinements for failed requirements.

    Input: Requirement + judge feedback
    Output: SuggestorOutput with refinement suggestions
    """

    def __init__(self, instance_id: int = 1):
        super().__init__(
            name=f"suggestor_{instance_id}",
            system_prompt=SYSTEM_PROMPT,
        )
        self.instance_id = instance_id

    async def execute(
        self,
        requirement: Requirement,
        atomicness_feedback: str | None = None,
        feasibility_feedback: str | None = None,
    ) -> SuggestorOutput:
        """
        Suggest refinements for a failed requirement.

        Args:
            requirement: The requirement that failed checks
            atomicness_feedback: Feedback from atomicness judge
            feasibility_feedback: Feedback from feasibility judge

        Returns:
            SuggestorOutput with refinement suggestions
        """
        # TODO: Implement suggestion logic
        # 1. Combine judge feedback
        # 2. Generate refinement suggestions
        # 3. Pick best recommendation

        # Placeholder implementation
        return SuggestorOutput(
            analysis="TODO: Implement analysis",
            suggestions=[],
            recommended_action="TODO: Implement",
        )
