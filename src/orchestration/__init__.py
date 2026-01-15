"""
Workflow orchestration for the multi-agent system.

This module coordinates agent execution, handles majority voting,
and manages the overall research workflow.
"""

from src.orchestration.workflow import ResearchWorkflow
from src.orchestration.voting import majority_vote
from src.orchestration.tree_of_thoughts import TreeOfThoughts

__all__ = [
    "ResearchWorkflow",
    "majority_vote",
    "TreeOfThoughts",
]
