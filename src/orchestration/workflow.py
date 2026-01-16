"""
Main workflow orchestrator.

This is the central coordinator that runs the entire research workflow
from hypothesis to final research plan.

Owner: [ASSIGN TEAMMATE]
"""

import asyncio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import settings
from src.models.hypothesis import Hypothesis
from src.models.requirement import Requirement, RequirementTree
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
    2. Requirement Decomposition - Build requirement tree
    3. Context Search - Find existing solutions
    4. Solution Generation - Generate solutions for requirements
    5. Aggregation - Combine all solutions
    6. Synthesis - Generate final research plan
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

            # Phase 3: Requirement Decomposition
            task = progress.add_task("Phase 3: Decomposing requirements...", total=None)
            req_tree = await self._phase_decomposition(hypothesis)
            progress.update(task, completed=True)

            # Phase 4: Context Search
            task = progress.add_task("Phase 4: Searching for existing solutions...", total=None)
            existing, needs_solving = await self._phase_context_search(req_tree)
            progress.update(task, completed=True)

            # Phase 5: Solution Generation
            task = progress.add_task("Phase 5: Generating solutions...", total=None)
            solutions = await self._phase_solving(needs_solving)
            all_solutions = existing + solutions
            progress.update(task, completed=True)

            # Phase 6: Aggregation
            task = progress.add_task("Phase 6: Aggregating solutions...", total=None)
            aggregated = await self._phase_aggregation(req_tree.root, all_solutions)
            progress.update(task, completed=True)

            # Phase 7: Plan Synthesis
            task = progress.add_task("Phase 7: Synthesizing research plan...", total=None)
            plan = await self._phase_synthesis(hypothesis, aggregated)
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

    async def _phase_decomposition(self, hypothesis: Hypothesis) -> RequirementTree:
        """Phase 3: Decompose into requirement tree."""
        return await self.decomposer.execute(hypothesis)

    def _get_atomic_requirements(self, req_tree: RequirementTree) -> list[Requirement]:
        """
        Get all atomic (leaf) requirements from the tree.

        Traverses the tree to find all requirements without children.
        """
        atomic = []

        def traverse(req: Requirement):
            if not req.children:
                # Leaf node = atomic requirement
                atomic.append(req)
            else:
                for child in req.children:
                    traverse(child)

        traverse(req_tree.root)
        return atomic

    async def _phase_context_search(
        self, req_tree: RequirementTree
    ) -> tuple[list[Solution], list[Requirement]]:
        """
        Phase 4: Search for existing solutions in RAG.

        For each atomic requirement:
        1. Use RetrieverAgent to search literature
        2. If relevant content found, create an existing solution
        3. Otherwise, mark requirement as needing novel solution

        Returns:
            (existing_solutions, requirements_needing_solutions)
        """
        atomic_reqs = self._get_atomic_requirements(req_tree)

        existing_solutions: list[Solution] = []
        needs_solving: list[Requirement] = []

        for req in atomic_reqs:
            # Search for existing knowledge
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
                existing_solutions.append(solution)
            else:
                # No relevant knowledge found - needs novel solution
                needs_solving.append(req)

        return existing_solutions, needs_solving

    async def _phase_solving(self, requirements: list[Requirement]) -> list[Solution]:
        """
        Phase 5: Generate solutions for requirements.

        For each requirement:
        1. Get context via RetrieverAgent
        2. Run proposer to generate solution
        """
        solutions: list[Solution] = []

        for req in requirements:
            # Get context for the requirement
            retrieval_result = await self.retriever.execute(
                RetrieverAgentInput(query=req.content, top_k=5)
            )
            context = retrieval_result.chunks if retrieval_result.success else ""

            # Use first proposer (we have multiple for parallel solving if needed)
            proposer = self.proposers[0]
            proposer_input = ProposerInput(requirement=req, context=context)
            result = await proposer.execute(proposer_input)

            solutions.append(result.solution)

        return solutions

    async def _phase_aggregation(
        self, root_requirement: Requirement, solutions: list[Solution]
    ):
        """
        Phase 6: Aggregate all solutions.

        Currently performs single-level aggregation of all atomic solutions.
        Future: Hierarchical tree traversal when requirement decomposition is finalized.
        """
        # Get additional context for the root problem
        retrieval_result = await self.retriever.execute(
            RetrieverAgentInput(query=root_requirement.content, top_k=5)
        )
        knowledge = retrieval_result.chunks if retrieval_result.success else ""

        # Create aggregator input
        aggregator_input = AggregatorInput(
            parent_requirement=root_requirement,
            child_solutions=solutions,
            knowledge=knowledge,
        )

        return await self.aggregator.execute(aggregator_input)

    async def _phase_synthesis(self, hypothesis: Hypothesis, aggregated) -> ResearchPlan:
        """Phase 7: Synthesize final research plan."""
        return await self.synthesizer.execute(hypothesis, aggregated)
