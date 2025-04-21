# streamlit_app.py

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import json
import math
from collections import defaultdict, Counter
from datetime import datetime
from io import BytesIO
from neo4j import GraphDatabase
from networkx.drawing.nx_agraph import graphviz_layout

# your DAGOptimizer implementation
from src.dag_optimiser.dag_class import DAGOptimizer

# --- Persisted session_state ---
if "edges" not in st.session_state:
    st.session_state.edges = None
if "optimizer" not in st.session_state:
    st.session_state.optimizer = None
if "did_optimize" not in st.session_state:
    st.session_state.did_optimize = False

# --- Sidebar (always visible) ---
with st.sidebar:
    st.header("🔧 Optimization Options")
    do_tr    = st.checkbox("Transitive Reduction", value=True, help="Transitive Reduction simplifies a Directed Acyclic Graph (DAG) by removing redundant edges while preserving the reachability between nodes. It makes the graph cleaner and easier to interpret without changing its core structure.")
    do_merge = st.checkbox("Merge Equivalent Nodes", value=True, help="Use this feature with caution, as node merging can lead to overlapping data or functions. Ensure that it enhances your graph’s functionality without introducing unintended side effects.")
    optimize = st.button("Optimize")
    st.markdown("---")
    st.subheader("🚀 Neo4j Export")
    uri  = st.text_input("Bolt/Neo4j+s URI",      value="bolt://localhost:7687")
    usr  = st.text_input("Username",      value="neo4j")
    pwd  = st.text_input("Password",      type="password")
    push = st.button("Push to Neo4j")

# --- Main UI ---
st.title("🗺️ DAG Optimizer")

# 1) Input mode
mode = st.radio(
    "How would you like to provide your DAG?",
    ("Upload CSV", "Paste edge list", "Random DAG")
)

new_edges = []
if mode == "Upload CSV":
    up = st.file_uploader("CSV with columns: source,target", type="csv")
    if up:
        import pandas as pd
        df = pd.read_csv(up)
        if {"source","target"}.issubset(df.columns):
            new_edges = list(df[["source","target"]].itertuples(index=False, name=None))
        else:
            st.error("CSV needs 'source' and 'target' columns.")
elif mode == "Paste edge list":
    txt = st.text_area("One `A,B` per line")
    if txt:
        try:
            new_edges = [tuple(l.split(",")) for l in txt.splitlines() if l.strip()]
        except:
            st.error("Could not parse your list.")
else:
    n = st.number_input("Number of nodes", min_value=2, value=6)
    p = st.slider("Edge probability", 0.0, 1.0, 0.3)
    if st.button("Generate Random DAG"):
        nodes = list(range(n))
        for i in range(n):
            for j in range(i+1, n):
                if random.random() < p:
                    new_edges.append((str(nodes[i]), str(nodes[j])))

# 2) Persist & (re)initialize optimizer
if new_edges:
    if st.session_state.edges != new_edges:
        st.session_state.edges = new_edges
        try:
            st.session_state.optimizer   = DAGOptimizer(new_edges)
            st.session_state.did_optimize = False
        except ValueError as e:
            st.error(str(e))

if st.session_state.edges is None:
    st.info("Specify or generate a DAG to get started.")
    st.stop()

opt = st.session_state.optimizer

# 3) Handle Optimize click
if optimize:
    if opt:
        if do_tr:    opt.transitive_reduction()
        if do_merge: opt.merge_equivalent_nodes()
        st.session_state.did_optimize = True
        st.success("✅ Optimization complete!")
    else:
        st.warning("Load a valid DAG before optimizing.")

# 4) Handle Push to Neo4j click
if push:
    if st.session_state.did_optimize:
        try:
            opt.push_to_neo4j(uri, usr, pwd)
            st.success("✅ Pushed to Neo4j")
        except Exception as e:
            st.error(f"Neo4j error: {e}")
    else:
        st.warning("Optimize first, then push.")

# 5) Only show metrics & static viz after Optimize
if st.session_state.did_optimize:
    # Metrics comparison
    om = opt.evaluate_graph_metrics(opt.original_graph)
    nm = opt.evaluate_graph_metrics(opt.graph)
    df = {
        "Metric":    list(om.keys()),
        "Original":  list(om.values()),
        "Optimized": list(nm.values()),
    }
    st.subheader("📊 Metrics Comparison")
    st.table(df)

    # Static PNG visualization
    st.subheader("🖼️ Graph Visualization")
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    diffs = {k:(om[k],nm[k]) for k in om if om[k]!=nm[k]}
    diff_text = "\n".join(f"{k}: {a} → {b}" for k,(a,b) in diffs.items()) or "No changes"
    for G, ax, title in [
        (opt.original_graph, axes[0], "Original"),
        (opt.graph,          axes[1], "Optimized")
    ]:
        try:
            pos = graphviz_layout(G, prog="dot")
        except:
            pos = nx.spring_layout(G, seed=1)
        nx.draw(
            G, pos, with_labels=True, ax=ax,
            node_color=("lightblue" if title=="Original" else "lightgreen")
        )
        ax.set_title(title)
    fig.suptitle("Changed Metrics:\n" + diff_text, fontsize=10)
    st.pyplot(fig)

    # Download buttons
    meta = opt.metadata()
    st.download_button(
        "📥 Download metadata (JSON)",
        data=json.dumps(meta, indent=2),
        file_name=f"dag_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    st.download_button(
        "📥 Download visualization (PNG)",
        data=buf,
        file_name="dag_optimization.png",
        mime="image/png"
    )
