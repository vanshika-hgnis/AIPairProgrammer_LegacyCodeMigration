# agents/annotator_agent.py
import os, json
from rich.console import Console
from ai_provider import LLMProvider
import time
from pathlib import Path

console = Console()
llm = LLMProvider()

def summarize_file(file_path: str):
    """Generate one-line summary for a VB.NET/C# file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        snippet = "\n".join(content.splitlines()[:200])[:6000]
        prompt = (
            f"Summarize in one clear English line what this VB.NET or C# file does. "
            f"Keep it under 20 words, no code.\n\n```vbnet\n{snippet}\n```"
        )

        summary = llm.generate(prompt)
        return summary or "⚠ No summary generated."

    except Exception as e:
        return f"⚠ Exception while summarizing: {e}"


def annotate_repository(repo_path, extensions = [".vb", ".cs", ".py"]):
    """Summarize each relevant file (cached). Writes to reports/annotations.json."""
    console.print("[bold cyan]🧩 Annotator Agent: Generating file summaries...[/bold cyan]")

    os.makedirs("reports", exist_ok=True)
    save_path = os.path.join("reports", "annotations.json")

    # Load cache if it exists
    annotations = {}
    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            annotations = json.load(f)

    for root, _, files in os.walk(repo_path):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            abs_path = os.path.join(root, file)
            if ext in extensions and abs_path not in annotations:
                summary = summarize_file(abs_path)
                annotations[abs_path] = summary
                console.print(f"[green]✔ {file}[/green]: {summary}")
                time.sleep(2)

                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(annotations, f, indent=2)

    console.print(f"[bold green]✅ File annotations saved to {save_path}[/bold green]")
    return annotations
