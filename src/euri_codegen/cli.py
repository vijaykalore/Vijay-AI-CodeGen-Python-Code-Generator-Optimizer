from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .config import Settings
from .euri_client import Euri
from .codegen.generator import generate_code_for_topic, explain_code
from .codegen.optimizer import optimize_code
from .catalog_loader import load_catalog, list_topics
from .models import validate_specs, Spec

app = typer.Typer(add_completion=False)
console = Console()


@app.command("doctor")
def doctor() -> None:
    """Check environment and configuration."""
    try:
        settings = Settings.load()
        console.print("[green]EURI_API_KEY found[/green]")
        console.print(f"[cyan]Default model:[/cyan] {settings.model}")
        console.print("[green]Environment looks good![/green]")
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        console.print("Set the key with: $env:EURI_API_KEY = \"<your-key>\"")
        raise typer.Exit(code=1)


@app.command("list-topics")
def cmd_list_topics() -> None:
    data = load_catalog()
    # Validate for early feedback
    _ = validate_specs(data)
    table = Table(title="DSA Topics")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Summary")
    for item in data:
        table.add_row(item["id"], item["title"], item["summary"])
    console.print(table)


@app.command("models")
def cmd_models() -> None:
    """Show commonly available Euri models (static list)."""
    table = Table(title="Euri Models")
    table.add_column("Model")
    table.add_column("Notes")
    table.add_row("gpt-4.1-nano", "Fast and efficient")
    table.add_row("gpt-4.1-mini", "Balanced performance")
    table.add_row("gemini-2.5-flash", "Google Gemini model")
    console.print(table)


@app.command("integrations")
def cmd_integrations() -> None:
    """Show how to enable optional framework integrations."""
    console.rule("Euri AI Integrations")
    console.print("Install extras as needed:")
    console.print("- euriai[autogen]    # AutoGen integration")
    console.print("- euriai[crewai]     # CrewAI integration")
    console.print("- euriai[langchain]  # LangChain integration")
    console.print("- euriai[smolagents] # SmolAgents integration")
    console.print("- euriai[langgraph]  # LangGraph integration")
    console.print("- euriai[llama-index] # LlamaIndex integration")
    console.print("- euriai[all]        # Install all integrations")
    console.print("\nThen import from euriai.<framework> as shown in docs.")


@app.command("generate")
def cmd_generate(
    topic: str = typer.Option(..., help="Topic id from the catalog"),
    out_dir: Path = typer.Option(Path("generated"), help="Output directory"),
    max_tokens: Optional[int] = typer.Option(None, help="Override max tokens"),
) -> None:
    settings = Settings.load()
    euri = Euri(settings)
    specs = load_catalog()
    # Validate catalog first
    valid_specs = {s.id: s for s in validate_specs(specs)}
    spec = valid_specs.get(topic)
    if not spec:
        console.print(f"[red]Topic not found:[/red] {topic}")
        raise typer.Exit(code=1)
    out_dir.mkdir(parents=True, exist_ok=True)
    module_path, test_path = generate_code_for_topic(euri, spec.model_dump(), out_dir, max_tokens=max_tokens)
    console.print(f"[green]Generated:[/green] {module_path}")
    console.print(f"[green]Tests:[/green] {test_path}")


@app.command("generate-all")
def cmd_generate_all(
    out_dir: Path = typer.Option(Path("generated"), help="Output directory"),
    max_tokens: Optional[int] = typer.Option(None, help="Override max tokens"),
) -> None:
    """Generate implementations and tests for all catalog topics."""
    settings = Settings.load()
    euri = Euri(settings)
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = [Spec.model_validate(s) for s in load_catalog()]
    for spec in specs:
        console.print(f"[cyan]Generating[/cyan] {spec.id} ...")
        try:
            module_path, test_path = generate_code_for_topic(
                euri, spec.model_dump(), out_dir, max_tokens=max_tokens
            )
            console.print(f"[green]OK:[/green] {module_path} | {test_path}")
        except Exception as e:
            console.print(f"[red]Failed {spec.id}:[/red] {e}")


@app.command("validate-catalog")
def cmd_validate_catalog() -> None:
    """Validate the DSA catalog JSON against schema rules."""
    try:
        specs = validate_specs(load_catalog())
        console.print(f"[green]Catalog valid:[/green] {len(specs)} spec(s)")
    except Exception as e:
        console.print(f"[red]Catalog validation failed:[/red] {e}")
        raise typer.Exit(code=1)


@app.command("new-spec")
def cmd_new_spec(
    id: str = typer.Option(..., help="New spec id (snake_case)"),
    title: str = typer.Option(..., help="Title"),
    summary: str = typer.Option(..., help="Short summary"),
    signature: str = typer.Option(..., help="Function signature or class decl"),
) -> None:
    """Print a JSON template for a new spec to add to the catalog."""
    spec = Spec(
        id=id,
        title=title,
        summary=summary,
        function_signature=signature,
        inputs=[],
        outputs={"type": "", "desc": ""},
        constraints=[],
        examples=[],
    )
    console.print_json(data=spec.model_dump())


@app.command("optimize")
def cmd_optimize(
    path: Path = typer.Option(..., exists=True, file_okay=True, dir_okay=False),
    level: str = typer.Option("all", help="one|readability|performance|memory|all"),
) -> None:
    settings = Settings.load()
    euri = Euri(settings)
    new_content = optimize_code(euri, path.read_text(encoding="utf-8"), level=level)
    path.write_text(new_content, encoding="utf-8")
    console.print(f"[green]Optimized file saved:[/green] {path}")


@app.command("explain")
def cmd_explain(path: Path = typer.Option(..., exists=True)) -> None:
    settings = Settings.load()
    euri = Euri(settings)
    explanation = explain_code(euri, path.read_text(encoding="utf-8"))
    console.print(explanation)


def main():
    app()


if __name__ == "__main__":
    main()
