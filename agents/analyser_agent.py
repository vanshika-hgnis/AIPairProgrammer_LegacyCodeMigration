from io import StringIO
import os, re, json
from collections import defaultdict
from datetime import datetime
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel

console = Console(record=True)

IMPORT_PATTERN = re.compile(r"^\s*Imports\s+([A-Za-z0-9_.]+)", re.MULTILINE)


def extract_imports_from_vb(file_path: str):
    """Extract all 'Imports' dependencies from a VB.NET file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return IMPORT_PATTERN.findall(content)
    except Exception:
        return []


def analyze_repo_structure(repo_path: str, return_tree=False):
    """
    Scans the project folder, builds a rich tree visualization,
    extracts dependencies, and saves project_summary.json.

    If return_tree=True → returns (summary, tree_text)
    """
    # ✅ Create a fresh Rich console that records output each run
    local_console = Console(record=True)
    local_console.print(Panel.fit("[bold cyan]🔍 Project Analyzer Agent[/bold cyan]"))

    summary = {
        "root": os.path.basename(repo_path),
        "analyzed_at": datetime.now().isoformat(),
        "extensions": defaultdict(list),
        "vb_dependencies": defaultdict(list),
    }

    root_tree = Tree(f"[bold cyan]📁 {os.path.basename(repo_path)}[/bold cyan]")

    # ---- Build directory tree ----
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

    # ---- Print & Export Tree ----
    local_console.print(root_tree)
    text_buffer = StringIO()
    plain_console = Console(file=text_buffer, force_terminal=False, color_system=None)
    plain_console.print(root_tree)
    tree_text = text_buffer.getvalue()

    tree_text = re.sub(r"[╭╰╮╯│─┤├└┘┌┐]+", "", tree_text)
    tree_text = re.sub(r"\n\s*\n", "\n", tree_text).strip()
    # ---- Save summary ----
    os.makedirs("reports", exist_ok=True)
    json_path = os.path.join("reports", "project_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    local_console.print(
        f"[bold magenta]📦 Project summary saved to:[/bold magenta] {json_path}\n"
    )

    # ---- Return both summary & tree ----
    if return_tree:
        return summary, tree_text
    return summary
