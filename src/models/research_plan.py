"""
Research plan data model - the final output of the system.

Owner: [ASSIGN TEAMMATE]
"""

from pydantic import BaseModel, Field

from src.models.hypothesis import Hypothesis
from src.models.requirement import RequirementTree
from src.models.solution import Solution


class MethodologyStep(BaseModel):
    """A single step in the research methodology."""

    step_number: int
    name: str
    description: str
    expected_output: str
    dependencies: list[int] = Field(default_factory=list)


class ResearchPlan(BaseModel):
    """
    The final research plan output.

    This is the main deliverable of the system - a structured plan
    that tells the researcher exactly how to proceed with their hypothesis.

    Attributes:
        hypothesis: The original and refined hypothesis
        goals: Clear, actionable research goals
        methodology: Step-by-step research methodology
        requirements_tree: The full breakdown of requirements
        solutions: All approved solutions
        expected_outcomes: What the research should achieve
        next_steps: Immediate next actions for the researcher
    """

    hypothesis: Hypothesis
    goals: list[str] = Field(default_factory=list)
    methodology: list[MethodologyStep] = Field(default_factory=list)
    requirements_tree: RequirementTree | None = None
    solutions: list[Solution] = Field(default_factory=list)
    expected_outcomes: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        """
        Render the research plan as a formatted markdown document.

        Returns:
            Formatted markdown string
        """
        # TODO: Implement markdown rendering
        # Should produce output like:
        #
        # # Research Plan: [Hypothesis Summary]
        #
        # ## Goals
        # 1. [Goal 1]
        # ...
        #
        # ## Methodology
        # ### Step 1: [Name]
        # ...
        #
        # ## Solutions
        # ...
        #
        # ## Expected Outcomes
        # ...
        #
        # ## Next Steps
        # ...

        raise NotImplementedError("Implement markdown rendering")
