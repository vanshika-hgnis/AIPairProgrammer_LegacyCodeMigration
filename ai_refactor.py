# ai_refactor.py
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from repo_handler import clone_or_load_repo
from vb_parser import extract_vb_methods

from report_generator import save_report
import requests
from dotenv import load_dotenv
import os
from ai_provider import LLMProvider
llm = LLMProvider()


def translate_vb_to_csharp(vb_code: str):
    prompt = f"Convert this VB.NET code to idiomatic C#:\n\n```vbnet\n{vb_code}\n```"
    try:
        return llm.generate(prompt)
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
