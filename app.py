# streamlit_app.py
import pandas as pd
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

# DAG optimizer
from src.dag_optimiser.dag_class import DAGOptimizer

# --- Helper: aggregate_edge_classes ---
def aggregate_edge_classes(df, source_col, target_col, class_col=None):
    """
    Collapse DataFrame rows into unique edges and collect classes per edge.
    Returns:
      edges: list of (u, v) tuples
      edge_attrs: dict mapping (u, v) -> sorted list of classes
    """
    access_map = defaultdict(set)
    for _, row in df.iterrows():
        u = row[source_col]
        v = row[target_col]
        if class_col and class_col in df.columns:
            c = row[class_col]
            access_map[(u, v)].add(c)
        else:
            access_map[(u, v)]  # ensure key exists
    edges = list(access_map.keys())
    edge_attrs = {e: sorted(access_map[e]) for e in access_map}
    return edges, edge_attrs

# --- Session state persistence ---
if "edges" not in st.session_state:
    st.session_state.edges = None
if "edge_attrs" not in st.session_state:
    st.session_state.edge_attrs = {}
if "optimizer" not in st.session_state:
    st.session_state.optimizer = None
if "did_optimize" not in st.session_state:
    st.session_state.did_optimize = False

# --- Sidebar ---
with st.sidebar:
    st.header("🔧 Optimization Options")
    do_tr = st.checkbox("Transitive Reduction", value=True)
    do_merge = st.checkbox("Merge Equivalent Nodes", value=True)
    optimize = st.button("Optimize")
    handle_cycles = st.selectbox(
        "If cycles are detected:", ["Show error", "Automatically remove cycles"], index=0
    )
    st.markdown("---")
    st.subheader("🚀 Neo4j Export")
    graph_target = st.radio(
        "Push which graph to Neo4j?", ["Uploaded DAG", "Optimized DAG"], index=1
    )
    uri = st.text_input("Bolt/Neo4j+s URI", value="bolt://localhost:7687")
    usr = st.text_input("Username", value="neo4j")
    pwd = st.text_input("Password", type="password")
    push = st.button("Push to Neo4j")

# --- Main UI ---
st.title("🗺️ DAG Optimizer")
mode = st.radio(
    "How would you like to provide your DAG?",
    ("Upload CSV or Excel", "Paste edge list", "Random DAG")
)
new_edges = []
edge_attrs = {}

# --- Input modes ---
if mode == "Upload CSV or Excel":
    uploaded_file = st.file_uploader(
        "Upload CSV/Excel with columns: source, target, classes(optional)",
        type=["csv", "xlsx"]
    )
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.write("Preview:")
        st.dataframe(df.head())

        # optional filters
        if "report_name" in df.columns:
            sel = st.selectbox("Filter by report_name", df['report_name'].unique())
            df = df[df['report_name'] == sel]

        # classes filter
        has_classes = 'classes' in df.columns
        if has_classes:
            cls_choices = df['classes'].unique().tolist()
            sel_classes = st.multiselect("Include access classes", cls_choices, default=cls_choices)
            df = df[df['classes'].isin(sel_classes)]

        # select columns
        cols = df.columns.tolist()
        source_col = st.selectbox("Source Column", cols)
        target_col = st.selectbox("Target Column", cols)

        if st.button("Build DAG"):
            # aggregate edges and classes
            new_edges, edge_attrs = aggregate_edge_classes(df, source_col, target_col, 'classes' if has_classes else None)

            # show components
            G0 = nx.DiGraph(new_edges)
            comps = nx.number_weakly_connected_components(G0)
            st.info(f"Uploaded DAG has {comps} weakly connected component(s).")

            # cycle handling
            if not nx.is_directed_acyclic_graph(G0):
                if handle_cycles == "Show error":
                    st.error("Graph contains cycles—cannot optimize.")
                    for cyc in nx.simple_cycles(G0):
                        st.write(" → ".join(cyc) + " → " + cyc[0])
                    st.stop()
                else:
                    for cyc in nx.simple_cycles(G0):
                        G0.remove_edge(cyc[-1], cyc[0])
                    new_edges = list(G0.edges())

            # init optimizer
            try:
                st.session_state.optimizer = DAGOptimizer(new_edges, edge_attrs)
                st.session_state.edges = new_edges
                st.session_state.edge_attrs = edge_attrs
                st.session_state.did_optimize = False
                st.success("Built DAG successfully.")
            except Exception as e:
                st.error(f"Init error: {e}")

elif mode == "Paste edge list":
    txt = st.text_area("One `source,target,classes` per line")
    if st.button("Build DAG from text"):
        rows = []
        for line in txt.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                rows.append({ 'source': parts[0], 'target': parts[1], 'classes': parts[2] if len(parts)>2 else None })
        df = pd.DataFrame(rows)
        new_edges, edge_attrs = aggregate_edge_classes(df, 'source', 'target', 'classes')
        try:
            st.session_state.optimizer = DAGOptimizer(new_edges, edge_attrs)
            st.session_state.edges = new_edges
            st.session_state.edge_attrs = edge_attrs
            st.session_state.did_optimize = False
            st.success("Built DAG from text.")
        except Exception as e:
            st.error(f"Init error: {e}")

else:
    n = st.number_input("Node count", 2, 100, 6)
    p = st.slider("Edge probability", 0.0, 1.0, 0.3)
    if st.button("Generate Random DAG"):
        access_map = defaultdict(set)
        nodes = [str(i) for i in range(n)]
        for i in range(n):
            for j in range(i+1, n):
                if random.random() < p:
                    access_map[(nodes[i], nodes[j])]  # no classes
        new_edges = list(access_map.keys())
        edge_attrs = {e: [] for e in new_edges}
        st.session_state.optimizer = DAGOptimizer(new_edges, edge_attrs)
        st.session_state.edges = new_edges
        st.session_state.edge_attrs = edge_attrs
        st.session_state.did_optimize = False
        st.success("Generated random DAG.")

# guard
if st.session_state.edges is None:
    st.info("Specify or generate a DAG first.")
    st.stop()
opt = st.session_state.optimizer

# optimize
if optimize:
    if do_tr: opt.transitive_reduction()
    if do_merge: opt.merge_equivalent_nodes()
    st.session_state.did_optimize = True
    st.success("Optimization done.")

# push to Neo4j
if push:
    graph_to_push = opt.original_graph if graph_target == "Uploaded DAG" else opt.graph
    try:
        driver = GraphDatabase.driver(uri, auth=(usr, pwd))
        def create_graph(tx):
            for n in graph_to_push.nodes():
                tx.run("MERGE (n:Node {name:$name})", name=n)
            for u, v in graph_to_push.edges():
                classes = st.session_state.edge_attrs.get((u, v), [])
                tx.run(
                    "MATCH (a:Node {name:$u}) MATCH (b:Node {name:$v})"
                    " MERGE (a)-[r:DEPENDS_ON]->(b) SET r.classes=$classes",
                    u=u, v=v, classes=classes
                )
        with driver.session() as session:
            session.write_transaction(create_graph)
        driver.close()
        st.success("Pushed to Neo4j.")
    except Exception as e:
        st.error(f"Neo4j push error: {e}")

# display
if st.session_state.did_optimize:
    om = opt.evaluate_graph_metrics(opt.original_graph)
    nm = opt.evaluate_graph_metrics(opt.graph)
    metrics_df = pd.DataFrame({
        "Metric": list(om.keys()),
        "Original": list(om.values()),
        "Optimized": list(nm.values())
    })
    st.subheader("Metrics Comparison")
    st.dataframe(metrics_df)

    st.subheader("Graph Visualization")
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    for G, ax, title in [(opt.original_graph, axes[0], "Original"), (opt.graph, axes[1], "Optimized")]:
        try:
            pos = graphviz_layout(G, prog='dot')
        except:
            pos = nx.spring_layout(G, seed=1)
        edge_colors = []
        for u, v in G.edges():
            cls = st.session_state.edge_attrs.get((u, v), [])
            if 'Modify' in cls:
                edge_colors.append('magenta')
            elif 'Call_by' in cls:
                edge_colors.append('gray')
            else:
                edge_colors.append('lightblue')
        nx.draw(
            G, pos, ax=ax, with_labels=True,
            node_color='lightblue' if title == 'Original' else 'lightgreen',
            edge_color=edge_colors
        )
        ax.set_title(title)
    st.pyplot(fig)

    meta = opt.metadata()
    st.download_button(
        "Download metadata (JSON)",
        data=json.dumps(meta, indent=2),
        file_name=f"meta_{datetime.now().strftime('%Y%m%d%H%M%S')}.json",
        mime="application/json"
    )
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    st.download_button(
        "Download visualization (PNG)",
        data=buf,
        file_name="graph.png",
        mime="image/png"
    )
