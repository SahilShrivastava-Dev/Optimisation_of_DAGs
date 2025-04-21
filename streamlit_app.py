# app.py

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

# --- Persisted state setup ---
if "edges" not in st.session_state:
    st.session_state.edges = None
if "optimizer" not in st.session_state:
    st.session_state.optimizer = None
if "did_optimize" not in st.session_state:
    st.session_state.did_optimize = False

# --- Sidebar (always visible) ---
with st.sidebar:
    st.header("🔧 Optimization Options")
    do_tr    = st.checkbox("Transitive Reduction", value=True)
    do_merge = st.checkbox("Merge Equivalent Nodes", value=True)
    optimize = st.button("Optimize")
    st.markdown("---")
    st.subheader("🚀 Neo4j Export")
    uri  = st.text_input("Bolt URI",      value="bolt://localhost:7687")
    usr  = st.text_input("Username",      value="neo4j")
    pwd  = st.text_input("Password",      type="password")
    push = st.button("Push to Neo4j")

# --- DAGOptimizer class ---
class DAGOptimizer:
    def __init__(self, edges):
        self.original_graph = nx.DiGraph()
        self.original_graph.add_edges_from(edges)
        if not nx.is_directed_acyclic_graph(self.original_graph):
            raise ValueError("The input graph must be a DAG.")
        self.graph = self.original_graph.copy()

    def transitive_reduction(self):
        self.graph = nx.transitive_reduction(self.graph)

    def merge_equivalent_nodes(self):
        sig = defaultdict(list)
        for n in self.graph.nodes:
            parents  = frozenset(self.graph.predecessors(n))
            children = frozenset(self.graph.successors(n))
            sig[(parents, children)].append(n)

        mapping = {}
        merged  = nx.DiGraph()
        for group in sig.values():
            merged_node = group[0] if len(group)==1 else "+".join(sorted(map(str, group)))
            for n in group:
                mapping[n] = merged_node

        for u, v in self.graph.edges():
            nu, nv = mapping[u], mapping[v]
            if nu != nv:
                merged.add_edge(nu, nv)
        self.graph = merged

    def evaluate_graph_metrics(self, G):
        m = {}
        m["num_nodes"]  = G.number_of_nodes()
        m["num_edges"]  = G.number_of_edges()
        m["num_leaf_nodes"] = sum(1 for n in G.nodes if G.out_degree(n)==0)
        m["longest_path_length"] = (
            nx.dag_longest_path_length(G)
            if nx.is_directed_acyclic_graph(G) else "N/A"
        )
        try:
            lengths = dict(nx.all_pairs_shortest_path_length(G))
            sp = min(
                l for targets in lengths.values() for l in targets.values() if l>0
            )
            m["shortest_path_length"] = sp
        except:
            m["shortest_path_length"] = "N/A"

        m["depth"] = m["longest_path_length"]
        levels = Counter(len(nx.ancestors(G, n)) for n in G.nodes)
        m["width"] = max(levels.values()) if levels else 0

        comps = nx.number_weakly_connected_components(G)
        m["cyclomatic_complexity"] = G.number_of_edges() - G.number_of_nodes() + 2*comps

        degs = [d for _, d in G.degree()]
        freq = Counter(degs)
        m["degree_distribution"] = dict(freq)
        total = sum(freq.values())
        m["degree_entropy"] = (
            -sum((f/total)*math.log2(f/total) for f in freq.values())
            if total>0 else 0
        )
        m["density"] = nx.density(G)
        return m

    def metadata(self):
        om = self.evaluate_graph_metrics(self.original_graph)
        nm = self.evaluate_graph_metrics(self.graph)
        return {
            "timestamp":        datetime.now().isoformat(),
            "original_edges":   list(self.original_graph.edges()),
            "optimized_edges":  list(self.graph.edges()),
            "original_metrics": om,
            "optimized_metrics":nm,
            "changed_metrics": {
                k: {"original": om[k], "optimized": nm[k]}
                for k in om if om[k] != nm[k]
            }
        }

    def push_to_neo4j(self, uri, user, password):
        drv = GraphDatabase.driver(uri, auth=(user, password))
        def _tx(tx):
            for n in self.graph.nodes():
                tx.run("MERGE (x:Node {name:$n})", n=n)
            for u, v in self.graph.edges():
                tx.run(
                    "MATCH (a:Node {name:$u}), (b:Node {name:$v}) "
                    "MERGE (a)-[:DEPENDS_ON]->(b)",
                    u=u, v=v
                )
        with drv.session() as ses:
            ses.write_transaction(_tx)
        drv.close()

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

# 2) Persist & (re)initialize validator
if new_edges:
    if st.session_state.edges != new_edges:
        st.session_state.edges = new_edges
        try:
            st.session_state.optimizer = DAGOptimizer(new_edges)
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

# 4) Handle Neo4j push
if push:
    if st.session_state.did_optimize:
        try:
            opt.push_to_neo4j(uri, usr, pwd)
            st.success("✅ Pushed to Neo4j")
        except Exception as e:
            st.error(f"Neo4j error: {e}")
    else:
        st.warning("Optimize first, then push.")

# 5) Only show metrics & viz after Optimize
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

    # Visualization
    st.subheader("🖼️ Graph Visualization")
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    diffs = {k: (om[k], nm[k]) for k in om if om[k] != nm[k]}
    diff_text = "\n".join(f"{k}: {a} → {b}" for k,(a,b) in diffs.items()) or "No changes"
    for G, ax, title in [
        (opt.original_graph, axes[0], "Original"),
        (opt.graph,          axes[1], "Optimized")
    ]:
        try:
            pos = graphviz_layout(G, prog="dot")
        except:
            pos = nx.spring_layout(G, seed=1)
        nx.draw(G, pos, with_labels=True, ax=ax,
                node_color=("lightblue" if title=="Original" else "lightgreen"))
        ax.set_title(title)
    fig.suptitle("Changed Metrics:\n" + diff_text, fontsize=10)
    st.pyplot(fig)

    # Downloads
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
