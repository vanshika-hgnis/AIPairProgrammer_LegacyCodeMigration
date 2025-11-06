# agents/migration_agent.py
import os
import requests
from datetime import datetime
from config import OPENROUTER_API_KEY

MODEL = "nousresearch/hermes-3-llama-3.1-405b:free"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_migration_report(lang_info, target_lang):
    """
    Generate a detailed migration report via OpenRouter.
    Falls back to an offline heuristic plan if API fails.
    """
    source_lang = lang_info.get("primary", "Unknown")
    secondary = ", ".join(lang_info.get("secondary", []))

    prompt = f"""
You are a senior software architect and migration specialist.
We are migrating a full-stack codebase from {source_lang} (with {secondary}) to {target_lang}.

Generate a detailed, professional migration report in markdown with sections:
1. **Technology Summary**
2. **Compatibility Analysis** — reusable, partial, and rewrite components
3. **Migration Strategy and Phases**
4. **Risk and Mitigation Plan**
5. **Estimated Effort and Timeline**
6. **Post-Migration Testing and Optimization**

Keep it concise (400–600 words) and use markdown formatting.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a senior migration consultant."},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        resp = requests.post(BASE_URL, headers=headers, json=body, timeout=90)
        data = resp.json()

        if "choices" in data and data["choices"]:
            report_text = data["choices"][0]["message"]["content"].strip()
        elif "error" in data:
            report_text = _offline_migration_plan(
                source_lang, target_lang, api_error=data["error"].get("message")
            )
        else:
            report_text = _offline_migration_plan(
                source_lang, target_lang, api_error="unknown"
            )

    except Exception as e:
        report_text = _offline_migration_plan(
            source_lang, target_lang, api_error=str(e)
        )

    # Save always
    os.makedirs("reports", exist_ok=True)
    out_path = f"reports/migration_report_{target_lang.replace('#', 'Sharp')}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_text


# --------------------------------------------------------------------
# 🧠 Local fallback logic (no API required)
# --------------------------------------------------------------------
def _offline_migration_plan(source, target, api_error=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# 🧾 Migration Report: {source} → {target}
_Generated locally on {now}_  
⚠️ API fallback mode activated ({api_error})

---

## 1. Technology Summary
The source system is implemented in **{source}**, possibly leveraging frameworks like ASP.NET Core, WinForms, or VB modules.
The target environment will migrate to **{target}**, adopting a modern architecture with reusable components, strong typing,
and containerized deployment.

---

## 2. Compatibility Analysis
| Component Type | Reuse Potential | Notes |
|----------------|----------------|-------|
| Core Logic / Business Layer | ✅ High | Most classes can be ported or rewritten with minimal logic changes. |
| Controllers / Routing | ⚠ Partial | HTTP pipeline differs — needs re-implementation in the new framework. |
| Config & Secrets | ⚠ Partial | Migrate to `.env`, `appsettings.json`, or environment variables. |
| UI Layer (if any) | ❌ Low | Must be redesigned using native patterns of {target}. |

---

## 3. Migration Strategy and Phases
1. **Assessment & Inventory (1–2 days)** — Identify critical modules and dependencies.
2. **Environment Setup (1 day)** — Prepare containerized build/test setup.
3. **Code Conversion (4–7 days)** — Port models, services, and configs.
4. **Integration Testing (2–3 days)** — Verify behavior consistency.
5. **Deployment (1 day)** — Package via Docker / CI pipelines.

---

## 4. Risk and Mitigation
- ⚠️ _Serialization differences_ — validate JSON/XML schema compatibility.  
- ⚠️ _Dependency Injection mismatch_ — re-architect for {target}’s IoC pattern.  
- ⚠️ _Threading/async behavior_ — verify I/O models.  
**Mitigation:** Incremental refactoring + automated regression tests.

---

## 5. Estimated Effort and Timeline
| Phase | Duration | Tools |
|-------|-----------|-------|
| Analysis | 2 days | Visual Studio, Roslyn Analyzers |
| Conversion | 5–7 days | Transpilers or manual rewrite |
| Testing | 3 days | xUnit, Postman, pytest (if {target}) |
| Deployment | 2 days | Docker Compose / CI-CD |

---

## 6. Post-Migration Optimization
- Enable type hinting and linting for consistency.  
- Containerize and push images to registry.  
- Run profiling tools (PerfView / cProfile) to benchmark parity.  
- Document environment variables and setup commands.

---

✅ **Outcome:** A modernized, maintainable {target}-based system ready for future integration and CI/CD automation.  
"""
    return report
