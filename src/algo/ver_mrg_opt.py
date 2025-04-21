import os
import json
from datetime import datetime
import networkx as nx
from collections import defaultdict, Counter
import math
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from neo4j import GraphDatabase


class DAGOptimizer:
    def __init__(self, edges):
        self.original_graph = nx.DiGraph()
        self.original_graph.add_edges_from(edges)
        if not nx.is_directed_acyclic_graph(self.original_graph):
            raise ValueError("The input graph must be a DAG.")
        self.graph = self.original_graph.copy()

    def transitive_reduction(self):
        """Applies transitive reduction to simplify the graph."""
        self.graph = nx.transitive_reduction(self.graph)

    def merge_equivalent_nodes(self):
        """Merge nodes that have the same set of parents and children."""
        signature_map = defaultdict(list)
        for node in self.graph.nodes:
            parents = frozenset(self.graph.predecessors(node))
            children = frozenset(self.graph.successors(node))
            signature = (parents, children)
            signature_map[signature].append(node)

        mapping = {}  # maps old nodes to merged node
        merged_graph = nx.DiGraph()

        for nodes in signature_map.values():
            if len(nodes) == 1:
                merged_node = nodes[0]
            else:
                merged_node = "+".join(sorted(map(str, nodes)))
            for node in nodes:
                mapping[node] = merged_node

        for u, v in self.graph.edges():
            new_u = mapping[u]
            new_v = mapping[v]
            if new_u != new_v:  # avoid self-loops caused by merging
                merged_graph.add_edge(new_u, new_v)

        self.graph = merged_graph

    def get_optimized_graph(self):
        return self.graph

    def visualize(self):
        """Visualize original vs optimized DAG using hierarchical layout and show changed metrics."""
        fig, axes = plt.subplots(1, 2, figsize=(16, 10))

        # Evaluate metrics
        orig_metrics = self.evaluate_graph_metrics(self.original_graph)
        opt_metrics = self.evaluate_graph_metrics(self.graph)

        # Detect differences
        changed_metrics = {k: (orig_metrics[k], opt_metrics[k])
                           for k in orig_metrics if orig_metrics[k] != opt_metrics[k]}

        # Try hierarchical layout
        try:
            pos1 = graphviz_layout(self.original_graph, prog='dot')
        except:
            pos1 = nx.spring_layout(self.original_graph, seed=42)

        try:
            pos2 = graphviz_layout(self.graph, prog='dot')
        except:
            pos2 = nx.spring_layout(self.graph, seed=42)

        # Plot original graph
        nx.draw(self.original_graph, pos1, with_labels=True, node_color='lightblue', edge_color='gray', ax=axes[0])
        axes[0].set_title("Original DAG (Unoptimized)")

        # Plot optimized graph
        nx.draw(self.graph, pos2, with_labels=True, node_color='lightgreen', edge_color='black', ax=axes[1])
        axes[1].set_title("Optimized DAG (Reduced + Merged)")

        # Add changed metrics to the figure
        if changed_metrics:
            metrics_text = "\n".join(
                f"{k}: {v[0]} → {v[1]}" for k, v in changed_metrics.items()
            )
        else:
            metrics_text = "No differences in metrics."

        fig.text(0.5, 0.92, "Changed Metrics:", fontsize=8, ha='center', fontweight='bold')
        fig.text(0.5, 0.89, metrics_text, fontsize=8, ha='center', va='top')

        plt.tight_layout(rect=[0, 0, 1, 0.88])  # Leave space for top text
        plt.show()

    def evaluate_graph_metrics(self, G):
        metrics = {}

        metrics["num_nodes"] = G.number_of_nodes()
        metrics["num_edges"] = G.number_of_edges()

        leaf_nodes = [n for n in G.nodes if G.out_degree(n) == 0]
        metrics["num_leaf_nodes"] = len(leaf_nodes)

        if nx.is_directed_acyclic_graph(G):
            try:
                metrics["longest_path_length"] = nx.dag_longest_path_length(G)
            except:
                metrics["longest_path_length"] = "N/A"
        else:
            metrics["longest_path_length"] = "N/A"

        try:
            lengths = dict(nx.all_pairs_shortest_path_length(G))
            shortest = min(
                length
                for target_map in lengths.values()
                for length in target_map.values()
                if length > 0
            )
            metrics["shortest_path_length"] = shortest
        except:
            metrics["shortest_path_length"] = "N/A"

        metrics["depth"] = metrics["longest_path_length"] if isinstance(metrics["longest_path_length"], int) else "N/A"

        levels = Counter()
        for node in G.nodes:
            try:
                level = len(nx.ancestors(G, node))
                levels[level] += 1
            except:
                continue
        metrics["width"] = max(levels.values()) if levels else 0

        num_components = nx.number_weakly_connected_components(G)
        metrics["cyclomatic_complexity"] = G.number_of_edges() - G.number_of_nodes() + 2 * num_components

        degrees = [deg for _, deg in G.degree()]
        degree_freq = Counter(degrees)
        metrics["degree_distribution"] = dict(degree_freq)

        total = sum(degree_freq.values())
        if total > 0:
            entropy = -sum((freq / total) * math.log2(freq / total) for freq in degree_freq.values())
            metrics["degree_entropy"] = entropy
        else:
            metrics["degree_entropy"] = 0

        metrics["density"] = nx.density(G)

        return metrics

    def evaluate_metrics(self):
        print("=== Original Graph Metrics ===")
        orig_metrics = self.evaluate_graph_metrics(self.original_graph)
        for k, v in orig_metrics.items():
            print(f"{k}: {v}")

        print("\n=== Optimized Graph Metrics ===")
        opt_metrics = self.evaluate_graph_metrics(self.graph)
        for k, v in opt_metrics.items():
            print(f"{k}: {v}")

    def save_metadata(self, base_folder="../../graph_metadata"):
        import os
        import json
        from datetime import datetime

        # Create a subfolder with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_folder = os.path.join(base_folder, f"dag_{timestamp}")
        os.makedirs(run_folder, exist_ok=True)

        # Metrics
        orig_metrics = self.evaluate_graph_metrics(self.original_graph)
        opt_metrics = self.evaluate_graph_metrics(self.graph)
        changed_metrics = {
            k: {"original": orig_metrics[k], "optimized": opt_metrics[k]}
            for k in orig_metrics if orig_metrics[k] != opt_metrics[k]
        }

        # Edge lists
        original_edges = list(self.original_graph.edges())
        optimized_edges = list(self.graph.edges())

        metadata = {
            "timestamp": timestamp,
            "original_edges": original_edges,
            "optimized_edges": optimized_edges,
            "original_metrics": orig_metrics,
            "optimized_metrics": opt_metrics,
            "changed_metrics": changed_metrics
        }

        # Save JSON
        json_path = os.path.join(run_folder, "metadata.json")
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=4)
        print(f"✅ Saved metadata: {json_path}")

        # Save PNG of visualization
        self._save_visualization(os.path.join(run_folder, "visualization.png"))
        print(f"✅ Saved visualization: {os.path.join(run_folder, 'visualization.png')}")

    def push_to_neo4j(self, uri="bolt://localhost:7687", user="neo4j", password="your_password"):
        """
        Push the optimized graph to Neo4j database.
        """
        driver = GraphDatabase.driver(uri, auth=(user, password))

        def create_graph(tx, graph):
            for node in graph.nodes():
                tx.run("MERGE (n:Node {name: $name})", name=node)

            for u, v in graph.edges():
                tx.run("""
                                MATCH (a:Node {name: $from})
                                MATCH (b:Node {name: $to})
                                MERGE (a)-[:DEPENDS_ON]->(b)
                            """,from=u, to= v)

                with driver.session() as session:
                    session.write_transaction(create_graph, self.graph)

                driver.close()
                print("✅ Optimized graph pushed to Neo4j.")


    def _save_visualization(self, filepath):
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

        # Top annotation
        if changed_metrics:
            diff_text = "\n".join(f"{k}: {v[0]} → {v[1]}" for k, v in changed_metrics.items())
        else:
            diff_text = "No metric differences."

        fig.text(0.5, 0.92, "Changed Metrics:", fontsize=14, ha='center', fontweight='bold')
        fig.text(0.5, 0.89, diff_text, fontsize=12, ha='center', va='top')

        plt.tight_layout(rect=[0, 0, 1, 0.88])
        plt.savefig(filepath)
        plt.close()


# Example usage
if __name__ == "__main__":
    edges = [
        ('N0', 'N3'),
        ('N0', 'N8'),
        ('N0', 'N5'),
        ('N1', 'N4'),
        ('N2', 'N8'),
        ('N3', 'N11'),
        ('N4', 'N10'),
        ('N4', 'N6'),
        ('N4', 'N9'),
        ('N5', 'N6'),
        ('N6', 'N10'),
        ('N7', 'N13'),
        ('N8', 'N9'),
        ('N8', 'N13'),
        ('N8', 'N10'),
        ('N9', 'N14'),
        ('N9', 'N13'),
        ('N9', 'N12'),
        ('N10', 'N14'),
        ('N10', 'N13'),
        ('N11', 'N12'),
    ]
    optimizer = DAGOptimizer(edges)
    print("Original Graph Edges:", optimizer.graph.edges())

    optimizer.transitive_reduction() # incremental=True
    print("After Transitive Reduction:", optimizer.graph.edges())

    optimizer.merge_equivalent_nodes()
    print("After Merging Equivalent Nodes:", optimizer.graph.edges())

    print("\n--- Graph Metrics Comparison ---")
    optimizer.evaluate_metrics()

    optimizer.save_metadata()

    optimizer.visualize()

    optimizer.push_to_neo4j(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="your_password"
    )
