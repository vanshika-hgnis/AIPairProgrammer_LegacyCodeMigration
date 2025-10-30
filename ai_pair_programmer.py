import os, requests

# ========= CONFIG =========
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # put your key in env var
MODEL = "minimax/minimax-01"  # or minimax/minimax-m1
API_URL = "https://openrouter.ai/api/v1/chat/completions"
CODE_PATH = "codebase_digest.txt"  # your cdiget output
CHUNK_LIMIT = 6000  # characters per chunk to avoid token overflow
TOP_N = 3  # number of chunks with keyword hits to send

# ========= LOAD CODEBASE =========
with open(CODE_PATH, encoding="utf-8") as f:
    code_text = f.read()

# Split the codebase into small chunks
chunks = [code_text[i : i + CHUNK_LIMIT] for i in range(0, len(code_text), CHUNK_LIMIT)]


def get_relevant_chunks(query: str):
    """Naive keyword search for top-N relevant chunks"""
    scored = [(chunk.lower().count(query.lower()), chunk) for chunk in chunks]
    scored.sort(reverse=True, key=lambda x: x[0])
    return [text for _, text in scored[:TOP_N]]


def ask_ai(question: str):
    context_chunks = get_relevant_chunks(question)
    context = "\n\n---\n\n".join(context_chunks)
    prompt = (
        f"You are an expert code migration assistant.\n\n"
        f"User question:\n{question}\n\n"
        f"Relevant project code context:\n{context[:15000]}"
    )  # limit size

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You analyze VB.NET projects and assist with modernization or code comprehension.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    print("🧠 Internal AI Pair Programmer (MiniMax via OpenRouter)")
    while True:
        q = input("\nAsk a question (or 'exit'): ")
        if q.lower() in ("exit", "quit"):
            break
        print("\nThinking...")
        answer = ask_ai(q)
        print("\n--- AI Answer ---\n")
        print(answer)
