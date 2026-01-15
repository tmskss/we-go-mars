"""
Plan Synthesizer Agent.

This agent generates the final research plan from aggregated solutions
and the original hypothesis.

Owner: [ASSIGN TEAMMATE]
"""

from src.agents.base import BaseAgent
from src.agents.aggregator import AggregatorOutput
from src.models.hypothesis import Hypothesis
from src.models.research_plan import ResearchPlan

SYSTEM_PROMPT = """You are a Research Plan Synthesizer Agent.

Your responsibility is to create a comprehensive, actionable research plan.

The plan must include:
1. Clear, measurable goals derived from the hypothesis
2. Step-by-step methodology with expected outputs
3. Mapping of solutions to methodology steps
4. Expected outcomes and success criteria
5. Concrete next steps for the researcher

Guidelines:
- Be specific and actionable
- Include timelines where possible
- Highlight dependencies between steps
- Anticipate potential challenges

Output Format (JSON):
{
    "goals": ["list of clear goals"],
    "methodology": [
        {
            "step_number": 1,
            "name": "step name",
            "description": "what to do",
            "expected_output": "what you'll get",
            "dependencies": [step numbers]
        }
    ],
    "expected_outcomes": ["list of outcomes"],
    "next_steps": ["immediate actions"],
    "risks": ["potential challenges"]
}
"""


class PlanSynthesizerAgent(BaseAgent):
    """
    Synthesizes the final research plan.

    Input: Hypothesis + Aggregated solutions
    Output: Complete ResearchPlan
    """

    def __init__(self):
        super().__init__(
            name="plan_synthesizer",
            system_prompt=SYSTEM_PROMPT,
        )

    async def execute(
        self,
        hypothesis: Hypothesis,
        aggregated: AggregatorOutput,
    ) -> ResearchPlan:
        """
        Generate the final research plan.

        Args:
            hypothesis: The original/refined hypothesis
            aggregated: The aggregated solutions

        Returns:
            Complete ResearchPlan
        """
        # TODO: Implement plan synthesis
        # 1. Extract goals from hypothesis
        # 2. Create methodology from solutions
        # 3. Define outcomes and next steps
        # 4. Build complete research plan

        # Placeholder implementation
        return ResearchPlan(
            hypothesis=hypothesis,
            goals=["TODO: Generate goals from hypothesis"],
            methodology=[],
            expected_outcomes=["TODO: Define expected outcomes"],
            next_steps=["TODO: Define next steps"],
        )
