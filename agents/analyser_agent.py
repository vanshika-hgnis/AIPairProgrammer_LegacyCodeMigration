import os, re, json
from collections import defaultdict
from datetime import datetime
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel

console = Console()

IMPORT_PATTERN = re.compile(r"^\s*Imports\s+([A-Za-z0-9_.]+)", re.MULTILINE)


def extract_imports_from_vb(file_path: str):
    """Extract all 'Imports' dependencies from a VB.NET file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return IMPORT_PATTERN.findall(content)
    except Exception:
        return []


def analyze_repo_structure(repo_path: str):
    """
    Scans the project folder, builds a rich tree visualization,
    extracts dependencies, and saves project_summary.json
    """
    console.print(Panel.fit("[bold cyan]🔍 Project Analyzer Agent[/bold cyan]"))
    summary = {
        "root": os.path.basename(repo_path),
        "analyzed_at": datetime.now().isoformat(),
        "extensions": defaultdict(list),
        "vb_dependencies": defaultdict(list),
    }

    root_tree = Tree(f"[bold cyan]📁 {os.path.basename(repo_path)}[/bold cyan]")

    for root, dirs, files in os.walk(repo_path):
        rel_root = os.path.relpath(root, repo_path)
        branch = root_tree
        if rel_root != ".":
            for part in rel_root.split(os.sep):
                branch = branch.add(f"[yellow]{part}[/yellow]")

        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            abs_path = os.path.join(root, file)
            rel_path = os.path.join(rel_root, file)

            # Record file by extension
            summary["extensions"][ext].append(rel_path)

            color = (
                "green"
                if ext == ".vb"
                else "blue" if ext in [".config", ".csproj"] else "white"
            )
            branch.add(f"[{color}]{file}[/{color}]")

            # Extract dependencies if VB.NET
            if ext == ".vb":
                imports = extract_imports_from_vb(abs_path)
                if imports:
                    summary["vb_dependencies"][rel_path] = imports

    console.print(root_tree)
    console.print(
        Panel.fit(
            f"[green]✅ Project analyzed successfully![/green]\n"
            f"[cyan]VB.NET files:[/cyan] {len(summary['extensions'].get('.vb', []))}\n"
            f"[cyan]Config files:[/cyan] {len(summary['extensions'].get('.config', []))}\n"
            f"[cyan]Dependencies extracted:[/cyan] {len(summary['vb_dependencies'])}"
        )
    )

    os.makedirs("reports", exist_ok=True)
    json_path = os.path.join("reports", "project_summary.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    console.print(
        f"[bold magenta]📦 Project summary saved to:[/bold magenta] {json_path}\n"
    )

    return summary
