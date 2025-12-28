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
    def __init__(self, edges, edge_attrs=None):
        """
        edges: list of (u, v) tuples
        edge_attrs: dict mapping (u, v) to list of classes or other attributes
        """
        self.original_graph = nx.DiGraph()
        self.original_graph.add_edges_from(edges)
        if not nx.is_directed_acyclic_graph(self.original_graph):
            raise ValueError("The input graph must be a DAG.")
        self.graph = self.original_graph.copy()
        # preserve edge attributes
        self.edge_attrs = edge_attrs.copy() if edge_attrs is not None else {e: [] for e in edges}
        # trim attrs to only original edges
        self.edge_attrs = {e: self.edge_attrs.get(e, []) for e in self.original_graph.edges()}

    def transitive_reduction(self):
        # compute reduction
        red = nx.transitive_reduction(self.graph)
        # preserve attrs: keep only surviving edges
        new_attrs = {e: self.edge_attrs.get(e, []) for e in red.edges()}
        self.graph = red
        self.edge_attrs = new_attrs

    def merge_equivalent_nodes(self):
        # find equivalent node sets
        signature_map = defaultdict(list)
        for node in self.graph.nodes:
            parents = frozenset(self.graph.predecessors(node))
            children = frozenset(self.graph.successors(node))
            signature_map[(parents, children)].append(node)
        # map old->merged label
        mapping = {}
        for nodes in signature_map.values():
            merged = nodes[0] if len(nodes)==1 else "+".join(sorted(map(str,nodes)))
            for n in nodes:
                mapping[n] = merged
        # build merged graph and attrs
        merged_graph = nx.DiGraph()
        new_attrs = {}
        for u,v in self.graph.edges():
            nu, nv = mapping[u], mapping[v]
            if nu!=nv:
                merged_graph.add_edge(nu, nv)
                # aggregate classes from all original edges that now collapse to (nu,nv)
                classes = new_attrs.get((nu,nv), set())
                classes.update(self.edge_attrs.get((u,v), []))
                new_attrs[(nu,nv)] = classes
        self.graph = merged_graph
        # convert sets to sorted lists
        self.edge_attrs = {e: sorted(list(cls_set)) for e,cls_set in new_attrs.items()}

    def evaluate_graph_metrics(self, G):
        metrics = {}
        
        # Basic Metrics
        metrics["num_nodes"] = G.number_of_nodes()
        metrics["num_edges"] = G.number_of_edges()
        metrics["num_leaf_nodes"] = sum(1 for n in G if G.out_degree(n)==0)
        
        # Path Metrics
        try:
            metrics["longest_path_length"] = nx.dag_longest_path_length(G)
        except:
            metrics["longest_path_length"] = "N/A"
        try:
            lengths = dict(nx.all_pairs_shortest_path_length(G))
            shortest = min(l for targets in lengths.values() for l in targets.values() if l>0)
            metrics["shortest_path_length"] = shortest
        except:
            metrics["shortest_path_length"] = "N/A"
        
        metrics["depth"] = metrics["longest_path_length"] if isinstance(metrics["longest_path_length"],int) else "N/A"
        levels = Counter(len(nx.ancestors(G,n)) for n in G.nodes())
        metrics["width"] = max(levels.values()) if levels else 0
        
        # Complexity Metrics
        comps = nx.number_weakly_connected_components(G)
        metrics["cyclomatic_complexity"] = G.number_of_edges() - G.number_of_nodes() + 2*comps
        
        # Degree Metrics
        degs = [d for _,d in G.degree()]
        freq = Counter(degs)
        metrics["degree_distribution"] = dict(freq)
        total = sum(freq.values())
        metrics["degree_entropy"] = -sum((f/total)*math.log2(f/total) for f in freq.values()) if total>0 else 0
        metrics["density"] = nx.density(G)
        
        # ========== ADVANCED RESEARCH METRICS ==========
        
        # Average Degree
        metrics["avg_degree"] = sum(degs) / len(degs) if degs else 0
        
        # Max In/Out Degrees (Bottleneck Detection)
        in_degrees = [d for _, d in G.in_degree()]
        out_degrees = [d for _, d in G.out_degree()]
        metrics["max_in_degree"] = max(in_degrees) if in_degrees else 0
        metrics["max_out_degree"] = max(out_degrees) if out_degrees else 0
        
        # Average Path Length (Graph Efficiency)
        try:
            all_paths = dict(nx.all_pairs_shortest_path_length(G))
            path_lengths = [length for source in all_paths.values() 
                          for length in source.values() if length > 0]
            metrics["avg_path_length"] = sum(path_lengths) / len(path_lengths) if path_lengths else 0
        except:
            metrics["avg_path_length"] = 0
        
        # Diameter (Maximum Eccentricity)
        try:
            # For DAGs, we use the longest path length as diameter
            metrics["diameter"] = metrics["longest_path_length"] if isinstance(metrics["longest_path_length"], int) else 0
        except:
            metrics["diameter"] = 0
        
        # Transitivity (Clustering Coefficient for Directed Graphs)
        try:
            metrics["transitivity"] = nx.transitivity(G)
        except:
            metrics["transitivity"] = 0
        
        # Redundancy Ratio (Transitive Edges / Total Edges)
        try:
            transitive_closure = nx.transitive_closure_dag(G)
            transitive_reduction = nx.transitive_reduction(G)
            redundant_edges = transitive_closure.number_of_edges() - transitive_reduction.number_of_edges()
            metrics["redundancy_ratio"] = redundant_edges / G.number_of_edges() if G.number_of_edges() > 0 else 0
        except:
            metrics["redundancy_ratio"] = 0
        
        # Compactness Score (1 - normalized edge count)
        # Lower is better: measures how compact the DAG is
        n = G.number_of_nodes()
        max_possible_edges = n * (n - 1) / 2 if n > 1 else 1
        metrics["compactness_score"] = 1 - (G.number_of_edges() / max_possible_edges) if max_possible_edges > 0 else 1
        
        # Efficiency Score (composite metric)
        # Higher is better: combines low redundancy, low density, high compactness
        efficiency_components = []
        if metrics["redundancy_ratio"] >= 0:
            efficiency_components.append(1 - metrics["redundancy_ratio"])
        if metrics["density"] >= 0:
            efficiency_components.append(1 - metrics["density"])
        if metrics["compactness_score"] >= 0:
            efficiency_components.append(metrics["compactness_score"])
        metrics["efficiency_score"] = sum(efficiency_components) / len(efficiency_components) if efficiency_components else 0
        
        # Bottleneck Nodes (nodes with highest betweenness centrality)
        try:
            betweenness = nx.betweenness_centrality(G)
            sorted_nodes = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
            metrics["bottleneck_nodes"] = [str(node) for node, _ in sorted_nodes[:5]]
        except:
            metrics["bottleneck_nodes"] = []
        
        # Critical Path (longest path in the DAG)
        try:
            critical_path = nx.dag_longest_path(G)
            metrics["critical_path"] = [str(node) for node in critical_path]
        except:
            metrics["critical_path"] = []
        
        # Strongly Connected Components (should be 1 for each node in a DAG)
        try:
            # For DAGs, we count weakly connected components instead
            metrics["strongly_connected_components"] = nx.number_weakly_connected_components(G)
        except:
            metrics["strongly_connected_components"] = 1
        
        # Topological Complexity (normalized sum of topological levels)
        try:
            topo_levels = {}
            for node in nx.topological_sort(G):
                predecessors = list(G.predecessors(node))
                if not predecessors:
                    topo_levels[node] = 0
                else:
                    topo_levels[node] = max(topo_levels[p] for p in predecessors) + 1
            
            max_level = max(topo_levels.values()) if topo_levels else 0
            metrics["topological_complexity"] = max_level
        except:
            metrics["topological_complexity"] = 0
        
        return metrics

    def metadata(self):
        om = self.evaluate_graph_metrics(self.original_graph)
        nm = self.evaluate_graph_metrics(self.graph)
        return {
            "timestamp": datetime.now().isoformat(),
            "original_edges": list(self.original_graph.edges()),
            "optimized_edges": list(self.graph.edges()),
            "edge_attributes": self.edge_attrs,
            "original_metrics": om,
            "optimized_metrics": nm,
            "changed_metrics": {k:{"original":om[k],"optimized":nm[k]} for k in om if om[k]!=nm[k]}
        }

    def visualize(self, show=True, save_path=None):
        fig, axes = plt.subplots(1, 2, figsize=(16,10))
        om = self.evaluate_graph_metrics(self.original_graph)
        nm = self.evaluate_graph_metrics(self.graph)
        diffs = {k:(om[k],nm[k]) for k in om if om[k]!=nm[k]}
        try:
            pos1 = graphviz_layout(self.original_graph,prog='dot')
        except:
            pos1 = nx.spring_layout(self.original_graph,seed=42)
        try:
            pos2 = graphviz_layout(self.graph,prog='dot')
        except:
            pos2 = nx.spring_layout(self.graph,seed=42)
        # draw original
        nx.draw(self.original_graph,pos1,with_labels=True,node_color='lightblue',edge_color='gray',ax=axes[0])
        axes[0].set_title('Original DAG')
        # draw optimized with colored edges
        edge_colors = []
        for u,v in self.graph.edges():
            cls = self.edge_attrs.get((u,v),[])
            if 'Modify' in cls: edge_colors.append('magenta')
            elif 'Call_by' in cls: edge_colors.append('gray')
            else: edge_colors.append('lightblue')
        nx.draw(self.graph,pos2,with_labels=True,node_color='lightgreen',edge_color=edge_colors,ax=axes[1])
        axes[1].set_title('Optimized DAG')
        diff_text = '\n'.join(f"{k}: {v[0]} → {v[1]}" for k,v in diffs.items()) or 'No changes'
        fig.text(0.5,0.92,'Changed Metrics',ha='center',fontweight='bold')
        fig.text(0.5,0.89,diff_text,ha='center')
        plt.tight_layout(rect=[0,0,1,0.88])
        if save_path:
            plt.savefig(save_path)
            plt.close()
        elif show:
            plt.show()

    def push_to_neo4j(self, uri="bolt://localhost:7687", user="neo4j", password="your_password"):
        driver = GraphDatabase.driver(uri, auth=(user,password))
        def create_graph(tx):
            for n in self.graph.nodes():
                tx.run("MERGE (n:Node{name:$name})", name=n)
            for u,v in self.graph.edges():
                cls = self.edge_attrs.get((u,v),[])
                tx.run(
                    "MATCH (a:Node{name:$u}) MATCH (b:Node{name:$v})"
                    " MERGE (a)-[r:DEPENDS_ON]->(b) SET r.classes=$cls",
                    u=u,v=v,cls=cls
                )
        with driver.session() as session:
            session.write_transaction(create_graph)
        driver.close()
        print("Pushed with classes to Neo4j.")
