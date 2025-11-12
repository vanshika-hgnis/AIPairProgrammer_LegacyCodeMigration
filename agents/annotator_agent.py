# agents/annotator_agent.py
import os, json
from rich.console import Console
from ai_provider import LLMProvider
import time
import re
from dotenv import load_dotenv

from pathlib import Path

console = Console()
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)
llm = LLMProvider()


def summarize_file(file_path: str):
    """Locally parse the file to extract only relevant structural info, then send to LLM."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 🔹 Keep only meaningful lines
        clean = "\n".join(
            line for line in content.splitlines()
            if not line.strip().startswith(("'", "//", "#")) and len(line.strip()) > 2
        )

        # 🔹 Extract only key parts (classes, functions, subs)
        tokens = re.findall(r"(?i)(class\s+\w+|sub\s+\w+|function\s+\w+|public\s+\w+|private\s+\w+)", clean)
        snippet = ", ".join(tokens)[:800]

        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[-1].lower().replace(".", "")

        # ✨ Small, structured prompt
        prompt = (
            f"This is a {ext.upper()} source file named '{file_name}'. "
            f"It contains: {snippet or 'no identifiable functions or classes'}. "
            "Describe in one short English line what the file likely does."
        )

        summary = llm.generate(prompt)
        if not isinstance(summary, str) or not summary.strip():
            return f"⚠ No summary generated for {file_name}"
        return summary.strip()

    except Exception as e:
        return f"⚠ Exception while summarizing {file_path}: {e}"


def annotate_repository(repo_path, extensions=[".vb", ".cs", ".py"], force=False):
    """Summarize each relevant file, caching results."""
    import json, time, os
    console.print("[bold cyan]🧩 Annotator Agent: Generating file summaries...[/bold cyan]")

    os.makedirs("reports", exist_ok=True)
    save_path = os.path.join("reports", "annotations.json")

    # Load existing summaries
    annotations = {}
    if os.path.exists(save_path):
        try:
            with open(save_path, "r", encoding="utf-8") as f:
                annotations = json.load(f)
        except Exception:
            annotations = {}

    for root, _, files in os.walk(repo_path):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            abs_path = os.path.join(root, file)

            if ext not in extensions:
                continue

            if abs_path in annotations and not force:
                console.print(f"[yellow]⏩ Cached: {file}[/yellow]")
                continue

            summary = summarize_file(abs_path)
            annotations[abs_path] = summary
            console.print(f"[green]✔ {file}[/green]: {summary}")
            time.sleep(1.5)

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(annotations, f, indent=2)

    console.print(f"[bold green]✅ File annotations saved to {save_path}[/bold green]")
    return annotations
