"""
Requirement Decomposer Agent.

Decomposes requirements into a hierarchical graph structure with
semantic deduplication for shared atomic nodes.

Owner: [ASSIGN TEAMMATE]
"""

import json
from typing import List

from openai import AsyncOpenAI

from src.agents.base import BaseAgent
from src.agents.similarity_checker import (
    SimilarityCheckerAgent,
    SimilarityCheckerInput,
)
from src.models.hypothesis import Hypothesis
from src.models.requirement import Requirement, RequirementGraph
from src.rag.requirement_store import RequirementStore

client = AsyncOpenAI()

SYSTEM_PROMPT = """You are a Recursive Research Decomposition Agent.

Your goal is to determine if a given query is "Atomic" or "Complex."
- **Atomic:** A query that is specific enough to be answered by a single Google search, a specific fact lookup, or a direct definition.
- **Complex:** A query that requires synthesizing information from multiple distinct sub-topics or perspectives.

### Instructions
1. **Analyze the Input:** specificy the current level of complexity.
2. **If Complex:** Break the query down into 2-4 **immediate** sub-questions. Do not try to reach the bottom of the tree instantly; just identify the next logical layer of questions.
3. **If Atomic:** Return an empty list `[]`. This signals the system to execute a search rather than decomposing further.
4. **Context:** Ensure sub-questions are self-contained (mention the specific subject, avoid "it/they").

### Output Format
Output **valid JSON only**.

**Example (Complex):**
Input: "Compare the EV markets in China and the USA."
Output: { "sub_questions": ["What is the current state of the EV market in China?", "What is the current state of the EV market in the USA?"] }

**Example (Atomic):**
Input: "What is the current state of the EV market in China?"
Output: { "sub_questions": [] }
"""


class RequirementDecomposerAgent(BaseAgent[Hypothesis, RequirementGraph]):
    """
    Decomposes requirements into a hierarchical graph structure with deduplication.

    Key features:
    - Graph structure allowing shared atomic nodes
    - Semantic deduplication via RequirementStore
    - Level-based crossover constraint (only match at child level)
    """

    MAX_LEVEL = 4

    def __init__(
        self,
        top_k_candidates: int = 5,
        similarity_threshold: float = 0.75,
    ):
        """
        Initialize the decomposer agent.

        Args:
            top_k_candidates: Number of candidates to retrieve for deduplication
            similarity_threshold: Minimum similarity score for candidates
        """
        super().__init__(
            name="requirement_decomposer",
            instructions=SYSTEM_PROMPT,
        )
        self.requirement_store = RequirementStore()
        self.similarity_checker = SimilarityCheckerAgent()
        self.top_k_candidates = top_k_candidates
        self.similarity_threshold = similarity_threshold

    async def execute(self, input_data: Hypothesis) -> RequirementGraph:
        """
        Execute decomposition with deduplication.

        Args:
            input_data: Hypothesis to decompose

        Returns:
            RequirementGraph with hierarchical structure and shared nodes
        """
        # Clear store for new session
        self.requirement_store.clear()

        root_text = input_data.refined_text or input_data.original_text
        root = Requirement(
            content=f"How to {root_text.strip('?')}",
            level=0,
            parent_ids=[],
        )

        # Initialize graph
        graph = RequirementGraph(root_id=root.id)
        graph.add_node(root)

        # Index root requirement
        self.requirement_store.add_requirement(root)

        async def recurse(req: Requirement):
            if req.level >= self.MAX_LEVEL:
                return

            # Decompose into sub-questions (returns content strings)
            raw_children = await self.decompose_single(req)

            for child_content in raw_children:
                child_level = req.level + 1

                # Search for similar at child_level ONLY (level constraint)
                candidates = self.requirement_store.find_similar(
                    content=child_content,
                    level=child_level,
                    top_k=self.top_k_candidates,
                    score_threshold=self.similarity_threshold,
                )

                if candidates:
                    # Use SimilarityCheckerAgent to decide
                    result = await self.similarity_checker.execute(
                        SimilarityCheckerInput(
                            new_content=child_content,
                            candidates=candidates,
                        )
                    )

                    if result.has_match and result.matched_id:
                        # Link to existing node (deduplication)
                        graph.link_existing_child(req.id, result.matched_id)
                        print(
                            f"[DEDUP] Reusing existing node for: "
                            f"{child_content[:50]}..."
                        )
                        print(f"[DEDUP] Reason: {result.reason}")
                        # Don't recurse - already decomposed
                        continue

                # No match: create new node
                child = Requirement(
                    content=child_content.strip(),
                    level=child_level,
                    parent_ids=[req.id],
                )
                graph.add_child(req.id, child)
                self.requirement_store.add_requirement(child)

                await recurse(child)

        await recurse(root)

        # Update atomic count
        graph.get_atomic_requirements()

        return graph

    async def decompose_single(self, requirement: Requirement) -> List[str]:
        """
        Decompose a single requirement into sub-questions.

        Args:
            requirement: Requirement object to decompose

        Returns:
            List of content strings (not Requirement objects)
        """
        print(f"Decomposing: {requirement.content}")

        response = await client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": requirement.content},
            ],
        )

        # Extract text from response
        text = response.output_text.strip()

        try:
            # Parse the JSON list of sub-requirements
            data = json.loads(text)
            return data.get("sub_questions", [])
        except Exception as e:
            print("Error parsing model output:", e)
            print("Raw output:", text)
            return []
