# ai_provider.py
import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class LLMProvider:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "gemini")  # gemini | openrouter | huggingface | ollama
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("MODEL", "gemini-2.0-flash-lite")
        self.base_urls = {
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models",
            "openrouter": "https://openrouter.ai/api/v1/chat/completions",
            "huggingface": "https://api-inference.huggingface.co/models",
            "ollama": "http://localhost:11434/api/generate",
        }

    def generate(self, prompt: str):
        provider = self.provider.lower()
        if provider == "gemini":
            return self._call_gemini(prompt)
        elif provider == "openrouter":
            return self._call_openrouter(prompt)
        elif provider == "huggingface":
            return self._call_huggingface(prompt)
        elif provider == "ollama":
            return self._call_ollama(prompt)
        else:
            raise ValueError(f"Unknown AI provider: {provider}")

    def _call_gemini(self, prompt: str):
        base = self.base_urls["gemini"]
        model = self.model or "gemini-2.0-flash-lite"
        key = self.api_key

        if not key:
            return "⚠ Gemini API key missing in environment."
        clean_prompt = (
        prompt.replace("```", "")      # remove code fences
        .replace("\u0000", "")   # remove nulls
        .replace("\r", " ")[:10000]  # trim to ~10 KB
    )

        url = f"{base}/{model}:generateContent?key={key}"
        payload = {
        "contents": [
            {
                "role": "user",  # ✅ required field!
                "parts": [{"text": clean_prompt}]
            }
        ]
    }
        headers = {"Content-Type": "application/json"}

        try:
            for attempt in range(3):
                r = requests.post(url, headers=headers, json=payload, timeout=60)
                if r.status_code == 429:
                    time.sleep(8 * (attempt + 1))
                    continue
                if r.status_code >= 400:
                # detailed message for debugging
                    return f"⚠ Gemini network error: {r.status_code} {r.reason} | {r.text[:200]}"
                r.raise_for_status()

                data = r.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    parts = data["candidates"][0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
                if "error" in data:
                    return f"⚠ Gemini API error: {data['error'].get('message', 'unknown error')}"
                return f"⚠ Unexpected Gemini response: {json.dumps(data)[:300]}"

        except requests.exceptions.RequestException as e:
            return f"⚠ Gemini network error: {e}"

        return "⚠ Gemini returned no content."




    # ---------- OpenRouter ----------
    def _call_openrouter(self, prompt: str):
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        r = requests.post(self.base_urls["openrouter"], headers=headers, json=body)
        data = r.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return f"⚠ OpenRouter error: {data}"

    # ---------- Hugging Face ----------
    def _call_huggingface(self, prompt: str):
        url = f"{self.base_urls['huggingface']}/{self.model}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt}
        r = requests.post(url, headers=headers, json=payload)
        data = r.json()
        try:
            if isinstance(data, list):
                return data[0]["generated_text"]
            return str(data)
        except Exception:
            return f"⚠ Hugging Face error: {data}"

    # ---------- Ollama ----------
    def _call_ollama(self, prompt: str):
        payload = {"model": self.model, "prompt": prompt}
        r = requests.post(self.base_urls["ollama"], json=payload)
        data = r.json()
        return data.get("response", str(data))
