import streamlit as st
import json, time, random
import networkx as nx
from pyvis.network import Network

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Pair Programmer", layout="wide")


# ---------- CLAUDE-STYLE TYPING ----------
def type_effect(text: str, delay=0.015):
    st.markdown("<br>", unsafe_allow_html=True)
    container = st.empty()
    s = ""
    for ch in text:
        s += ch
        container.markdown(
            f"<span style='color:cyan;font-family:monospace;font-size:16px;'>{s}</span>",
            unsafe_allow_html=True,
        )
        time.sleep(delay)


# ---------- HEADER ----------
st.markdown(
    "<h1 style='color:#00FFFF;'>🤖 Internal AI Pair Programmer Dashboard</h1>",
    unsafe_allow_html=True,
)
type_effect("🧠 Initializing Analyzer Agent...", delay=0.02)

# ---------- LOAD PROJECT SUMMARY ----------
try:
    with open("reports/project_summary.json") as f:
        data = json.load(f)
except FileNotFoundError:
    st.error("❌ No project_summary.json found. Please run the analyzer first.")
    st.stop()

# ---------- BASIC STATS ----------
col1, col2, col3 = st.columns(3)
col1.metric("📦 Project", data.get("root", "unknown"))
col2.metric("🕓 Last Analyzed", data.get("analyzed_at", "N/A"))
col3.metric("📄 VB.NET Files", len(data["extensions"].get(".vb", [])))

st.divider()

# ---------- FILE EXTENSIONS SUMMARY ----------
st.subheader("📁 File Type Summary")
for ext, files in data["extensions"].items():
    with st.expander(f"**{ext}**  ({len(files)} files)"):
        for f in files:
            st.markdown(f"- `{f}`")

st.divider()

# ---------- DEPENDENCY GRAPH ----------
st.subheader("🧩 Dependency Graph (Imports Relationships)")

if data.get("vb_dependencies"):
    G = nx.DiGraph()

    # Add nodes + edges
    for file, deps in data["vb_dependencies"].items():
        G.add_node(file, color="lightblue", title=file)
        for dep in deps:
            G.add_node(dep, color="orange", title=dep)
            G.add_edge(file, dep)

    net = Network(height="650px", width="100%", bgcolor="#111", font_color="white")
    net.from_nx(G)
    net.repulsion(node_distance=150, spring_length=120)
    net.save_graph("reports/graph.html")

    st.components.v1.html(open("reports/graph.html").read(), height=670)
else:
    st.info("No VB.NET imports or dependencies found.")

# ---------- CONCLUSION ----------
st.divider()
type_effect(
    "✅ Project analysis complete. Ready for migration planning phase...", delay=0.02
)
