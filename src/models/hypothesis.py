"""
Hypothesis data model.

Owner: [ASSIGN TEAMMATE]
"""

from pydantic import BaseModel, Field


class Hypothesis(BaseModel):
    """
    Represents a research hypothesis provided by the user.

    Attributes:
        original_text: The raw hypothesis text from the user
        refined_text: The hypothesis after refinement by the deep researcher
        clarifying_questions: Questions generated to clarify the hypothesis
        user_answers: Answers provided by the user to clarifying questions
        context: Additional context gathered from deep research
    """

    original_text: str = Field(..., description="Original hypothesis from user")
    refined_text: str | None = Field(None, description="Refined hypothesis after research")
    clarifying_questions: list[str] = Field(default_factory=list)
    user_answers: dict[str, str] = Field(default_factory=dict)
    context: str = Field("", description="Context gathered from deep research")
    report_path: str | None = Field(None, description="Path to the generated report")
