import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from repo_handler import clone_or_load_repo
from vb_parser import extract_vb_methods

from report_generator import save_report
import requests
from config import OPENROUTER_API_KEY, BASE_URL, MODEL


import requests
from config import OPENROUTER_API_KEY, BASE_URL, MODEL


def translate_vb_to_csharp(vb_code: str):
    prompt = f"Convert this VB.NET code to idiomatic C#:\n\n```vbnet\n{vb_code}\n```"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://openrouter.ai",
        "X-Title": "AI Pair Programmer",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert in VB.NET to C# refactoring. Output only valid C# code.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    try:
        r = requests.post(BASE_URL, headers=headers, json=body, timeout=120)
        data = r.json()
        print(data)
        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return f"// Translation error: {data}"
    except Exception as e:
        return f"// Translation failed: {e}"


app = typer.Typer()
console = Console()


@app.command()
def analyze(repo: str):
    console.print(Panel.fit("[bold cyan]🤖 Internal AI Pair Programmer[/bold cyan]"))
    repo_path = clone_or_load_repo(repo, console)

    vb_methods = extract_vb_methods(repo_path, console)
    report = []

    for method in track(vb_methods, description="Translating VB.NET → C#"):
        translation = translate_vb_to_csharp(method["code"])
        report.append({"file": method["file"], "vb": method["code"], "cs": translation})

    save_report(report)
    console.print(Panel.fit("[green]✅ Report generated successfully![/green]"))


if __name__ == "__main__":
    app()
