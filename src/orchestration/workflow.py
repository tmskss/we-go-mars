"""
Main workflow orchestrator.

This is the central coordinator that runs the entire research workflow
from hypothesis to final research plan.

Owner: [ASSIGN TEAMMATE]
"""

from uuid import UUID
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import settings
from src.models.hypothesis import Hypothesis
from src.models.requirement import Requirement, RequirementGraph, RequirementStatus
from src.models.research_plan import ResearchPlan
from src.models.solution import Solution, SolutionSource

from src.agents.deep_researcher import DeepResearcherAgent
from src.agents.requirement_decomposer import RequirementDecomposerAgent
from src.agents.proposer import ProposerAgent, ProposerInput
from src.agents.aggregator import AggregatorAgent, AggregatorInput
from src.agents.plan_synthesizer import PlanSynthesizerAgent
from src.agents.retriever import RetrieverAgent, RetrieverAgentInput

console = Console()


class ResearchWorkflow:
    """
    Orchestrates the complete research workflow.

    Workflow Phases:
    1. Deep Research - Analyze hypothesis, generate questions
    2. Requirement Decomposition - Build requirement graph with deduplication
    3. Bottom-up Solving - Level-by-level solving from leaves to root
    4. Synthesis - Generate final research plan
    """

    def __init__(self):
        """Initialize all agents."""
        self.deep_researcher = DeepResearcherAgent()
        self.decomposer = RequirementDecomposerAgent()
        self.aggregator = AggregatorAgent()
        self.synthesizer = PlanSynthesizerAgent()
        self.retriever = RetrieverAgent()
        self.proposers = [
            ProposerAgent(i) for i in range(settings.proposer_count)
        ]

    async def run(self, hypothesis_text: str) -> ResearchPlan:
        """
        Execute the complete research workflow.

        Args:
            hypothesis_text: The user's research hypothesis

        Returns:
            Complete ResearchPlan
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Phase 1: Deep Research
            task = progress.add_task("Phase 1: Deep Research...", total=None)
            hypothesis = await self._phase_deep_research(hypothesis_text)
            progress.update(task, completed=True)

            # Phase 2: User Clarification (if needed)
            if hypothesis.clarifying_questions:
                task = progress.add_task("Phase 2: Getting clarifications...", total=None)
                hypothesis = await self._phase_clarification(hypothesis)
                progress.update(task, completed=True)

            # Phase 3: Requirement Decomposition (now builds graph with deduplication)
            task = progress.add_task("Phase 3: Decomposing requirements...", total=None)
            req_graph = await self._phase_decomposition(hypothesis)
            progress.update(task, completed=True)

            console.print(
                f"[green]Graph built: {req_graph.total_nodes} nodes, "
                f"{req_graph.shared_count} shared, "
                f"max depth {req_graph.max_depth}[/green]"
            )

            # Phase 4: Bottom-up Solving (combines context search, solving, aggregation)
            task = progress.add_task("Phase 4: Bottom-up solving...", total=None)
            solutions = await self._phase_bottom_up_solving(req_graph)
            progress.update(task, completed=True)

            # Root solution is the final aggregation
            root_solution = solutions.get(req_graph.root_id)

            # Phase 5: Plan Synthesis
            task = progress.add_task("Phase 5: Synthesizing research plan...", total=None)
            plan = await self._phase_synthesis(hypothesis, root_solution)
            progress.update(task, completed=True)

        return plan

    async def _phase_deep_research(self, hypothesis_text: str) -> Hypothesis:
        """Phase 1: Deep research on the hypothesis."""
        return await self.deep_researcher.execute(hypothesis_text)

    async def _phase_clarification(self, hypothesis: Hypothesis) -> Hypothesis:
        """Phase 2: Get user clarifications."""
        # TODO: Implement user interaction for clarifications
        # For hackathon, might skip or use defaults
        return hypothesis

    async def _phase_decomposition(self, hypothesis: Hypothesis) -> RequirementGraph:
        """Phase 3: Decompose into requirement graph with deduplication."""
        return await self.decomposer.execute(hypothesis)

    async def _phase_bottom_up_solving(
        self,
        graph: RequirementGraph,
    ) -> dict[UUID, Solution]:
        """
        Phase 4: Bottom-up solving from leaves to root.

        Process:
        1. Solve all atomic (leaf) requirements
        2. For each level from max_depth-1 to 0:
           - Aggregate child solutions for each node
        3. Root solution is final aggregation

        CRITICAL: When a shared node gets solved, ALL parents reference
        the SAME solution (no redundant computation).

        Args:
            graph: RequirementGraph with hierarchical structure

        Returns:
            Dictionary mapping requirement IDs to solutions
        """
        solutions: dict[UUID, Solution] = {}

        # Step 1: Solve atomic requirements (leaves)
        atomic_reqs = graph.get_atomic_requirements()
        console.print(f"[blue]Solving {len(atomic_reqs)} atomic requirements...[/blue]")

        for req in atomic_reqs:
            # Skip if already solved (shared node processed earlier)
            if req.id in solutions:
                console.print(
                    f"[yellow]Skipping shared node (already solved): "
                    f"{req.content[:40]}...[/yellow]"
                )
                continue

            # Check RAG for existing solution
            retrieval_result = await self.retriever.execute(
                RetrieverAgentInput(query=req.content, top_k=5)
            )

            if retrieval_result.success and retrieval_result.chunks:
                # Found relevant existing knowledge - create solution from it
                solution = Solution(
                    requirement_id=req.id,
                    content=retrieval_result.chunks,
                    reasoning_chain=[
                        f"Retrieved from: {', '.join(retrieval_result.sources)}"
                    ],
                    source=SolutionSource.EXISTING,
                    confidence=0.7,
                )
            else:
                # Generate novel solution
                context = retrieval_result.chunks if retrieval_result.success else ""
                proposer = self.proposers[0]
                result = await proposer.execute(
                    ProposerInput(requirement=req, context=context)
                )
                solution = result.solution

            solutions[req.id] = solution
            req.solution_id = solution.id
            req.status = RequirementStatus.SOLVED

        # Step 2: Bottom-up aggregation level by level
        for level in range(graph.max_depth - 1, -1, -1):
            level_nodes = graph.get_level_nodes(level)
            non_leaf_nodes = [n for n in level_nodes if graph.get_children(n.id)]

            if non_leaf_nodes:
                console.print(
                    f"[blue]Aggregating {len(non_leaf_nodes)} nodes at level {level}...[/blue]"
                )

            for node in non_leaf_nodes:
                # Skip if already solved (shouldn't happen, but safety check)
                if node.id in solutions:
                    continue

                # Get children's solutions
                children = graph.get_children(node.id)
                child_solutions = [
                    solutions[child.id]
                    for child in children
                    if child.id in solutions
                ]

                if not child_solutions:
                    console.print(
                        f"[red]Warning: No child solutions for {node.content[:40]}...[/red]"
                    )
                    continue

                # Deduplicate solutions (shared nodes may appear multiple times)
                seen_ids = set()
                unique_solutions = []
                for sol in child_solutions:
                    if sol.id not in seen_ids:
                        unique_solutions.append(sol)
                        seen_ids.add(sol.id)

                # Get additional context
                retrieval_result = await self.retriever.execute(
                    RetrieverAgentInput(query=node.content, top_k=5)
                )
                knowledge = retrieval_result.chunks if retrieval_result.success else ""

                # Aggregate
                agg_result = await self.aggregator.execute(
                    AggregatorInput(
                        parent_requirement=node,
                        child_solutions=unique_solutions,
                        knowledge=knowledge,
                    )
                )

                solutions[node.id] = agg_result.solution
                node.solution_id = agg_result.solution.id
                node.status = RequirementStatus.SOLVED

        return solutions

    async def _phase_synthesis(
        self, hypothesis: Hypothesis, root_solution: Solution | None
    ) -> ResearchPlan:
        """Phase 5: Synthesize final research plan."""
        return await self.synthesizer.execute(hypothesis, root_solution)
