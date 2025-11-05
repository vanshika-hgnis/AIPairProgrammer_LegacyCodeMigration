import streamlit as st
import io, sys, tempfile, os, json, time
from rich.console import Console
from rich.tree import Tree
from contextlib import redirect_stdout
from repo_handler import clone_or_load_repo
from agents.analyser_agent import analyze_repo_structure
import networkx as nx
from pyvis.network import Network

# ----- CONFIG -----
st.set_page_config(page_title="Terminal AI Pair Programmer", layout="wide")
st.markdown(
    """
    <style>
    body {background-color: #0e1117;}
    .terminal {
        background-color: #000000;
        color: #00ffcc;
        font-family: 'Courier New', monospace;
        padding: 1.2rem;
        border-radius: 10px;
        overflow-y: auto;
        height: 300px;
        font-size: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

console = Console(record=True)

# ----- HEADER -----
st.markdown(
    "<h1 style='color:#00FFFF;'>💻 Terminal-Style AI Pair Programmer</h1>",
    unsafe_allow_html=True,
)
st.markdown("#### 🧠 Full pipeline: Clone → Analyze → Visualize")

# ----- INPUT -----
repo_url = st.text_input("🔗 Enter GitHub repo URL or local folder path")
start_btn = st.button("🚀 Run Analyzer")

terminal_output = st.empty()
terminal_text = ""


def print_term(line):
    global terminal_text
    terminal_text += line + "\n"
    terminal_output.markdown(
        f"<div class='terminal'><pre>{terminal_text}</pre></div>",
        unsafe_allow_html=True,
    )


# ----- PIPELINE -----
if start_btn and repo_url:
    print_term(f"🤖 Starting analysis for: {repo_url}")
    with st.spinner("Cloning or loading repository..."):
        repo_path = clone_or_load_repo(repo_url, console)
    print_term(f"✅ Repo ready at: {repo_path}")

    print_term("🔍 Running Analyzer Agent...")
    buf = io.StringIO()
    with redirect_stdout(buf):
        summary = analyze_repo_structure(repo_path)
    printed_output = buf.getvalue()
    print_term(printed_output)

    # ----- VISUAL OUTPUTS -----
    st.subheader("📦 Project Summary")
    st.json(summary)

    # Tree representation
    st.subheader("🌲 Folder Tree (text-based)")
    tree_text = console.export_text(clear=False)
    st.code(tree_text, language="text")

    # Dependency graph
    st.subheader("🧩 Dependency Graph (Imports Relationships)")
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
        net.save_graph("reports/graph.html")
        st.components.v1.html(open("reports/graph.html").read(), height=650)
    else:
        st.info("No dependencies found.")

    print_term("✅ Analysis complete. Reports and graphs saved to /reports.")
