"""
Solution Aggregator Agent.

This agent combines all approved solutions (both existing and novel)
into a unified solution set with relationships.

Owner: [ASSIGN TEAMMATE]
"""

from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.models.solution import Solution

SYSTEM_PROMPT = """You are a Solution Aggregator Agent.

Your responsibility is to combine all approved solutions into a coherent whole.

Tasks:
1. Identify relationships between solutions
2. Resolve any conflicts or contradictions
3. Create a unified narrative
4. Highlight dependencies between solutions

Output Format (JSON):
{
    "unified_solutions": [
        {
            "id": "solution_id",
            "summary": "brief summary",
            "dependencies": ["ids of dependent solutions"],
            "category": "methodology/analysis/etc"
        }
    ],
    "relationships": [
        {
            "from": "solution_id",
            "to": "solution_id",
            "type": "depends_on/supports/contradicts"
        }
    ],
    "synthesis": "overall synthesis of all solutions",
    "gaps": ["any identified gaps"]
}
"""


class SolutionRelationship(BaseModel):
    """Relationship between two solutions."""

    from_id: str
    to_id: str
    relationship_type: str  # "depends_on", "supports", "contradicts"


class AggregatedSolution(BaseModel):
    """A solution in the aggregated set."""

    id: str
    summary: str
    dependencies: list[str]
    category: str


class AggregatorOutput(BaseModel):
    """Output from the aggregator agent."""

    unified_solutions: list[AggregatedSolution]
    relationships: list[SolutionRelationship]
    synthesis: str
    gaps: list[str]


class AggregatorAgent(BaseAgent[list[Solution], AggregatorOutput]):
    """
    Aggregates all solutions into a unified set.

    Input: List of approved solutions
    Output: AggregatorOutput with relationships and synthesis
    """

    def __init__(self):
        super().__init__(
            name="aggregator",
            instructions=SYSTEM_PROMPT,
        )

    async def execute(self, input_data: list[Solution]) -> AggregatorOutput:
        """
        Aggregate all solutions into a unified set.

        Args:
            input_data: List of all approved solutions

        Returns:
            AggregatorOutput with unified solutions and relationships
        """
        # TODO: Implement aggregation logic
        # 1. Analyze all solutions
        # 2. Identify relationships
        # 3. Create synthesis
        # 4. Identify gaps

        # Placeholder implementation
        return AggregatorOutput(
            unified_solutions=[],
            relationships=[],
            synthesis="TODO: Implement solution aggregation",
            gaps=[],
        )
