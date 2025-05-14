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

# --- Session state persistence ---
if "edges" not in st.session_state:
    st.session_state.edges = None
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
        "If cycles are detected:",
        ["Show error", "Automatically remove cycles"],
        index=0
    )
    st.markdown("---")
    st.subheader("🚀 Neo4j Export")
    graph_target = st.radio(
        "Push which graph to Neo4j?",
        ["Uploaded DAG", "Optimized DAG"],
        index=1
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

# --- Input modes ---
if mode == "Upload CSV or Excel":
    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel file with edge list (source → target)",
        type=["csv", "xlsx"]
    )
    if uploaded_file:
        # Load dataframe
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())

        # Optional report_name filter
        if "report_name" in df.columns:
            selected_report = st.selectbox(
                "Filter by report_name", df["report_name"].unique()
            )
            df = df[df["report_name"] == selected_report]

        # Classes filter placed in main UI
        if "classes" in df.columns:
            class_filter = st.multiselect(
                "Filter by 'classes' column", df["classes"].unique(),
                default=df["classes"].unique().tolist()
            )
            df = df[df["classes"].isin(class_filter)]

        # Select source/target columns
        cols = df.columns.tolist()
        source_col = st.selectbox("Select Source Column", cols)
        target_col = st.selectbox("Select Target Column", cols)

        if st.button("Build DAG"):
            new_edges = list(zip(df[source_col], df[target_col]))
            G = nx.DiGraph()
            G.add_edges_from(new_edges)
            st.info(
                f"Uploaded DAG has {nx.number_weakly_connected_components(G)} weakly connected component(s)."
            )
            # cycle handling
            if not nx.is_directed_acyclic_graph(G):
                if handle_cycles == "Show error":
                    st.error(
                        "The uploaded graph contains cycles and cannot be optimized as a DAG."
                    )
                    cycles = list(nx.simple_cycles(G))
                    if cycles:
                        st.warning("Detected cycles:")
                        for cycle in cycles:
                            st.text(" → ".join(map(str, cycle)) + f" → {cycle[0]}")
                    st.stop()
                else:
                    # remove one back-edge per cycle
                    for cycle in list(nx.simple_cycles(G)):
                        G.remove_edge(cycle[-1], cycle[0])
                    new_edges = list(G.edges())
            # initialize optimizer
            try:
                st.session_state.optimizer = DAGOptimizer(new_edges)
                st.session_state.edges = new_edges
                st.session_state.did_optimize = False
                st.success("✅ DAG built successfully.")
            except Exception as e:
                st.error(f"Error initializing DAG: {e}")

elif mode == "Paste edge list":
    txt = st.text_area("One `A,B` per line")
    if txt:
        try:
            new_edges = [tuple(line.split(",")) for line in txt.splitlines() if line.strip()]
            st.session_state.optimizer = DAGOptimizer(new_edges)
            st.session_state.edges = new_edges
            st.session_state.did_optimize = False
            st.success("✅ DAG parsed successfully.")
        except Exception as e:
            st.error(f"Could not parse edges: {e}")

else:  # Random DAG
    n = st.number_input("Number of nodes", min_value=2, value=6)
    p = st.slider("Edge probability", 0.0, 1.0, 0.3)
    if st.button("Generate Random DAG"):
        nodes = list(map(str, range(n)))
        for i in range(n):
            for j in range(i + 1, n):
                if random.random() < p:
                    new_edges.append((nodes[i], nodes[j]))
        st.session_state.optimizer = DAGOptimizer(new_edges)
        st.session_state.edges = new_edges
        st.session_state.did_optimize = False
        st.success("✅ Random DAG generated.")

# --- Guard: must have edges ---
if st.session_state.edges is None:
    st.info("Specify or generate a DAG to get started.")
    st.stop()

opt = st.session_state.optimizer

# --- Optimization trigger from sidebar ---
if optimize:
    if opt:
        if do_tr:    opt.transitive_reduction()
        if do_merge: opt.merge_equivalent_nodes()
        st.session_state.did_optimize = True
        st.success("✅ Optimization complete!")
    else:
        st.warning("Load a valid DAG before optimizing.")

# --- Neo4j push ---
if push:
    if st.session_state.did_optimize or graph_target == "Uploaded DAG":
        graph_to_push = (
            opt.graph if graph_target == "Optimized DAG" else opt.original_graph
        )
        try:
            driver = GraphDatabase.driver(uri, auth=(usr, pwd))
            def create_graph(tx):
                for n in graph_to_push.nodes():
                    tx.run("MERGE (n:Node {name: $name})", name=n)
                for u, v in graph_to_push.edges():
                    # Create relationships using safe parameter names
                    tx.run(
                        "MATCH (a:Node {name:$from_node}) MATCH (b:Node {name:$to_node})"
                        " MERGE (a)-[:DEPENDS_ON]->(b)",
                        from_node=u,
                        to_node=v
                    )
            with driver.session() as session:
                session.write_transaction(create_graph)
            driver.close()
            st.success("✅ Pushed to Neo4j")
        except Exception as e:
            st.error(f"Neo4j error: {e}")
    else:
        st.warning("Optimize first, or choose 'Uploaded DAG' for Neo4j.")

# --- Post-optimization display ---
if st.session_state.did_optimize:
    om = opt.evaluate_graph_metrics(opt.original_graph)
    nm = opt.evaluate_graph_metrics(opt.graph)
    metrics_df = pd.DataFrame({
        "Metric": list(om.keys()),
        "Original": list(om.values()),
        "Optimized": list(nm.values())
    })
    st.subheader("📊 Metrics Comparison")
    st.dataframe(metrics_df)

    st.subheader("🖼️ Graph Visualization")
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    diffs = {k:(om[k], nm[k]) for k in om if om[k] != nm[k]}
    diff_text = "\n".join(f"{k}: {a} → {b}" for k,(a,b) in diffs.items()) or "No changes"
    for G, ax, title in [(opt.original_graph, axes[0], "Original"),
                         (opt.graph, axes[1], "Optimized")]:
        try:
            pos = graphviz_layout(G, prog="dot")
        except:
            pos = nx.spring_layout(G, seed=1)
        nx.draw(G, pos, with_labels=True, ax=ax,
                node_color="lightblue" if title=="Original" else "lightgreen")
        ax.set_title(title)
    fig.suptitle("Changed Metrics:\n" + diff_text, fontsize=10)
    st.pyplot(fig)

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
