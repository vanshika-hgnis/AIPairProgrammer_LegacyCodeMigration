import os, re, json
from rich.console import Console
from collections import Counter

console = Console()

LANG_MAP = {
    ".py": "Python",
    ".vb": "VB.NET",
    ".cs": "C#",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".html": "HTML",
    ".json": "JSON",
    ".xml": "XML",
}


def detect_languages(repo_path: str):
    console.print("[bold cyan]🧭 Routing Agent: Detecting languages...[/bold cyan]")
    exts = []
    for root, _, files in os.walk(repo_path):
        for f in files:
            ext = os.path.splitext(f)[-1].lower()
            if ext in LANG_MAP:
                exts.append(LANG_MAP[ext])
    if not exts:
        console.print("[red]No recognized language extensions found.[/red]")
        return None

    count = Counter(exts)
    primary = count.most_common(1)[0][0]
    secondary = [lang for lang, _ in count.items() if lang != primary]

    result = {"primary": primary, "secondary": secondary, "count": dict(count)}
    console.print(f"[green]Detected primary:[/green] {primary}")
    console.print(f"[yellow]Secondary:[/yellow] {', '.join(secondary) or 'None'}")

    os.makedirs("reports", exist_ok=True)
    with open("reports/language_summary.json", "w") as f:
        json.dump(result, f, indent=2)

    return result
