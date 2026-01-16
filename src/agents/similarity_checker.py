"""
Similarity Checker Agent for semantic deduplication.

This agent determines if a new requirement is semantically equivalent
to any existing candidates from the RequirementStore.

Owner: [ASSIGN TEAMMATE]
"""

import json
from uuid import UUID

from pydantic import BaseModel

from src.agents.base import BaseAgent
from src.rag.requirement_store import RequirementCandidate


SYSTEM_PROMPT = """You are a Semantic Similarity Judge for research questions.

Your task is to determine if a NEW question is semantically equivalent to any EXISTING questions.

Two questions are equivalent if:
- They ask about the same fundamental concept or information
- An answer to one would fully answer the other
- They differ only in phrasing, not substance

IMPORTANT: Output your reasoning BEFORE the verdict.

Output **valid JSON only** in this format:
{"reason": "<your analysis of each candidate>", "match_index": <index of matching candidate, or -1 if no match>}

### Example

NEW: "What is the current market size of EVs in China?"
EXISTING:
0. "How large is China's EV market today?"
1. "Who are the main EV manufacturers in China?"

Output: {"reason": "Question 0 asks about China's EV market size, which is semantically equivalent to the NEW question about market size. Question 1 asks about manufacturers, which is a different concept.", "match_index": 0}

### Another Example

NEW: "What are the safety regulations for autonomous vehicles?"
EXISTING:
0. "How do self-driving cars navigate city traffic?"
1. "What is the fuel efficiency of electric vehicles?"

Output: {"reason": "Question 0 is about navigation technology, not safety regulations. Question 1 is about fuel efficiency for EVs, unrelated to autonomous vehicle safety. Neither matches the NEW question about safety regulations.", "match_index": -1}
"""


class SimilarityCheckerInput(BaseModel):
    """Input for similarity checking."""

    new_content: str
    candidates: list[RequirementCandidate]


class SimilarityCheckerOutput(BaseModel):
    """Output from similarity checker (reasoning before verdict)."""

    reason: str
    has_match: bool
    matched_id: UUID | None = None


class SimilarityCheckerAgent(BaseAgent[SimilarityCheckerInput, SimilarityCheckerOutput]):
    """
    Decides if a new requirement matches any existing candidates.

    Uses LLM to make semantic equivalence decisions with reasoning.
    """

    def __init__(self):
        super().__init__(
            name="similarity_checker",
            instructions=SYSTEM_PROMPT,
        )

    async def execute(
        self, input_data: SimilarityCheckerInput
    ) -> SimilarityCheckerOutput:
        """
        Check if new content matches any candidate.

        Args:
            input_data: Contains new_content and list of candidates

        Returns:
            SimilarityCheckerOutput with reason, has_match, and matched_id
        """
        if not input_data.candidates:
            return SimilarityCheckerOutput(
                reason="No candidates to compare against.",
                has_match=False,
                matched_id=None,
            )

        # Format candidates for LLM
        candidates_text = "\n".join(
            [f"{i}. {c.content}" for i, c in enumerate(input_data.candidates)]
        )

        prompt = f"""NEW: {input_data.new_content}

EXISTING:
{candidates_text}"""

        result = await self.run(prompt)

        try:
            data = json.loads(result.strip())
            reason = data.get("reason", "No reasoning provided.")
            match_index = data.get("match_index", -1)

            if 0 <= match_index < len(input_data.candidates):
                return SimilarityCheckerOutput(
                    reason=reason,
                    has_match=True,
                    matched_id=input_data.candidates[match_index].requirement_id,
                )

            return SimilarityCheckerOutput(
                reason=reason,
                has_match=False,
                matched_id=None,
            )

        except json.JSONDecodeError as e:
            print(f"[SimilarityChecker] Error parsing LLM response: {e}")
            print(f"[SimilarityChecker] Raw output: {result}")
            return SimilarityCheckerOutput(
                reason=f"Failed to parse LLM response: {result[:200]}",
                has_match=False,
                matched_id=None,
            )
