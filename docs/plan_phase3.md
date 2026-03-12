Good ideas — both are doable. High-level plan + minimal scaffolds you can drop into the repo.

Main options

Index & embed repo for RAG chat: chunk files, embed each chunk, store embedding + metadata (repo-relative path, start/end line, language, code snippet hash). Use a vector DB (FAISS/Chroma/Milvus) or a file-backed store. On chat: retrieve top-N chunks, include snippet + file path in prompt, and return LLM output that cites file paths/lines. Keep a short convo memory of citations so follow-ups can refer to prior sources.
Graph the codebase: build nodes for files/classes/functions and edges for imports/calls/inheritance. Use static analysis per-language (ast for Python, tree-sitter or ctags for multi-language), build a NetworkX graph and export to interactive HTML via pyvis or D3.
Minimal indexer (embeddings + FAISS)

Requires: pip install sentence-transformers faiss-cpu numpy tqdm
Stores: faiss index file + metadata JSON with each vector's metadata.
Chat usage pattern (RAG + cite files)

Retrieve top-N via search(), assemble a prompt where each chunk is prefixed with "SOURCE: <path> [chunk i]\n<code...>"
Ask LLM to answer and include a final "SOURCES:" section listing referenced paths.
Keep a short conversation history limited to last N turns and last retrieved sources to allow follow-ups that refer to prior references.
Example prompt assembly (pseudo)

Make the chat “remember location”

Save metadata of retrieved items into the conversation state (session) with timestamps.
When the user says "show me the file you cited" look up the last cited metadata and present the path/snippet.
Graph builder (quick start)

For Python use ast to find imports, class and function defs and call sites. For multi-language, start with imports detection via regex or use tree-sitter.
Notes & next steps

For multi-language precise graphs, use tree-sitter or language-specific analyzers (Roslyn for C#, ctags, srcML).
Consider using Chroma or Milvus if you want a production vector DB with persistence + metadata queries.
Store chunk start/end line numbers so you can open exact file ranges in UI.
Add a simple web UI to chat + click citations to open files in VS Code (vscode://file/<abs_path>:<line>).
If you want, I can:

scaffold the indexer + search + chat agent files into this project,
or implement the Python graph builder and add an HTML visualizer.
Which one first: embeddings-based chat (RAG) or code-dependency graph?
