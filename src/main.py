"""
Main entry point for the We Go Mars CLI application.

This module provides the command-line interface for running the research
plan generator.

Usage:
    python -m src.main "Your research hypothesis here"
    python -m src.main "Your hypothesis" --model gpt-5
    python -m src.main "Your hypothesis" --papers ./data/papers/

Owner: [ASSIGN TEAMMATE]
"""

import typer
from rich.console import Console
from rich.panel import Panel

from src.config import settings

app = typer.Typer(
    name="we-go-mars",
    help="AI-first science platform for hypothesis-driven research planning",
)
console = Console()


@app.command()
def run(
    hypothesis: str = typer.Argument(..., help="The research hypothesis to analyze"),
    model: str = typer.Option(None, "--model", "-m", help="LLM model to use"),
    papers: str = typer.Option(None, "--papers", "-p", help="Path to papers directory for RAG"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """
    Generate a research plan from a hypothesis.

    This command runs the full agentic workflow:
    1. Deep research on the hypothesis
    2. Generate clarifying questions
    3. Break down into requirements
    4. Solve atomic requirements
    5. Generate final research plan
    """
    # TODO: Implement the main workflow orchestration
    # 1. Initialize the workflow orchestrator
    # 2. Run deep research agent
    # 3. Handle user clarifications (if any)
    # 4. Run requirement decomposition
    # 5. Run solver phase
    # 6. Aggregate and synthesize plan
    # 7. Output the final research plan

    if model:
        settings.llm_model = model

    console.print(Panel(f"[bold blue]Research Hypothesis:[/bold blue]\n{hypothesis}"))
    console.print(f"\n[yellow]Using model: {settings.llm_model}[/yellow]")

    if papers:
        console.print(f"[yellow]Papers directory: {papers}[/yellow]")

    # TODO: Replace with actual workflow execution
    console.print("\n[red]TODO: Implement workflow orchestration[/red]")
    console.print("See src/orchestration/workflow.py")


@app.command()
def ingest(
    path: str = typer.Argument(..., help="Path to paper or directory"),
) -> None:
    """Ingest papers into the RAG knowledge base."""
    # TODO: Implement paper ingestion
    console.print(f"[red]TODO: Implement paper ingestion for {path}[/red]")


if __name__ == "__main__":
    app()
