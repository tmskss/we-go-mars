"""
Research plan data model - the final output of the system.

Owner: [ASSIGN TEAMMATE]
"""

from enum import Enum
from uuid import UUID, uuid4

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
        raise NotImplementedError("Implement markdown rendering")


# ============================================================================
# Iterative Plan Synthesis Models
# ============================================================================


class VerificationCategory(str, Enum):
    """Category indicating what verification a step requires."""

    INFORMATION_COMPLETE = "information_complete"
    REQUIRES_EXPERIMENT = "requires_experiment"
    REQUIRES_FIELD_TEST = "requires_field_test"
    REQUIRES_PROTOTYPE = "requires_prototype"
    REQUIRES_SIMULATION = "requires_simulation"
    REQUIRES_MEASUREMENT = "requires_measurement"
    REQUIRES_EXPERT_REVIEW = "requires_expert_review"


class InformationGap(BaseModel):
    """Represents a gap in information identified during preliminary planning."""

    id: UUID = Field(default_factory=uuid4)
    description: str
    query_for_kb: str
    related_step_ids: list[int] = Field(default_factory=list)
    filled: bool = False
    filled_content: str = ""
    sources: list[str] = Field(default_factory=list)


class PreliminaryPlanStep(BaseModel):
    """A step in the preliminary plan with gap markers."""

    step_number: int
    name: str
    description: str
    what_we_have: str
    what_we_lack: list[str] = Field(default_factory=list)
    gap_ids: list[UUID] = Field(default_factory=list)
    preliminary_approach: str
    dependencies: list[int] = Field(default_factory=list)
    confidence: float = Field(0.5, ge=0.0, le=1.0)


class PreliminaryPlan(BaseModel):
    """Output of the first iteration - plan with gaps identified."""

    problem_summary: str
    available_knowledge_summary: str
    steps: list[PreliminaryPlanStep] = Field(default_factory=list)
    gaps: list[InformationGap] = Field(default_factory=list)
    overall_confidence: float = Field(0.5, ge=0.0, le=1.0)


class FinalPlanStep(BaseModel):
    """A step in the final plan with verification markers."""

    step_number: int
    name: str
    description: str
    detailed_approach: str
    expected_output: str
    dependencies: list[int] = Field(default_factory=list)
    verification_category: VerificationCategory
    verification_details: str = ""
    estimated_effort: str = ""
    knowledge_sources: list[str] = Field(default_factory=list)
    confidence: float = Field(0.7, ge=0.0, le=1.0)


class FinalPlan(BaseModel):
    """Output of the second iteration - refined plan with verification markers."""

    problem_statement: str
    hypothesis_refined: str = ""
    executive_summary: str
    steps: list[FinalPlanStep] = Field(default_factory=list)
    total_steps: int = 0
    steps_information_complete: int = 0
    steps_requiring_verification: int = 0
    remaining_gaps: list[str] = Field(default_factory=list)
    overall_feasibility: str = ""
    key_risks: list[str] = Field(default_factory=list)
    recommended_next_actions: list[str] = Field(default_factory=list)
