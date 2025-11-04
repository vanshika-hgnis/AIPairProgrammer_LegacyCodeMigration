import os, datetime
from rich.console import Console


def save_report(report):
    console = Console()
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"reports/refactor_report_{timestamp}.md"

    with open(file_path, "w", encoding="utf-8") as f:
        for item in report:
            f.write(f"### File: {item['file']}\n\n")
            f.write("**VB.NET:**\n```vbnet\n" + item["vb"] + "\n```\n\n")
            f.write("**C# (Suggested):**\n```csharp\n" + item["cs"] + "\n```\n\n---\n")

    console.print(f"[cyan]Report saved to:[/cyan] {file_path}")
