import os
import re
import ast
import json
from pathlib import Path
import networkx as nx

try:
    from tree_sitter import Language, Parser

    TREE_SITTER_AVAILABLE = True
except Exception:
    TREE_SITTER_AVAILABLE = False


def _extract_python_symbols_and_imports(src: str):
    """Return (symbols, imports, calls) from Python source."""
    symbols = []
    imports = []
    calls = []
    try:
        tree = ast.parse(src)
    except Exception:
        return symbols, imports, calls

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            symbols.append(("function", node.name, node.lineno))
        elif isinstance(node, ast.ClassDef):
            symbols.append(("class", node.name, node.lineno))
        elif isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.append(func.id)
            elif isinstance(func, ast.Attribute):
                # attr like module.func or obj.method
                calls.append(func.attr)

    return symbols, imports, calls


_GENERIC_IMPORT_PATTERNS = [
    r"^\s*using\s+([A-Za-z0-9_.]+);",  # C#
    r"^\s*Imports\s+([A-Za-z0-9_.]+)",  # VB
    r"^\s*import\s+.*from\s+[\'\"]([^\'\"]+)[\'\"]",  # JS/TS
    r"require\([\'\"]([^\'\"]+)[\'\"]\)",  # CommonJS
]


def _extract_generic_imports(src: str):
    mods = set()
    for pat in _GENERIC_IMPORT_PATTERNS:
        for m in re.findall(pat, src, flags=re.MULTILINE):
            mods.add(m.split("/")[0].split(".")[0])
    return list(mods)


def build_repo_graph(
    repo_path: str, extensions=None, symbol_level=False, resolve_to_files=True
):
    """Build a directed graph of files and optionally symbols.

    - `symbol_level` when True attempts to add function/class nodes (Python only currently).
    - `resolve_to_files` when True maps imports to project files when possible.
    """
    if extensions is None:
        extensions = {".py", ".cs", ".vb", ".js", ".ts"}

    repo = Path(repo_path)
    G = nx.DiGraph()
    file_index = {}  # stem -> list of relative paths

    # Collect files
    for root, _, files in os.walk(repo):
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in extensions:
                rel = str(p.relative_to(repo))
                G.add_node(rel, type="file", language=p.suffix.lstrip("."))
                file_index.setdefault(p.stem, []).append(rel)

    # Analyze each file
    for node in list(G.nodes):
        abs_path = repo / node
        try:
            src = abs_path.read_text(errors="ignore")
        except Exception:
            continue

        if node.endswith(".py"):
            symbols, imports, calls = _extract_python_symbols_and_imports(src)
            if symbol_level:
                for kind, name, lineno in symbols:
                    sym_node = f"{node}::{name}"
                    G.add_node(sym_node, type=kind, file=node, lineno=lineno)
                    G.add_edge(node, sym_node, type="contains")
                # naive call edges: connect symbol -> target by name if exists
                for kind, name, lineno in symbols:
                    src_sym = f"{node}::{name}"
                    for called in calls:
                        # if a symbol of called exists in the graph, link to it
                        for target_stem, paths in file_index.items():
                            if called == target_stem:
                                for p in paths:
                                    G.add_edge(src_sym, p, type="calls")
            else:
                # file-level import edges
                for imp in imports:
                    if resolve_to_files and imp in file_index:
                        for t in file_index[imp]:
                            G.add_edge(node, t, type="import")
                    else:
                        G.add_node(imp, type="module")
                        G.add_edge(node, imp, type="import")
        else:
            imports = _extract_generic_imports(src)
            for imp in imports:
                if resolve_to_files and imp in file_index:
                    for t in file_index[imp]:
                        G.add_edge(node, t, type="import")
                else:
                    G.add_node(imp, type="module")
                    G.add_edge(node, imp, type="import")

    return G


def save_graph(g: nx.Graph, out_dir: str = "reports", name: str = "dep_graph"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    graphml = out / f"{name}.graphml"
    nx.write_graphml(g, graphml)
    # interactive HTML via pyvis
    try:
        from pyvis.network import Network

        net = Network(height="900px", width="100%", directed=True)
        for n, d in g.nodes(data=True):
            title = json.dumps(d)
            label = n if len(n) < 80 else n.split("/")[-1]
            net.add_node(n, label=label, title=title)
        for u, v, d in g.edges(data=True):
            net.add_edge(u, v, title=json.dumps(d))
        html = out / f"{name}.html"
        net.show(str(html))
    except Exception:
        html = None

    return {"graphml": str(graphml), "html": str(html) if html else None}


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--repo", default=".", help="repo path")
    p.add_argument("--out", default="reports", help="output directory")
    p.add_argument(
        "--symbols", action="store_true", help="include symbol-level nodes (Python)"
    )
    args = p.parse_args()
    g = build_repo_graph(args.repo, symbol_level=args.symbols)
    outs = save_graph(g, out_dir=args.out)
    print("Saved:", outs)
