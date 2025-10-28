# file: ingest_codebase.py

import os
import hashlib
import json
import uuid

from typing import List
from pathlib import Path

# install: pip install chromadb openai requests tiktoken
import chromadb
from chromadb.utils import embedding_functions

# Replace with your embedding API (could be MiniMax if it supports embeddings, or openai/text-embedding-…)
import openai

# CONFIG
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # put your key in env var
EMBEDDING_MODEL = (
    "openai/text-embedding-3-small"  # example; replace if you use MiniMax embedding
)
VECTOR_STORE_DIR = "./vectordb"
CHUNK_SIZE = 1500  # approximate token/character limit per chunk
CHUNK_OVERLAP = 200

# initialise vector store
client = chromadb.Client(
    chromadb.config.Settings(
        persistent_directory=VECTOR_STORE_DIR, anonymized_telemetry=False
    )
)
collection = client.create_collection(
    "codebase_chunks",
    embedding_function=embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"), model_name=EMBEDDING_MODEL
    ),
)


def chunk_text(
    text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """Split text into overlapping chunks of approx size characters."""
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + size, length)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == length:
            break
        start = end - overlap
    return chunks


def ingest_digest(file_path: str, project_id: str):
    with open(file_path, encoding="utf-8") as f:
        full = f.read()
    chunks = chunk_text(full)
    metadata_list = []
    for idx, chunk in enumerate(chunks):
        doc_id = f"{project_id}-{idx}"
        metadata = {"project_id": project_id, "chunk_id": idx, "text": chunk}
        collection.add(ids=[doc_id], metadatas=[metadata], documents=[chunk])
    print(f"Ingested {len(chunks)} chunks for project {project_id}")


if __name__ == "__main__":
    # example usage
    PROJECT_ID = "vbnet-whatsapp-chatbot"
    DIGEST_PATH = "codebase_digest.txt"
    ingest_digest(DIGEST_PATH, PROJECT_ID)
