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
from src.agents.proposer import ProposerAgent, ProposerInput, ProposerOutput
from src.agents.aggregator import AggregatorAgent, AggregatorInput, AggregatorOutput
from src.agents.plan_synthesizer import PlanSynthesizerAgent, PlanSynthesizerInput
from src.agents.retriever import (
    RetrieverAgent,
    RetrieverAgentInput,
    RetrieverAgentOutput,
)
from src.agents.similarity_checker import (
    SimilarityCheckerAgent,
    SimilarityCheckerInput,
    SimilarityCheckerOutput,
)

__all__ = [
    "BaseAgent",
    "AgentExecutor",
    "DeepResearcherAgent",
    "RequirementDecomposerAgent",
    "ProposerAgent",
    "ProposerInput",
    "ProposerOutput",
    "AggregatorAgent",
    "AggregatorInput",
    "AggregatorOutput",
    "PlanSynthesizerAgent",
    "PlanSynthesizerInput",
    "RetrieverAgent",
    "RetrieverAgentInput",
    "RetrieverAgentOutput",
    "SimilarityCheckerAgent",
    "SimilarityCheckerInput",
    "SimilarityCheckerOutput",
]
