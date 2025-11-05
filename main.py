import typer, time, sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from repo_handler import clone_or_load_repo
from vb_parser import extract_vb_methods
from ai_refactor import translate_vb_to_csharp
from report_generator import save_report

from agents.analyser_agent import analyze_repo_structure


console = Console()


def type_effect(text: str, color="cyan"):
    """Claude-style typing effect"""
    for ch in text:
        console.print(ch, style=color, end="")
        sys.stdout.flush()
        time.sleep(0.015)
    console.print()


def main(
    repo: str = typer.Option(
        ..., "--repo", "-r", help="GitHub repo URL or local folder path"
    ),
):
    """AI Pair Programmer – VB.NET → C# Refactor CLI"""
    console.print(
        Panel.fit(
            "[bold bright_cyan]🤖  Internal AI Pair Programmer[/bold bright_cyan]"
        )
    )

    # 🧠 Clone / Load
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        progress.add_task("🧠  Cloning & loading repo...", total=None)
        repo_path = clone_or_load_repo(repo, console)
        progress.stop()

    # 🔍 Parse
    type_effect("🧩  Analyzing project structure...", "magenta")
    analyze_repo_structure(repo_path)
    type_effect("🔍  Scanning VB.NET files...", "yellow")
    vb_methods = extract_vb_methods(repo_path, console)
    type_effect(f"✅  Found {len(vb_methods)} VB.NET methods.", "green")

    # 🤖 Translate
    results = []
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}")
    ) as progress:
        t = progress.add_task("✨  Translating VB.NET → C# ...", total=len(vb_methods))
        for method in vb_methods:
            translation = translate_vb_to_csharp(method["code"])
            results.append(
                {"file": method["file"], "vb": method["code"], "cs": translation}
            )
            progress.advance(t)

    # 📦 Report
    type_effect("📦  Generating colorful report...", "magenta")
    save_report(results)
    console.print(
        Panel.fit(
            "[bold green]✅  Refactor complete! Report saved in /reports[/bold green]"
        )
    )


if __name__ == "__main__":
    typer.run(main)
