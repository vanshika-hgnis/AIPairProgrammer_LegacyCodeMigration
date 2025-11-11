import os
import streamlit as st
import io, sys, json, time
from contextlib import redirect_stdout
from rich.console import Console
from repo_handler import clone_or_load_repo
from agents.router_agent import detect_languages
from agents.analyser_agent import analyze_repo_structure
from agents.planner_agent import generate_migration_plan
import networkx as nx

from textwrap import shorten
from pyvis.network import Network

from agents.annotator_agent import annotate_repository



options = """
{
  "nodes": {
    "shape": "dot",
    "size": 18,
    "font": { "color": "white", "face": "monospace", "size": 14 }
  },
  "edges": {
    "color": { "color": "#888" },
    "width": 1.2,
    "smooth": { "type": "continuous" }
  },
  "interaction": {
    "hover": true,
    "tooltipDelay": 120,
    "zoomView": true,
    "dragView": true
  },
  "physics": { "stabilization": true }
}
"""

# ---- Streamlit Config ----
st.set_page_config(page_title="AI Pair Programmer", layout="wide")
st.markdown(
    """
<style>
body { background-color: #0e1117; }
.terminal {
    background-color: #000;
    color: #00ffcc;
    font-family: 'Courier New', monospace;
    padding: 1rem;
    border-radius: 8px;
    height: 300px;
    overflow-y: auto;
    font-size: 15px;
}
</style>
""",
    unsafe_allow_html=True,
)

console = Console(record=True)
st.markdown(
    "<h1 style='color:#00FFFF;'>💻 Internal AI Pair Programmer (v2.1)</h1>",
    unsafe_allow_html=True,
)

# ---- Terminal-like output box ----
terminal_box = st.empty()
terminal_text = ""


def term_log(msg: str):
    """Simulate terminal output."""
    global terminal_text
    terminal_text += f"{msg}\n"
    terminal_box.markdown(
        f"<div class='terminal'><pre>{terminal_text}</pre></div>",
        unsafe_allow_html=True,
    )


# ---- Session State ----
if "repo_path" not in st.session_state:
    st.session_state.repo_path = None
if "lang_info" not in st.session_state:
    st.session_state.lang_info = None
if "summary" not in st.session_state:
    st.session_state.summary = None

# ---- Input Section ----
repo_url = st.text_input("🔗 Enter GitHub repo URL or local folder path:")
if st.button("🚀 Start Analysis"):
    term_log(f"🤖 Starting pipeline for: {repo_url}")
    with st.spinner("Cloning repository..."):
        st.session_state.repo_path = clone_or_load_repo(repo_url, console)
    term_log(f"✅ Repo ready at: {st.session_state.repo_path}")

    term_log("🧭 Detecting languages...")
    st.session_state.lang_info = detect_languages(st.session_state.repo_path)
    term_log(json.dumps(st.session_state.lang_info, indent=2))

    term_log("🔍 Running Analyzer Agent...")
    summary, tree_text = analyze_repo_structure(
        st.session_state.repo_path, return_tree=True
    )
    st.session_state.summary = summary
    st.session_state.tree_text = tree_text
    term_log("✅ Analysis completed and saved to /reports")
    annotate_repository(st.session_state.repo_path)
    term_log("✅ File summaries saved to reports/annotations.json")

# ---- Results Section ----
if st.session_state.lang_info:
    st.divider()
    st.subheader("🧭 Language Detection Summary")
    lang = st.session_state.lang_info["primary"]
    sec = ", ".join(st.session_state.lang_info["secondary"]) or "None"
    count = json.dumps(st.session_state.lang_info["count"], indent=2)
    col1, col2 = st.columns(2)
    col1.metric("Primary Language", lang)
    col2.metric("Detected Files", sum(st.session_state.lang_info["count"].values()))
    st.code(count, language="json")

# ---- Folder Structure ----
# ---- Folder Structure ----
if st.session_state.summary:
    st.divider()
    st.subheader("🌲 Project Structure Overview (with inline summaries)")

    annotations_path = "reports/annotations.json"
    annotations = {}
    if os.path.exists(annotations_path):
        with open(annotations_path, "r", encoding="utf-8") as f:
            annotations = json.load(f)

    # Normalize paths (handles Windows/relative mismatches)
    normalized_annotations = {
        os.path.normpath(path).lower(): desc.strip()
        for path, desc in annotations.items()
        if isinstance(desc, str)
    }

    tree_lines = []
    root_base = st.session_state.repo_path

    for root, dirs, files in os.walk(root_base):
        level = root.count(os.sep) - root_base.count(os.sep)
        indent = "│   " * level
        folder_name = os.path.basename(root)
        tree_lines.append(f"{indent}📁 {folder_name}/")

        for file in sorted(files):
            abs_path = os.path.join(root, file)
            variants = [
                os.path.normpath(abs_path).lower(),
                os.path.basename(abs_path).lower(),
                os.path.relpath(abs_path, root_base).lower(),
            ]

            desc = ""
            for v in variants:
                if v in normalized_annotations:
                    desc = normalized_annotations[v]
                    break

            short_desc = shorten(desc, width=80, placeholder="…") if desc else ""
            tree_lines.append(f"{indent}    📄 {file} — {short_desc}")

    joined_tree = "\n".join(tree_lines)
    scrollable_html = f"""
    <div style="
    color:#00ffff;
    background-color:#111;
    padding:10px;
    border-radius:8px;
    font-family:monospace;
    height:500px;
    overflow-y:auto;
    white-space:pre;
    line-height:1.4;
    ">
    {joined_tree}
    </div>
    """

    st.markdown(scrollable_html, unsafe_allow_html=True)

    # ✅ Dependency Graph (separate, no summaries)
    st.subheader("🧩 Dependency Graph (Imports Relationships)")
    summary = st.session_state.summary

    if summary.get("vb_dependencies"):
        G = nx.DiGraph()
        for file, deps in summary["vb_dependencies"].items():
            G.add_node(file, color="lightblue", title=file)
            for dep in deps:
                G.add_node(dep, color="orange", title=dep)
                G.add_edge(file, dep)

        net = Network(height="650px", width="100%", bgcolor="#111", font_color="white")
        net.from_nx(G)
        net.repulsion(node_distance=150, spring_length=120)
        net.set_options(options)
        net.save_graph("reports/graph.html")
        st.components.v1.html(open("reports/graph.html").read(), height=650)
    else:
        st.info("No dependencies found.")

if st.session_state.lang_info:
    st.divider()
    st.subheader("⚙️ Migration Target Selection")

    options = ["C#", "Python", "Node.js", "React", "Java", "Modern VB.NET"]
    target_lang = st.selectbox(
        "Select target language/framework:", options, key="target_choice"
    )


if st.button("🧩 Generate Migration Plan"):
    term_log(
        f"🧠 Generating migration plan for {st.session_state.lang_info['primary']} → {target_lang}"
    )
    plan_md = generate_migration_plan(st.session_state.lang_info, target_lang)
    st.session_state.plan_md = plan_md
    st.markdown("### 📜 Migration Plan")
    st.markdown(plan_md, unsafe_allow_html=True)
    term_log("✅ Migration plan ready (saved to reports/migration_plan.md)")
