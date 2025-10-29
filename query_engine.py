# file: query_engine.py

import os
import json
from typing import List
import requests
import chromadb
from chromadb.utils import embedding_functions

# CONFIG
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CHAT_MODEL = "minimax/minimax-m1"  # or "minimax/minimax-01" depending on your choice
API_URL = "https://openrouter.ai/api/v1/chat/completions"
VECTOR_STORE_DIR = "./vectordb"
EMBEDDING_MODEL = "openai/text-embedding-3-small"  # or your embedding model

# initialise vector store
client = chromadb.Client(
    chromadb.config.Settings(
        persistent_directory=VECTOR_STORE_DIR, anonymized_telemetry=False
    )
)
collection = client.get_collection(
    "codebase_chunks",
    embedding_function=embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"), model_name=EMBEDDING_MODEL
    ),
)


def retrieve_relevant_chunks(question: str, top_k: int = 5) -> List[dict]:
    # embed question
    # (Chroma wrapper handles embed internally when passing embeddings_fn)
    results = collection.query(
        query_embeddings=None, query_texts=[question], n_results=top_k
    )
    chunks = []
    for idx, doc_id in enumerate(results["ids"][0]):
        metadata = results["metadatas"][0][idx]
        text = results["documents"][0][idx]
        chunks.append({"metadata": metadata, "text": text})
    return chunks


def call_openrouter_chat(user_prompt: str, context_chunks: List[dict]) -> str:
    # build system + user messages
    system_msg = {
        "role": "system",
        "content": "You are an expert VB.NET/C# migration assistant. Use the context and provide a clear, detailed answer.",
    }
    # build user message: include user prompt + the context
    context_text = "\n\n".join(
        [
            f"FILE {c['metadata']['file'] if 'file' in c['metadata'] else c['metadata']['chunk_id']}\n{c['text']}"
            for c in context_chunks
        ]
    )
    user_msg = {
        "role": "user",
        "content": f"Here is the context from the codebase:\n{context_text}\n\nUser question: {user_prompt}",
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": CHAT_MODEL,
        "messages": [system_msg, user_msg],
        "max_tokens": 1024,
        "temperature": 0.2,
    }
    resp = requests.post(API_URL, headers=headers, json=payload)
    resp.raise_for_status()
    j = resp.json()
    answer = j["choices"][0]["message"]["content"]
    return answer


def interactive_loop():
    print("AI Pair Programmer — ask your question about the codebase")
    while True:
        question = input("Question (or 'exit'): ")
        if question.lower() in ["exit", "quit"]:
            break
        chunks = retrieve_relevant_chunks(question, top_k=5)
        print(f"Retrieved {len(chunks)} context chunks.")
        answer = call_openrouter_chat(question, chunks)
        print("Answer:\n", answer)
        print("------")


if __name__ == "__main__":
    interactive_loop()
