# Internal AI Pair Programmer at SAP for Legacy Code Migration

Internal AI Pair Programmer — an assistant that understands legacy code and helps refactor or migrate it intelligently.

1. Integrate `codebase_digest` into your Streamlit app, show file tree + summary when user selects local path.
2. Build chunking logic to split VB.NET files into manageable pieces for embedding + conversion.
3. Choose and integrate an embeddings provider (OpenAI, local model, etc), store chunks + vectors in vector DB.
4. Connect the conversion UI: select file/chunk, send to OpenRouter, display converted C# + summary.
5. Add batch conversion capability and download/export of converted files.
6. Add status UI + logging.
7. (Optional) Add search interface using embeddings (semantic search across codebase).
