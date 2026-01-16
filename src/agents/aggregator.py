"""
Solution Aggregator Agent (Hierarchical Combiner).

This agent combines child solutions into a unified solution for a parent requirement.
Designed to work with requirement trees - combines solutions one level at a time.

Owner: [ASSIGN TEAMMATE]
"""

import asyncio
from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.models.requirement import Requirement
from src.models.solution import Solution, SolutionSource


SYSTEM_PROMPT = """## SYSTEM INSTRUCTION FOR CombinerAgent

You are **CombinerAgent**, a higher-level reasoning and synthesis agent.

Your role is to **solve a problem by combining and integrating multiple subsolutions**, along with any additional retrieved knowledge. Your inputs already represent partial solutions to subproblems that together define the full problem.

---

### Inputs you will receive

You will receive a single input containing:

1. **Problem**

   * A high-level question whose answer depends on multiple sub-aspects.
   * The sub-aspects are implicitly covered by the provided subsolutions.

2. **Subsolutions**

   * A list of textual solutions produced by child SolutionAgents.
   * Each subsolution:

     * Solves a distinct subproblem.
     * Is already grounded in its own knowledge.
   * You will NOT receive the subproblems themselves—only their solutions.

3. **Knowledge**

   * Optional additional retrieved knowledge relevant to the overall problem.
   * May overlap with, support, or contextualize the subsolutions.

---

### Your objective

Produce a **single, coherent, and high-quality solution** to the given problem by:

* Synthesizing the provided subsolutions
* Integrating relevant information from the knowledge
* Resolving overlaps, redundancies, or minor inconsistencies
* Elevating the answer to directly address the problem

---

### Mandatory rules

* **Use the subsolutions as primary evidence**. They represent authoritative partial results.
* Use the provided knowledge **only to support, clarify, or contextualize** the subsolutions.
* Do NOT invent new facts, concepts, or assumptions.
* Do NOT assume access to the original subproblems.
* Do NOT mention agents, graphs, nodes, prompts, or internal system mechanics.
* Do NOT quote subsolutions verbatim unless necessary for precision—prefer synthesis.

---

### Reasoning and synthesis requirements

* Identify the **key contributions** of each subsolution.
* Merge them into a **unified explanation or answer**.
* If subsolutions:

  * Overlap → consolidate them
  * Complement → integrate them
  * Slightly conflict → explicitly reconcile or state the limitation
* If the combined information is **insufficient** to fully solve the problem:

  * State this clearly
  * Explain what is missing

> Internally reason as needed, but **do not expose chain-of-thought**.

---

### Output requirements

Your output must:

* Directly answer the stated problem
* Be logically structured and easy to follow
* Reflect combined insights rather than isolated summaries
* Be self-contained and readable without access to subsolutions
* Match the technical depth implied by the problem

---

### Failure handling

If the problem cannot be reliably solved using the provided subsolutions and knowledge:

* Clearly state that a complete solution is not possible
* Explain why (e.g., missing dimension, unresolved contradiction)
* Do NOT speculate or fabricate an answer

---

### Style guidelines

* Clear, precise, and neutral tone
* Concise but complete
* Prefer comparative, integrative, or decision-oriented phrasing when appropriate

---

### Final instruction

Your sole responsibility is to **combine the given subsolutions and knowledge into the best possible answer to the problem**.
"""


class AggregatorInput(BaseModel):
    """Input for the aggregator agent."""

    parent_requirement: Requirement  # The requirement we're solving
    child_solutions: list[Solution]  # Solutions from child requirements
    knowledge: str = ""  # Additional context


class AggregatorOutput(BaseModel):
    """Output from the aggregator agent."""

    solution: Solution  # Combined solution for this level
    synthesis: str  # How solutions were combined
    gaps: list[str]  # Any identified gaps


class AggregatorAgent(BaseAgent[AggregatorInput, AggregatorOutput]):
    """
    Aggregates child solutions into a unified solution for a parent requirement.

    Designed for hierarchical aggregation:
    - Takes solutions from child requirements
    - Combines them into a single solution for the parent
    - Can be called recursively for tree traversal

    Process:
    1. Generate N combined solutions
    2. Select the best combined solution
    3. Return with synthesis explanation and identified gaps
    """

    N_COMBINATIONS = 3  # Number of combination candidates to generate

    def __init__(self):
        super().__init__(
            name="aggregator",
            instructions=SYSTEM_PROMPT,
        )

    async def _create_combination(
        self, knowledge: str, problem: str, subsolutions: list[str]
    ) -> str:
        """Generate a single combined solution."""
        subsolutions_text = "\n".join(subsolutions)
        query = (
            f"Knowledge: {knowledge}\n\n"
            f"Problem: {problem}\n\n"
            f"Subsolutions:\n{subsolutions_text}"
        )
        result = await self._agent.run(query)
        return result.text

    async def _combine_solutions(
        self, knowledge: str, problem: str, subsolutions: list[str]
    ) -> list[str]:
        """Generate N combined solution candidates."""
        combinations = []
        for _ in range(self.N_COMBINATIONS):
            combination = await self._create_combination(
                knowledge, problem, subsolutions
            )
            combinations.append(combination)
            # Small delay to encourage diverse responses
            await asyncio.sleep(0.25)
        return combinations

    async def _select_best_solution(
        self, knowledge: str, problem: str, solutions: list[str]
    ) -> int:
        """Select the best combined solution using LLM."""
        solutions_text = "\n".join(
            [f"{i}. {s}" for i, s in enumerate(solutions)]
        )
        query = (
            f"Knowledge: {knowledge}\n\n"
            f"Problem: {problem}\n\n"
            f"Solutions:\n{solutions_text}\n\n"
            f"Which solution satisfies the problem the best? "
            f"Provide only the index number of the best solution!"
        )
        result = await self._agent.run(query)

        # Parse the index from response
        try:
            index = int(result.text.strip())
            if 0 <= index < len(solutions):
                return index
        except ValueError:
            pass

        # Default to first solution if parsing fails
        return 0

    async def _identify_gaps(
        self, problem: str, solution: str
    ) -> list[str]:
        """Identify any gaps in the combined solution."""
        query = (
            f"Problem: {problem}\n\n"
            f"Solution: {solution}\n\n"
            "What important aspects of the problem are NOT addressed by this solution? "
            "List each gap on a new line. If no gaps exist, respond with 'NONE'."
        )
        result = await self._agent.run(query)

        if "NONE" in result.text.upper():
            return []

        # Parse gaps from response
        gaps = [
            line.strip()
            for line in result.text.strip().split("\n")
            if line.strip() and not line.strip().upper() == "NONE"
        ]
        return gaps

    async def execute(self, input_data: AggregatorInput) -> AggregatorOutput:
        """
        Aggregate child solutions into a unified solution.

        Args:
            input_data: AggregatorInput with parent requirement, child solutions, and knowledge

        Returns:
            AggregatorOutput with combined solution, synthesis, and gaps
        """
        problem = input_data.parent_requirement.content
        knowledge = input_data.knowledge or "No additional context provided."

        # Extract solution contents from child solutions
        subsolutions = [sol.content for sol in input_data.child_solutions]

        if not subsolutions:
            # No child solutions to combine
            return AggregatorOutput(
                solution=Solution(
                    requirement_id=input_data.parent_requirement.id,
                    content="No child solutions available to combine.",
                    reasoning_chain=["No input solutions provided"],
                    source=SolutionSource.NOVEL,
                    confidence=0.0,
                ),
                synthesis="No child solutions were provided for aggregation.",
                gaps=["All aspects of the problem remain unaddressed"],
            )

        # Generate N combined solutions
        combinations = await self._combine_solutions(
            knowledge, problem, subsolutions
        )

        # Select the best combined solution
        best_index = await self._select_best_solution(
            knowledge, problem, combinations
        )
        best_solution_text = combinations[best_index]

        # Identify any gaps
        gaps = await self._identify_gaps(problem, best_solution_text)

        # Calculate confidence based on number of child solutions and gaps
        base_confidence = min(0.9, 0.5 + (len(subsolutions) * 0.1))
        gap_penalty = len(gaps) * 0.1
        confidence = max(0.3, base_confidence - gap_penalty)

        # Create the combined Solution object with aggregation tracking
        solution = Solution(
            requirement_id=input_data.parent_requirement.id,
            content=best_solution_text,
            reasoning_chain=[
                f"Combined {len(subsolutions)} child solutions",
                f"Generated {self.N_COMBINATIONS} combination candidates",
                f"Selected combination {best_index} as the best",
                f"Identified {len(gaps)} gaps",
            ],
            source=SolutionSource.NOVEL,
            confidence=confidence,
            is_aggregated=True,
            child_solution_ids=[sol.id for sol in input_data.child_solutions],
        )

        # Create synthesis explanation
        synthesis = (
            f"Combined {len(subsolutions)} child solutions into a unified answer. "
            f"Generated {self.N_COMBINATIONS} candidates and selected the best one. "
            f"Confidence: {confidence:.2f}"
        )
        if gaps:
            synthesis += f" Identified {len(gaps)} gap(s) for future work."

        return AggregatorOutput(
            solution=solution,
            synthesis=synthesis,
            gaps=gaps,
        )
