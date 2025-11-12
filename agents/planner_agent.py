# agents/planner_agent.py
import os, json
from rich.console import Console
from ai_provider import LLMProvider

console = Console()
llm = LLMProvider()

def generate_migration_plan(language_info, target_language):
    console.print("[bold cyan]🧩 Planner Agent: Drafting migration plan...[/bold cyan]")
    src_lang = language_info.get("primary", "Unknown")

    prompt = f"""
    You are an AI pair programmer for legacy code migration.
    Analyze the following codebase text and produce modernization advice:
    The current codebase is written in {src_lang}.
    Generate a detailed, step-by-step migration plan to move it to {target_language}. 
    Limit it to 100 - 150 words
    Include:
    - Required tools and setup
    - Framework/library equivalents
    - Point out risky APIs, outdated packages, or VB-specific constructs.
    - Identify the framework and patterns.-
    Output format: Markdown with clear section headers.
    """

    try:
        plan_text = llm.generate(prompt)
    except Exception as e:
        plan_text = f"⚠ Exception during migration plan generation:\n{e}"

    os.makedirs("reports", exist_ok=True)
    with open("reports/migration_plan.md", "w", encoding="utf-8") as f:
        f.write(plan_text)

    console.print("[green]✅ Migration plan saved to reports/migration_plan.md[/green]")
    return plan_text
