"""
Solution Judge Agent.

This agent evaluates the quality of proposed solutions.
Multiple instances are used for majority voting.

Owner: [ASSIGN TEAMMATE]
"""

from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.models.requirement import Requirement
from src.models.solution import Solution

SYSTEM_PROMPT = """You are a Solution Quality Judge Agent.

Your responsibility is to evaluate whether a proposed solution adequately
addresses the requirement.

Evaluation Criteria:
1. Correctness: Is the solution factually correct?
2. Completeness: Does it fully address the requirement?
3. Clarity: Is the solution clearly explained?
4. Actionability: Can the solution be implemented/used?
5. Evidence: Is the solution supported by reasoning?

Scoring:
- Score each criterion 0-1
- Overall score is the weighted average
- A solution is acceptable if overall score >= 0.7

Output Format (JSON):
{
    "scores": {
        "correctness": 0.0-1.0,
        "completeness": 0.0-1.0,
        "clarity": 0.0-1.0,
        "actionability": 0.0-1.0,
        "evidence": 0.0-1.0
    },
    "overall_score": 0.0-1.0,
    "is_acceptable": true/false,
    "feedback": "specific feedback for improvement",
    "strengths": ["list of strengths"],
    "weaknesses": ["list of weaknesses"]
}
"""


class SolutionScores(BaseModel):
    """Individual scores for solution quality."""

    correctness: float
    completeness: float
    clarity: float
    actionability: float
    evidence: float


class SolutionJudgment(BaseModel):
    """Result of solution quality judgment."""

    scores: SolutionScores
    overall_score: float
    is_acceptable: bool
    feedback: str
    strengths: list[str] = []
    weaknesses: list[str] = []


class SolutionJudgeInput(BaseModel):
    """Input for solution judge agent."""

    solution: Solution
    requirement: Requirement


class SolutionJudgeAgent(BaseAgent[SolutionJudgeInput, SolutionJudgment]):
    """
    Judges the quality of proposed solutions.

    Input: Solution + Requirement
    Output: SolutionJudgment with scores and feedback
    """

    def __init__(self, instance_id: int = 1):
        super().__init__(
            name=f"solution_judge_{instance_id}",
            instructions=SYSTEM_PROMPT,
        )
        self.instance_id = instance_id

    async def execute(self, input_data: SolutionJudgeInput) -> SolutionJudgment:
        """
        Judge the quality of a solution.

        Args:
            input_data: SolutionJudgeInput containing solution and requirement

        Returns:
            SolutionJudgment with scores and feedback
        """
        # TODO: Implement judgment logic
        # 1. Format solution and requirement for LLM
        # 2. Get LLM evaluation
        # 3. Parse scores and feedback

        # Placeholder implementation
        return SolutionJudgment(
            scores=SolutionScores(
                correctness=0.5,
                completeness=0.5,
                clarity=0.5,
                actionability=0.5,
                evidence=0.5,
            ),
            overall_score=0.5,
            is_acceptable=False,
            feedback="TODO: Implement LLM-based judgment",
        )
