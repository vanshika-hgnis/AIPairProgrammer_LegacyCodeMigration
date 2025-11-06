import json, time
from rich.console import Console
from config import OPENROUTER_API_KEY
import requests

console = Console()

MODEL = "nousresearch/hermes-3-llama-3.1-405b:free"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_migration_plan(language_info, target_language):
    console.print("[bold cyan]🧩 Planner Agent: Drafting migration plan...[/bold cyan]")
    src_lang = language_info.get("primary", "Unknown")

    prompt = f"""
    You are a senior software architect.
    Given a project written in {src_lang}, generate a detailed, step-by-step plan to migrate it to {target_language}.
    Include:
    - Required environment/tools
    - Framework equivalents
    - Common pitfalls
    - Migration sequence (e.g., config → data → UI)
    - Validation & testing steps
    Format as Markdown.
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/suraj/ai-pair-programmer",
        "X-Title": "Migration Planner",
    }

    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a highly experienced software migration planner.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    resp = requests.post(BASE_URL, headers=headers, json=body, timeout=90)
    plan_text = resp.json()["choices"][0]["message"]["content"].strip()

    with open("reports/migration_plan.md", "w", encoding="utf-8") as f:
        f.write(plan_text)

    console.print("[green]✅ Migration plan saved to reports/migration_plan.md[/green]")
    return plan_text
