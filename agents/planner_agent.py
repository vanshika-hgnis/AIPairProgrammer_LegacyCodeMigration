# agents/planner_agent.py
import json
import requests
from rich.console import Console
from dotenv import load_dotenv
import os

console = Console()
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"



def generate_migration_plan(language_info, target_language):
    console.print("[bold cyan]🧩 Planner Agent: Drafting migration plan...[/bold cyan]")
    src_lang = language_info.get("primary", "Unknown")

    prompt = f"""
    You are a senior software architect.
    The current codebase is written in {src_lang}.
    Generate a detailed, step-by-step migration plan to move it to {target_language}.
    
    Include:
    - Required tools and setup
    - Framework/library equivalents
    - Common pitfalls
    - Migration order (config → logic → UI → tests)
    - Validation and optimization steps
    
    Output format: **Markdown** with clear section headers.
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
                "content": "You are an expert in enterprise-level software migration and modernization.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    try:
        resp = requests.post(BASE_URL, headers=headers, json=body, timeout=90)
        data = resp.json()

        # Defensive response handling
        if "choices" in data and len(data["choices"]) > 0:
            plan_text = data["choices"][0]["message"]["content"].strip()
        elif "error" in data:
            plan_text = f"⚠ API Error: {data['error'].get('message', 'unknown error')}"
        else:
            plan_text = f"⚠ Unexpected response:\n{json.dumps(data, indent=2)}"

    except Exception as e:
        plan_text = f"⚠ Exception during migration plan generation:\n{e}"

    # Always save output
    os.makedirs("reports", exist_ok=True)
    with open("reports/migration_plan.md", "w", encoding="utf-8") as f:
        f.write(plan_text)

    console.print("[green]✅ Migration plan saved to reports/migration_plan.md[/green]")
    return plan_text
