"""
Proposer Agent for solution generation.

This agent generates solution candidates by creating N solutions
and selecting the best one using LLM evaluation.

Owner: [ASSIGN TEAMMATE]
"""

import asyncio
from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.models.requirement import Requirement
from src.models.solution import Solution, SolutionSource


SYSTEM_PROMPT = """**SYSTEM INSTRUCTION FOR SolutionAgent**

You are **SolutionAgent**, an expert problem-solving assistant.

Your task is to generate a **clear, correct, and complete solution** to a given problem using **only the provided knowledge**.

### Inputs you will receive

You will receive a single input containing two parts:

1. **Knowledge**

   * This is a concatenation of multiple knowledge chunks retrieved by another agent (RetrieverAgent).
   * The knowledge may include:

     * Theoretical explanations
     * Applied methods
     * Experimental findings
     * Algorithms, formulas, or procedures
     * Assumptions and constraints
   * The knowledge may be redundant, partially overlapping, or loosely structured.

2. **Problem**

   * A concrete problem statement that must be solved using the provided knowledge.
   * The problem may be technical, mathematical, conceptual, or applied.

### Your objective

Produce a **solution that directly answers the problem**, grounded in the provided knowledge.

### Mandatory rules

* **Use only the provided knowledge** to derive your solution.

  * Do NOT introduce external facts, assumptions, or prior knowledge not present in the knowledge text.
* If the knowledge is **insufficient, contradictory, or incomplete**, explicitly state this and explain what is missing.
* Do NOT mention the existence of agents, prompts, models, APIs, or internal processes.
* Do NOT repeat the knowledge verbatim unless necessary for clarity.
* Do NOT hallucinate citations, equations, methods, or results.

### Reasoning requirements

* Internally synthesize and reason over the knowledge, but **do not expose chain-of-thought**.
* Present only the **final, well-structured reasoning outcome**, not intermediate deliberations.

### Output requirements

Your output must:

* Be written in **clear, precise, and technical language** appropriate to the problem domain.
* Directly address the problem without unnecessary background.
* Be logically structured (e.g., steps, bullet points, equations, or concise paragraphs as appropriate).
* Include formulas, algorithms, or procedural steps **only if they are supported by the knowledge**.
* Be self-contained and understandable without referencing the original knowledge text.

### Failure handling

If the problem **cannot be solved** using the provided knowledge:

* Clearly state that a complete solution is not possible.
* Identify exactly which information or assumptions are missing.
* Do NOT attempt to guess or fabricate a solution.

### Style guidelines

* Be concise but complete.
* Prefer precision over verbosity.
* Avoid speculation or vague language.

### Final instruction

Your sole responsibility is to produce the **best possible solution to the given problem based strictly on the provided knowledge**.
"""


class ProposerInput(BaseModel):
    """Input for proposer agent."""

    requirement: Requirement
    context: str = ""  # Knowledge from RetrieverAgent


class ProposerOutput(BaseModel):
    """Output from the proposer agent."""

    solution: Solution


class ProposerAgent(BaseAgent[ProposerInput, ProposerOutput]):
    """
    Generates solutions using N-solution generation and selection.

    Process:
    1. Generate N candidate solutions
    2. Use LLM to select the best solution
    3. Return the best solution

    Input: Atomic requirement + context
    Output: ProposerOutput with solution
    """

    N_SOLUTIONS = 3  # Number of candidate solutions to generate

    def __init__(self, instance_id: int = 0):
        super().__init__(
            name=f"proposer_{instance_id}",
            instructions=SYSTEM_PROMPT,
        )
        self.instance_id = instance_id

    async def _create_solution(self, knowledge: str, problem: str) -> str:
        """Generate a single solution candidate."""
        query = f"Knowledge: {knowledge}\n\nProblem: {problem}"
        result = await self._agent.run(query)
        return result.text

    async def _create_solutions(
        self, knowledge: str, problem: str
    ) -> list[str]:
        """Generate N solution candidates."""
        # Generate solutions sequentially to ensure diversity
        solutions = []
        for _ in range(self.N_SOLUTIONS):
            solution = await self._create_solution(knowledge, problem)
            solutions.append(solution)
            # Small delay to encourage diverse responses
            await asyncio.sleep(0.25)
        return solutions

    async def _select_best_solution(
        self, knowledge: str, problem: str, solutions: list[str]
    ) -> int:
        """Select the best solution from candidates using LLM."""
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

    async def execute(self, input_data: ProposerInput) -> ProposerOutput:
        """
        Generate a solution using N-solution generation and selection.

        Args:
            input_data: ProposerInput containing requirement and context

        Returns:
            ProposerOutput with the best solution
        """
        knowledge = input_data.context or "No additional context provided."
        problem = input_data.requirement.content

        # Generate N candidate solutions
        solutions = await self._create_solutions(knowledge, problem)

        # Select the best solution
        best_index = await self._select_best_solution(
            knowledge, problem, solutions
        )
        best_solution_text = solutions[best_index]

        # Create the Solution object
        solution = Solution(
            requirement_id=input_data.requirement.id,
            content=best_solution_text,
            reasoning_chain=[
                f"Generated {self.N_SOLUTIONS} candidate solutions",
                f"Selected solution {best_index} as the best",
            ],
            source=SolutionSource.NOVEL,
            confidence=0.8,  # Base confidence, can be adjusted
        )

        return ProposerOutput(solution=solution)
