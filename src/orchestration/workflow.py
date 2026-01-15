"""
Main workflow orchestrator.

This is the central coordinator that runs the entire research workflow
from hypothesis to final research plan.

Owner: [ASSIGN TEAMMATE]
"""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import settings
from src.models.hypothesis import Hypothesis
from src.models.requirement import Requirement, RequirementTree
from src.models.research_plan import ResearchPlan
from src.models.solution import Solution

from src.agents.deep_researcher import DeepResearcherAgent
from src.agents.requirement_decomposer import RequirementDecomposerAgent
from src.agents.suggestor import SuggestorAgent
from src.agents.proposer import ProposerAgent
from src.agents.aggregator import AggregatorAgent
from src.agents.plan_synthesizer import PlanSynthesizerAgent

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
        # Single instance agents
        self.deep_researcher = DeepResearcherAgent()
        self.decomposer = RequirementDecomposerAgent()
        self.aggregator = AggregatorAgent()
        self.synthesizer = PlanSynthesizerAgent()

        # Multi-instance agents
        self.suggestors = [
            SuggestorAgent(i) for i in range(3)
        ]
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
            aggregated = await self._phase_aggregation(all_solutions)
            progress.update(task, completed=True)

            # Phase 7: Plan Synthesis
            task = progress.add_task("Phase 7: Synthesizing research plan...", total=None)
            plan = await self._phase_synthesis(hypothesis, aggregated)
            progress.update(task, completed=True)

        return plan

    async def _phase_deep_research(self, hypothesis_text: str) -> Hypothesis:
        """Phase 1: Deep research on the hypothesis."""
        # TODO: Implement
        return await self.deep_researcher.execute(hypothesis_text)

    async def _phase_clarification(self, hypothesis: Hypothesis) -> Hypothesis:
        """Phase 2: Get user clarifications."""
        # TODO: Implement user interaction for clarifications
        # For hackathon, might skip or use defaults
        return hypothesis

    async def _phase_decomposition(self, hypothesis: Hypothesis) -> RequirementTree:
        """Phase 3: Decompose into requirement tree."""
        # TODO: Implement
        return await self.decomposer.execute(hypothesis)

    async def _phase_context_search(
        self, req_tree: RequirementTree
    ) -> tuple[list[Solution], list[Requirement]]:
        """
        Phase 4: Search for existing solutions in RAG.

        Returns:
            (existing_solutions, requirements_needing_solutions)
        """
        # TODO: Implement RAG search for existing solutions
        # Query the literature store for each atomic requirement
        # Return split of found vs not found
        atomic_reqs = []  # req_tree.get_atomic_requirements()
        return [], atomic_reqs

    async def _phase_solving(self, requirements: list[Requirement]) -> list[Solution]:
        """
        Phase 5: Generate solutions for requirements.

        For each requirement, run N proposers in parallel (each uses ToT).
        """
        # TODO: Implement solving loop
        return []

    async def _phase_aggregation(self, solutions: list[Solution]):
        """Phase 6: Aggregate all solutions."""
        # TODO: Implement
        return await self.aggregator.execute(solutions)

    async def _phase_synthesis(self, hypothesis: Hypothesis, aggregated) -> ResearchPlan:
        """Phase 7: Synthesize final research plan."""
        # TODO: Implement
        return await self.synthesizer.execute(hypothesis, aggregated)
