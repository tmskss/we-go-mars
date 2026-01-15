"""
Deep Researcher Agent.

This agent performs initial deep research on the user's hypothesis,
gathering context from the RAG system and generating clarifying questions.

Owner: [ASSIGN TEAMMATE]
"""

from src.agents.base import BaseAgent
from src.models.hypothesis import Hypothesis

SYSTEM_PROMPT = """You are a Deep Research Agent specialized in scientific literature analysis.

Your responsibilities:
1. Analyze the user's research hypothesis
2. Search the literature knowledge base for relevant context
3. Identify gaps and ambiguities in the hypothesis
4. Generate clarifying questions to refine the hypothesis

When analyzing a hypothesis:
- Look for similar research that has been done
- Identify the key variables and relationships
- Note any assumptions that need verification
- Consider feasibility and scope

Output Format:
- Provide a summary of relevant literature findings
- List specific clarifying questions (max 5)
- Suggest initial high-level requirements
"""


class DeepResearcherAgent(BaseAgent):
    """
    Performs deep research on the hypothesis and generates clarifying questions.

    Input: User hypothesis (str)
    Output: Hypothesis object with context and clarifying questions
    """

    def __init__(self):
        super().__init__(
            name="deep_researcher",
            system_prompt=SYSTEM_PROMPT,
        )

    async def execute(self, hypothesis_text: str) -> Hypothesis:
        """
        Research the hypothesis and generate clarifying questions.

        Args:
            hypothesis_text: The user's raw hypothesis

        Returns:
            Hypothesis object with context and questions populated
        """
        # TODO: Implement deep research logic
        # 1. Query the RAG system for relevant literature
        # 2. Analyze the hypothesis for gaps
        # 3. Generate clarifying questions
        # 4. Create initial context summary

        hypothesis = Hypothesis(original_text=hypothesis_text)

        # TODO: Replace with actual implementation
        hypothesis.clarifying_questions = [
            "What specific outcome are you trying to achieve?",
            "What constraints or limitations should be considered?",
            "What resources do you have available?",
        ]
        hypothesis.context = "TODO: Implement RAG retrieval"

        return hypothesis
