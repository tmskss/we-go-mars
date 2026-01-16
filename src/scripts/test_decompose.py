import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

from src.agents.requirement_decomposer import RequirementDecomposerAgent
from src.models.hypothesis import Hypothesis



async def run_test():
    agent = RequirementDecomposerAgent()

    hypothesis = Hypothesis(
        original_text="Summarize the mission context for a crewed Mars expedition with emphasis on radiation protection: mission phases/timelines, dominant radiation hazards per phase, and current NASA/ESA/CNSA dose limits (include notable pending policy changes). Identify contingency cases that could alter exposure budgets.",
        refined_text="",
        context="",
    )

    tree = await agent.execute(hypothesis)

    # Basic sanity checks
    assert tree.root is not None
    assert tree.total_nodes > 1
    assert tree.max_depth > 0

    # Print tree for visual inspection
    def print_tree(req, indent=0):
        print("  " * indent + f"- {req.content}")
        for child in getattr(req, "children", []):
            print_tree(child, indent + 1)

    print("\nRequirement Tree:")
    print_tree(tree.root)

    print("\nTest passed.")
    print(f"Total nodes: {tree.total_nodes}")
    print(f"Max depth: {tree.max_depth}")


if __name__ == "__main__":
    asyncio.run(run_test())
