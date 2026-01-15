"""
Agent definitions using Microsoft Agent Framework.

Each agent is responsible for a specific part of the research workflow.

References:
- https://github.com/microsoft/agent-framework
- https://learn.microsoft.com/en-us/agent-framework/
"""

from src.agents.base import BaseAgent, AgentExecutor
from src.agents.deep_researcher import DeepResearcherAgent
from src.agents.requirement_decomposer import RequirementDecomposerAgent
from src.agents.suggestor import SuggestorAgent, SuggestorInput
from src.agents.proposer import ProposerAgent, ProposerInput
from src.agents.aggregator import AggregatorAgent
from src.agents.plan_synthesizer import PlanSynthesizerAgent, PlanSynthesizerInput

__all__ = [
    "BaseAgent",
    "AgentExecutor",
    "DeepResearcherAgent",
    "RequirementDecomposerAgent",
    "SuggestorAgent",
    "SuggestorInput",
    "ProposerAgent",
    "ProposerInput",
    "AggregatorAgent",
    "PlanSynthesizerAgent",
    "PlanSynthesizerInput",
]
