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
    path: str = typer.Argument("data", help="Path to markdown file or directory (default: data/)"),
    skip_existing: bool = typer.Option(False, "--skip-existing", help="Skip files already in the knowledge base"),
    batch_size: int = typer.Option(10, "--batch-size", help="Files to process before logging progress"),
    dry_run: bool = typer.Option(False, "--dry-run", help="List files without actually ingesting"),
) -> None:
    """
    Ingest markdown files into the RAG knowledge base.

    This command recursively finds all .md files in the specified path and ingests
    them into the Qdrant vector database with hybrid (dense + sparse) embeddings.

    Examples:
        python -m src.main ingest
        python -m src.main ingest data/specs
        python -m src.main ingest --skip-existing --batch-size 5
    """
    from pathlib import Path
    from src.rag.literature_store import LiteratureStore

    path_obj = Path(path)

    # Check if path exists
    if not path_obj.exists():
        console.print(f"[red]Error: Path not found: {path}[/red]")
        raise typer.Exit(1)

    try:
        store = LiteratureStore()

        # Handle single file vs directory
        if path_obj.is_file():
            if not path_obj.suffix == ".md":
                console.print(f"[yellow]Warning: {path} is not a markdown file (.md)[/yellow]")
                raise typer.Exit(1)

            console.print(f"[blue]Ingesting single file: {path}[/blue]\n")

            if dry_run:
                console.print(f"[yellow]DRY RUN: Would ingest {path}[/yellow]")
                return

            document = store.ingest_file(str(path_obj))
            chunks = store._chunk_markdown(document)

            console.print(f"[green]✓ Successfully ingested {len(chunks)} chunks from {path_obj.name}[/green]")

        else:
            # Directory ingestion - find all markdown files
            md_files = list(path_obj.rglob("*.md"))

            if not md_files:
                console.print(f"[yellow]No markdown files found in {path}[/yellow]")
                return

            console.print(f"[blue]Found {len(md_files)} markdown files in {path}[/blue]\n")

            if dry_run:
                console.print("[yellow]DRY RUN: Would ingest the following files:[/yellow]")
                for md_file in sorted(md_files):
                    console.print(f"  - {md_file.relative_to(path_obj.parent)}")
                return

            # Batch ingestion with progress
            stats = {
                "total": len(md_files),
                "success": 0,
                "failed": 0,
                "chunks": 0,
            }

            console.print(f"[blue]Starting ingestion of {len(md_files)} files...[/blue]\n")

            for idx, md_file in enumerate(sorted(md_files), 1):
                try:
                    relative_path = md_file.relative_to(path_obj.parent)
                    console.print(f"[{idx}/{len(md_files)}] Ingesting: {relative_path}")

                    document = store.ingest_file(str(md_file))
                    chunks = store._chunk_markdown(document)
                    num_chunks = len(chunks)

                    stats["success"] += 1
                    stats["chunks"] += num_chunks

                    console.print(f"  [green]✓ {num_chunks} chunks[/green]")

                    # Progress update every batch_size files
                    if idx % batch_size == 0:
                        console.print(f"\n[cyan]--- Progress: {idx}/{len(md_files)} files processed ---[/cyan]\n")

                except Exception as e:
                    stats["failed"] += 1
                    console.print(f"  [red]✗ Failed: {e}[/red]")

            # Final summary
            console.print(f"\n{'='*60}")
            console.print("[bold green]INGESTION COMPLETE[/bold green]")
            console.print(f"{'='*60}")
            console.print(f"Total files:          {stats['total']}")
            console.print(f"[green]Successfully ingested: {stats['success']}[/green]")
            console.print(f"[red]Failed:               {stats['failed']}[/red]")
            console.print(f"Total chunks created: {stats['chunks']}")
            console.print(f"{'='*60}\n")

            if stats["failed"] > 0:
                raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Ingestion interrupted by user[/yellow]")
        raise typer.Exit(130)

    except Exception as e:
        console.print(f"[red]Error during ingestion: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
