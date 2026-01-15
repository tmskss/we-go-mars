"""
Majority voting utilities for multi-judge decisions.

Owner: [ASSIGN TEAMMATE]
"""

from typing import TypeVar, Callable, Any
from collections import Counter

T = TypeVar("T")


def majority_vote(votes: list[bool]) -> bool:
    """
    Determine the majority vote from a list of boolean votes.

    Args:
        votes: List of boolean votes

    Returns:
        True if majority voted True, False otherwise
    """
    if not votes:
        return False
    return sum(votes) > len(votes) / 2


def majority_vote_with_scores(
    judgments: list[tuple[bool, float]],
) -> tuple[bool, float]:
    """
    Determine majority vote with average score.

    Args:
        judgments: List of (vote, score) tuples

    Returns:
        (majority_vote, average_score)
    """
    if not judgments:
        return False, 0.0

    votes = [j[0] for j in judgments]
    scores = [j[1] for j in judgments]

    return majority_vote(votes), sum(scores) / len(scores)


async def run_parallel_judges(
    judges: list[Any],
    input_data: Any,
    extract_vote: Callable[[Any], bool],
) -> tuple[bool, list[Any]]:
    """
    Run multiple judges in parallel and aggregate votes.

    Args:
        judges: List of judge agent instances
        input_data: Input to pass to each judge
        extract_vote: Function to extract boolean vote from judge output

    Returns:
        (majority_vote_result, list_of_all_outputs)
    """
    # TODO: Implement parallel execution with asyncio.gather
    # 1. Run all judges in parallel
    # 2. Collect all outputs
    # 3. Extract votes and compute majority
    # 4. Return result and all outputs for feedback

    raise NotImplementedError("Implement parallel judge execution")


def select_best_suggestion(suggestions: list[Any], score_fn: Callable[[Any], float]) -> Any:
    """
    Select the best suggestion from multiple suggestors.

    Args:
        suggestions: List of suggestions from different suggestors
        score_fn: Function to score each suggestion

    Returns:
        The highest-scoring suggestion
    """
    if not suggestions:
        return None
    return max(suggestions, key=score_fn)
