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
        original_text="Summarize the mission context for a crewed Mars expedition with emphasis on radiation protection: dominant radiation hazards per phase, and current NASA/ESA/CNSA dose limits.",
        refined_text="",
        context="",
    )

    tree = await agent.execute(hypothesis)

    # Basic sanity checks
    assert tree.get_root() is not None
    assert tree.total_nodes > 1
    assert tree.max_depth > 0

    # Print graph for visual inspection
    def print_graph(node, graph, indent=0, visited=None):
        """Print graph structure, handling shared nodes."""
        if visited is None:
            visited = set()

        # Mark shared nodes
        shared_marker = " [SHARED]" if node.is_shared else ""

        # Mark if we've already printed this node
        already_printed = " (see above)" if node.id in visited else ""

        print("  " * indent + f"- {node.content}{shared_marker}{already_printed}")

        # If already visited, don't recurse again to avoid infinite loops
        if node.id in visited:
            return

        visited.add(node.id)

        # Get children from the graph
        children = graph.get_children(node.id)
        for child in children:
            print_graph(child, graph, indent + 1, visited)

    print("\nRequirement Graph:")
    print_graph(tree.get_root(), tree)

    print("\nTest passed.")
    print(f"Total nodes: {tree.total_nodes}")
    print(f"Max depth: {tree.max_depth}")
    print(f"Atomic nodes: {tree.atomic_count}")
    print(f"Shared nodes: {tree.shared_count}")


if __name__ == "__main__":
    asyncio.run(run_test())
