"""
Proposer Agent for solution generation.

This agent generates a single solution for an atomic requirement
using the provided context from the knowledge base.

Owner: [ASSIGN TEAMMATE]
"""

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
    Generates a single solution for an atomic requirement.

    Input: Atomic requirement + context
    Output: ProposerOutput with solution
    """

    def __init__(self, instance_id: int = 0):
        super().__init__(
            name=f"proposer_{instance_id}",
            instructions=SYSTEM_PROMPT,
        )
        self.instance_id = instance_id

    async def execute(self, input_data: ProposerInput) -> ProposerOutput:
        """
        Generate a solution for the given requirement.

        Args:
            input_data: ProposerInput containing requirement and context

        Returns:
            ProposerOutput with the solution
        """
        knowledge = input_data.context or "No additional context provided."
        problem = input_data.requirement.content

        query = f"Knowledge: {knowledge}\n\nProblem: {problem}"
        result = await self._agent.run(query)

        solution = Solution(
            requirement_id=input_data.requirement.id,
            content=result.text,
            reasoning_chain=["Generated solution from context"],
            source=SolutionSource.NOVEL,
            confidence=0.8,
        )

        return ProposerOutput(solution=solution)
