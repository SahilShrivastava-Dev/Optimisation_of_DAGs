import os
import json
import math
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from datetime import datetime
from neo4j import GraphDatabase
from networkx.drawing.nx_agraph import graphviz_layout

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
        signature_map = defaultdict(list)
        for node in self.graph.nodes:
            parents = frozenset(self.graph.predecessors(node))
            children = frozenset(self.graph.successors(node))
            signature = (parents, children)
            signature_map[signature].append(node)

        mapping = {}
        merged_graph = nx.DiGraph()
        for nodes in signature_map.values():
            merged_node = nodes[0] if len(nodes) == 1 else "+".join(sorted(map(str, nodes)))
            for node in nodes:
                mapping[node] = merged_node

        for u, v in self.graph.edges():
            nu, nv = mapping[u], mapping[v]
            if nu != nv:
                merged_graph.add_edge(nu, nv)

        self.graph = merged_graph

    def evaluate_graph_metrics(self, G):
        metrics = {}
        metrics["num_nodes"] = G.number_of_nodes()
        metrics["num_edges"] = G.number_of_edges()
        metrics["num_leaf_nodes"] = sum(1 for n in G.nodes if G.out_degree(n) == 0)

        try:
            metrics["longest_path_length"] = nx.dag_longest_path_length(G)
        except:
            metrics["longest_path_length"] = "N/A"

        try:
            lengths = dict(nx.all_pairs_shortest_path_length(G))
            shortest = min(l for targets in lengths.values() for l in targets.values() if l > 0)
            metrics["shortest_path_length"] = shortest
        except:
            metrics["shortest_path_length"] = "N/A"

        metrics["depth"] = metrics["longest_path_length"] if isinstance(metrics["longest_path_length"], int) else "N/A"
        levels = Counter(len(nx.ancestors(G, n)) for n in G.nodes)
        metrics["width"] = max(levels.values()) if levels else 0

        comps = nx.number_weakly_connected_components(G)
        metrics["cyclomatic_complexity"] = G.number_of_edges() - G.number_of_nodes() + 2 * comps

        degs = [d for _, d in G.degree()]
        freq = Counter(degs)
        metrics["degree_distribution"] = dict(freq)
        total = sum(freq.values())
        metrics["degree_entropy"] = -sum((f / total) * math.log2(f / total) for f in freq.values()) if total > 0 else 0
        metrics["density"] = nx.density(G)

        return metrics

    def evaluate_metrics(self):
        print("=== Original Graph Metrics ===")
        for k, v in self.evaluate_graph_metrics(self.original_graph).items():
            print(f"{k}: {v}")
        print("\n=== Optimized Graph Metrics ===")
        for k, v in self.evaluate_graph_metrics(self.graph).items():
            print(f"{k}: {v}")

    def metadata(self):
        om = self.evaluate_graph_metrics(self.original_graph)
        nm = self.evaluate_graph_metrics(self.graph)
        return {
            "timestamp": datetime.now().isoformat(),
            "original_edges": list(self.original_graph.edges()),
            "optimized_edges": list(self.graph.edges()),
            "original_metrics": om,
            "optimized_metrics": nm,
            "changed_metrics": {
                k: {"original": om[k], "optimized": nm[k]} for k in om if om[k] != nm[k]
            }
        }

    def visualize(self, show=True, save_path=None):
        fig, axes = plt.subplots(1, 2, figsize=(16, 10))
        orig_metrics = self.evaluate_graph_metrics(self.original_graph)
        opt_metrics = self.evaluate_graph_metrics(self.graph)
        changed_metrics = {
            k: (orig_metrics[k], opt_metrics[k])
            for k in orig_metrics if orig_metrics[k] != opt_metrics[k]
        }

        try:
            pos1 = graphviz_layout(self.original_graph, prog='dot')
        except:
            pos1 = nx.spring_layout(self.original_graph, seed=42)
        try:
            pos2 = graphviz_layout(self.graph, prog='dot')
        except:
            pos2 = nx.spring_layout(self.graph, seed=42)

        nx.draw(self.original_graph, pos1, with_labels=True, node_color='lightblue', edge_color='gray', ax=axes[0])
        axes[0].set_title("Original DAG (Unoptimized)")

        nx.draw(self.graph, pos2, with_labels=True, node_color='lightgreen', edge_color='black', ax=axes[1])
        axes[1].set_title("Optimized DAG (Reduced + Merged)")

        diff_text = "\n".join(f"{k}: {v[0]} → {v[1]}" for k, v in changed_metrics.items()) or "No differences in metrics."
        fig.text(0.5, 0.92, "Changed Metrics:", fontsize=12, ha='center', fontweight='bold')
        fig.text(0.5, 0.89, diff_text, fontsize=10, ha='center', va='top')

        plt.tight_layout(rect=[0, 0, 1, 0.88])
        if save_path:
            plt.savefig(save_path)
            plt.close()
        elif show:
            plt.show()

    def save_metadata(self, base_folder="graph_metadata"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_folder = os.path.join(base_folder, f"dag_{timestamp}")
        os.makedirs(run_folder, exist_ok=True)

        metadata = self.metadata()
        with open(os.path.join(run_folder, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=4)

        self.visualize(save_path=os.path.join(run_folder, "visualization.png"))
        print(f"✅ Saved metadata and visualization to {run_folder}")

    def push_to_neo4j(self, uri="bolt://localhost:7687", user="neo4j", password="your_password"):
        driver = GraphDatabase.driver(uri, auth=(user, password))

        def create_graph(tx):
            for node in self.graph.nodes():
                tx.run("MERGE (n:Node {name: $name})", name=node)

            for u, v in self.graph.edges():
                tx.run("""
                    MATCH (a:Node {name: $from_node})
                    MATCH (b:Node {name: $to_node})
                    MERGE (a)-[:DEPENDS_ON]->(b)
                """, from_node=u, to_node=v)

        with driver.session() as session:
            session.write_transaction(create_graph)

        driver.close()
        print("✅ Optimized graph pushed to Neo4j.")

