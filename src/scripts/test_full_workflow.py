"""
Full workflow integration test.

Tests the complete pipeline:
1. Problem decomposition (parallel)
2. Atomic problem solving
3. Bottom-up solution aggregation
4. Plan synthesis (two-iteration with gap filling)

Usage:
    python -m src.scripts.test_full_workflow
    python -m src.scripts.test_full_workflow --simple   # Simpler hypothesis for faster test
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

from src.agents.aggregator import AggregatorAgent, AggregatorInput
from src.agents.plan_synthesizer import PlanSynthesizerAgent, PlanSynthesizerInput
from src.agents.proposer import ProposerAgent, ProposerInput
from src.agents.requirement_decomposer import RequirementDecomposerAgent
from src.agents.retriever import RetrieverAgent, RetrieverAgentInput
from src.models.hypothesis import Hypothesis
from src.models.requirement import Requirement, RequirementGraph, RequirementStatus
from src.models.solution import Solution, SolutionSource

console = Console()


async def solve_atomic_requirements(
    graph: RequirementGraph,
    retriever: RetrieverAgent,
    proposer: ProposerAgent,
) -> dict[UUID, Solution]:
    """Solve all atomic (leaf) requirements in parallel."""
    atomic_reqs = graph.get_atomic_requirements()
    console.print(f"\n[bold blue]Solving {len(atomic_reqs)} atomic problems in parallel...[/bold blue]")

    # Track already-seen IDs to handle shared nodes
    seen_ids: set[UUID] = set()
    unique_reqs: list[Requirement] = []
    for req in atomic_reqs:
        if req.id not in seen_ids:
            unique_reqs.append(req)
            seen_ids.add(req.id)

    console.print(f"  ({len(unique_reqs)} unique after deduplication)")

    async def solve_single(req: Requirement) -> tuple[UUID, Solution]:
        """Solve a single atomic requirement."""
        # Check RAG for existing solution
        retrieval_result = await retriever.execute(
            RetrieverAgentInput(query=req.content, top_k=3)
        )

        if retrieval_result.success and retrieval_result.chunks:
            solution = Solution(
                requirement_id=req.id,
                content=retrieval_result.chunks,
                reasoning_chain=[f"Retrieved from: {', '.join(retrieval_result.sources)}"],
                source=SolutionSource.EXISTING,
                confidence=0.7,
            )
        else:
            # Generate novel solution
            context = retrieval_result.chunks if retrieval_result.success else ""
            result = await proposer.execute(
                ProposerInput(requirement=req, context=context)
            )
            solution = result.solution

        req.solution_id = solution.id
        req.status = RequirementStatus.SOLVED
        return req.id, solution

    # Solve all unique requirements in parallel
    results = await asyncio.gather(*[solve_single(req) for req in unique_reqs])

    # Build solutions dict
    solutions: dict[UUID, Solution] = {}
    for req_id, solution in results:
        solutions[req_id] = solution
        source_type = "RAG" if solution.source == SolutionSource.EXISTING else "Novel"
        console.print(f"  [green]Solved:[/green] {solution.content[:50]}... [{source_type}]")

    return solutions


async def aggregate_solutions(
    graph: RequirementGraph,
    solutions: dict[UUID, Solution],
    retriever: RetrieverAgent,
    aggregator: AggregatorAgent,
) -> dict[UUID, Solution]:
    """Bottom-up aggregation from leaves to root, parallel within each level."""
    console.print(f"\n[bold blue]Aggregating solutions bottom-up (parallel per level)...[/bold blue]")

    async def aggregate_single(
        node: Requirement,
    ) -> tuple[UUID, Solution, list[str]] | None:
        """Aggregate a single node from its children's solutions."""
        if node.id in solutions:
            return None

        # Get children's solutions
        children = graph.get_children(node.id)
        child_solutions = [
            solutions[child.id]
            for child in children
            if child.id in solutions
        ]

        if not child_solutions:
            return None

        # Deduplicate (shared nodes may appear multiple times)
        seen_ids: set[UUID] = set()
        unique_solutions: list[Solution] = []
        for sol in child_solutions:
            if sol.id not in seen_ids:
                unique_solutions.append(sol)
                seen_ids.add(sol.id)

        # Get additional context
        retrieval_result = await retriever.execute(
            RetrieverAgentInput(query=node.content, top_k=3)
        )
        knowledge = retrieval_result.chunks if retrieval_result.success else ""

        # Aggregate
        agg_result = await aggregator.execute(
            AggregatorInput(
                parent_requirement=node,
                child_solutions=unique_solutions,
                knowledge=knowledge,
            )
        )

        node.solution_id = agg_result.solution.id
        node.status = RequirementStatus.SOLVED

        return node.id, agg_result.solution, agg_result.gaps

    # Process level by level (must be sequential between levels)
    for level in range(graph.max_depth - 1, -1, -1):
        level_nodes = graph.get_level_nodes(level)
        non_leaf_nodes = [n for n in level_nodes if graph.get_children(n.id)]

        if not non_leaf_nodes:
            continue

        console.print(f"\n  [bold]Level {level}:[/bold] {len(non_leaf_nodes)} nodes to aggregate in parallel")

        # Aggregate all nodes at this level in parallel
        results = await asyncio.gather(*[aggregate_single(n) for n in non_leaf_nodes])

        # Collect results
        for result in results:
            if result is None:
                continue
            node_id, solution, gaps = result
            solutions[node_id] = solution
            gap_info = f" (gaps: {len(gaps)})" if gaps else ""
            console.print(f"    [green]Aggregated:[/green] {solution.content[:50]}...{gap_info}")

    return solutions


def print_solution_tree(graph: RequirementGraph, solutions: dict[UUID, Solution]):
    """Print the solution tree using rich."""
    root = graph.get_root()
    tree = Tree(f"[bold]{root.content}[/bold]")

    def add_node(parent_tree, node, visited=None):
        if visited is None:
            visited = set()

        if node.id in visited:
            return
        visited.add(node.id)

        solution = solutions.get(node.id)
        if solution:
            confidence = f"[{'green' if solution.confidence >= 0.7 else 'yellow'}]{solution.confidence:.2f}[/]"
            source = "[cyan]RAG[/cyan]" if solution.source == SolutionSource.EXISTING else "[magenta]Novel[/magenta]"
            label = f"{node.content[:60]}... [{confidence} | {source}]"
        else:
            label = f"[red]{node.content[:60]}... [UNSOLVED][/red]"

        if node.is_shared:
            label = f"[italic]{label} (shared)[/italic]"

        child_tree = parent_tree.add(label)

        for child in graph.get_children(node.id):
            add_node(child_tree, child, visited)

    for child in graph.get_children(root.id):
        add_node(tree, child, {root.id})

    console.print("\n")
    console.print(Panel(tree, title="[bold]Solution Tree[/bold]", expand=False))


async def run_full_workflow(hypothesis_text: str):
    """Run the complete decomposition -> solving -> aggregation workflow."""
    console.print(Panel(f"[bold]Hypothesis:[/bold]\n{hypothesis_text}", title="Input"))

    # Initialize agents
    decomposer = RequirementDecomposerAgent()
    retriever = RetrieverAgent()
    proposer = ProposerAgent(instance_id=0)
    aggregator = AggregatorAgent()

    # Phase 1: Decomposition
    console.print("\n[bold magenta]Phase 1: Problem Decomposition[/bold magenta]")
    console.print("-" * 50)

    hypothesis = Hypothesis(
        original_text=hypothesis_text,
        refined_text="",
        context="",
    )

    graph = await decomposer.execute(hypothesis)

    console.print(f"\n[green]Graph built successfully![/green]")
    console.print(f"  Total nodes: {graph.total_nodes}")
    console.print(f"  Max depth: {graph.max_depth}")
    console.print(f"  Atomic problems: {graph.atomic_count}")
    console.print(f"  Shared nodes: {graph.shared_count}")

    # Phase 2: Solve atomic requirements
    console.print("\n[bold magenta]Phase 2: Solving Atomic Problems[/bold magenta]")
    console.print("-" * 50)

    solutions = await solve_atomic_requirements(graph, retriever, proposer)

    console.print(f"\n[green]Solved {len(solutions)} atomic problems[/green]")

    # Phase 3: Bottom-up aggregation
    console.print("\n[bold magenta]Phase 3: Solution Aggregation[/bold magenta]")
    console.print("-" * 50)

    solutions = await aggregate_solutions(graph, solutions, retriever, aggregator)

    # Phase 4: Plan Synthesis (Two-Iteration)
    console.print("\n[bold magenta]Phase 4: Plan Synthesis[/bold magenta]")
    console.print("-" * 50)

    plan_synthesizer = PlanSynthesizerAgent()

    console.print("  Iteration 1: Analyzing gaps...")
    plan_result = await plan_synthesizer.execute(
        PlanSynthesizerInput(
            hypothesis=hypothesis,
            graph=graph,
            solutions=solutions,
        )
    )

    console.print(f"\n[green]Plan synthesized![/green]")
    console.print(f"  Total steps: {plan_result.final_plan.total_steps}")
    console.print(f"  Information complete: {plan_result.final_plan.steps_information_complete}")
    console.print(f"  Requires verification: {plan_result.final_plan.steps_requiring_verification}")
    console.print(f"  Remaining gaps: {len(plan_result.final_plan.remaining_gaps)}")

    # Results
    console.print("\n[bold magenta]Results[/bold magenta]")
    console.print("-" * 50)

    root_solution = solutions.get(graph.root_id)
    if root_solution:
        console.print(f"\n[bold green]Root solution generated![/bold green]")
        console.print(f"  Confidence: {root_solution.confidence:.2f}")
        console.print(f"  Is aggregated: {root_solution.is_aggregated}")
        console.print(f"  Child solutions: {len(root_solution.child_solution_ids)}")

        console.print("\n[bold]Final Solution Content:[/bold]")
        console.print(Panel(root_solution.content[:2000] + "..." if len(root_solution.content) > 2000 else root_solution.content))

    # Print solution tree
    print_solution_tree(graph, solutions)

    # Statistics
    console.print("\n[bold]Statistics:[/bold]")
    novel_count = sum(1 for s in solutions.values() if s.source == SolutionSource.NOVEL)
    existing_count = sum(1 for s in solutions.values() if s.source == SolutionSource.EXISTING)
    aggregated_count = sum(1 for s in solutions.values() if s.is_aggregated)
    avg_confidence = sum(s.confidence for s in solutions.values()) / len(solutions) if solutions else 0

    console.print(f"  Total solutions: {len(solutions)}")
    console.print(f"  Novel solutions: {novel_count}")
    console.print(f"  From RAG: {existing_count}")
    console.print(f"  Aggregated: {aggregated_count}")
    console.print(f"  Average confidence: {avg_confidence:.2f}")

    # Save outputs
    output_dir = ROOT_DIR / "outputs"
    output_dir.mkdir(exist_ok=True)

    graph.save_to_file(str(output_dir / "full_workflow_graph.json"))
    console.print(f"\n[dim]Graph saved to: {output_dir / 'full_workflow_graph.json'}[/dim]")

    # Save PLAN.md
    plan_path = output_dir / "PLAN.md"
    with open(plan_path, "w") as f:
        f.write(plan_result.plan_markdown)
    console.print(f"[dim]Plan saved to: {plan_path}[/dim]")

    # Display plan preview
    console.print("\n[bold]Plan Preview:[/bold]")
    preview = plan_result.plan_markdown[:2000] + "..." if len(plan_result.plan_markdown) > 2000 else plan_result.plan_markdown
    console.print(Panel(preview, title="PLAN.md"))

    # Cleanup: Clear the requirements database
    console.print("\n[dim]Cleaning up requirements database...[/dim]")
    decomposer.requirement_store.clear()

    return graph, solutions, plan_result


if __name__ == "__main__":
    if "--simple" in sys.argv:
        hypothesis = "Radiation protection for a crewed spacecraft transporting humans to Mars"
    else:
        hypothesis = (
            "Comprehensive radiation protection system for a crewed Mars transit vehicle, "
            "addressing GCR and SPE hazards during the 6-9 month journey"
        )

    asyncio.run(run_full_workflow(hypothesis))
