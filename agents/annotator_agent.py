import os, json, time, requests
from rich.console import Console
from config import OPENROUTER_API_KEY

console = Console()
MODEL = "nousresearch/hermes-3-llama-3.1-405b:free"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_RETRIES = 3
RETRY_DELAY = 8


def summarize_file(file_path: str):
    """
    Generate one-line summary for a VB.NET/C# file with retries and fallback.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        snippet = "\n".join(content.splitlines()[:200])[:6000]
        prompt = (
            f"Summarize briefly in one clear English line what this VB.NET file does. "
            f"Keep it under 20 words, no code.\n\n```vbnet\n{snippet}\n```"
        )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        body = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a VB.NET software migration assistant.",
                },
                {"role": "user", "content": prompt},
            ],
        }

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = requests.post(BASE_URL, headers=headers, json=body, timeout=45)
                data = resp.json()

                if "choices" in data and data["choices"]:
                    summary = data["choices"][0]["message"]["content"].strip()
                    if len(summary) > 2:
                        return summary

                if "error" in data:
                    msg = data["error"].get("message", "Unknown error")
                    if "limit" in msg.lower() or "rate" in msg.lower():
                        console.print(
                            f"[yellow]Rate-limited. Retry {attempt}/{MAX_RETRIES} in {RETRY_DELAY}s...[/yellow]"
                        )
                        time.sleep(RETRY_DELAY * attempt)
                        continue
                    return f"⚠ API Error: {msg}"

            except requests.exceptions.RequestException as e:
                console.print(f"[red]Network issue ({e}), retrying...[/red]")
                time.sleep(RETRY_DELAY * attempt)

        return "⚠ No summary generated (timeout or rate limit)."

    except Exception as e:
        return f"⚠ Exception while summarizing: {e}"


def annotate_repository(repo_path, extensions=[".vb", ".cs"]):
    """
    Summarize each relevant file (cached). Writes to reports/annotations.json.
    """
    console.print(
        "[bold cyan]🧩 Annotator Agent: Generating file summaries...[/bold cyan]"
    )

    os.makedirs("reports", exist_ok=True)
    save_path = os.path.join("reports", "annotations.json")

    # ✅ Load existing summaries (cache)
    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            annotations = json.load(f)
    else:
        annotations = {}

    for root, _, files in os.walk(repo_path):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            abs_path = os.path.join(root, file)
            if ext in extensions and abs_path not in annotations:
                summary = summarize_file(abs_path)
                annotations[abs_path] = summary
                console.print(f"[green]✔ {file}[/green]: {summary}")

                # Save incrementally
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(annotations, f, indent=2)

    console.print(f"[bold green]✅ File annotations saved to {save_path}[/bold green]")
    return annotations
