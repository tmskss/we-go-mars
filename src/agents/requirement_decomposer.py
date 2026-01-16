import json
import os
from typing import List

from openai import AsyncOpenAI

from src.agents.base import BaseAgent
from src.models.hypothesis import Hypothesis
from src.models.requirement import Requirement, RequirementTree

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


class RequirementDecomposerAgent(BaseAgent[Hypothesis, RequirementTree]):
    """
    Decomposes requirements into a hierarchical tree structure.
    """

    def __init__(self):
        super().__init__(
            name="requirement_decomposer",
            instructions=SYSTEM_PROMPT,
        )

    async def execute(self, input_data: Hypothesis) -> RequirementTree:
        root_text = input_data.refined_text or input_data.original_text

        root = Requirement(
            content=f"How to {root_text.strip('?')}",
            level=0,
        )

        total_nodes = 1
        max_depth = 1
        MAX_LEVEL = 4

        async def recurse(req: Requirement):
            nonlocal total_nodes, max_depth

            if req.level>=MAX_LEVEL: return

            children = await self.decompose_single(req)
            req.children = children

            if children:
                max_depth = max(max_depth, req.level + 1)

            for child in children:
                total_nodes += 1
                await recurse(child)

        await recurse(root)

        return RequirementTree(
            root=root,
            total_nodes=total_nodes,
            max_depth=max_depth,
        )


    async def decompose_single(self, requirement: Requirement) -> List[Requirement]:
        """
        Decompose a single requirement into child requirements.

        Args:
            requirement: Requirement object to decompose

        Returns:
            List[Requirement] objects (children)
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
            sub_reqs = data.get("sub_questions", [])
        except Exception as e:
            print("Error parsing model output:", e)
            print("Raw output:", text)
            sub_reqs = []

        # Wrap strings as Requirement objects
        children = [
            Requirement(
                content=sub_req.strip(),
                level=requirement.level + 1,
            )
            for sub_req in sub_reqs
        ]

        return children
