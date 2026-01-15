"""
Agent definitions using Microsoft Agent Framework.

Each agent is responsible for a specific part of the research workflow.
Agents communicate through the orchestration layer and use majority voting
for quality control.

References:
- https://github.com/microsoft/agent-framework
- https://learn.microsoft.com/en-us/agent-framework/
"""

from src.agents.base import BaseAgent, AgentExecutor, JudgeAgent
from src.agents.deep_researcher import DeepResearcherAgent
from src.agents.requirement_decomposer import RequirementDecomposerAgent
from src.agents.atomicness_judge import AtomicnessJudgeAgent
from src.agents.feasibility_judge import FeasibilityJudgeAgent, FeasibilityJudgeInput
from src.agents.suggestor import SuggestorAgent, SuggestorInput
from src.agents.proposer import ProposerAgent, ProposerInput
from src.agents.solution_judge import SolutionJudgeAgent, SolutionJudgeInput
from src.agents.aggregator import AggregatorAgent
from src.agents.plan_synthesizer import PlanSynthesizerAgent, PlanSynthesizerInput

__all__ = [
    "BaseAgent",
    "AgentExecutor",
    "JudgeAgent",
    "DeepResearcherAgent",
    "RequirementDecomposerAgent",
    "AtomicnessJudgeAgent",
    "FeasibilityJudgeAgent",
    "FeasibilityJudgeInput",
    "SuggestorAgent",
    "SuggestorInput",
    "ProposerAgent",
    "ProposerInput",
    "SolutionJudgeAgent",
    "SolutionJudgeInput",
    "AggregatorAgent",
    "PlanSynthesizerAgent",
    "PlanSynthesizerInput",
]
