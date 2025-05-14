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
        metrics["num_nodes"] = G.number_of_nodes()
        metrics["num_edges"] = G.number_of_edges()
        metrics["num_leaf_nodes"] = sum(1 for n in G if G.out_degree(n)==0)
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
        comps = nx.number_weakly_connected_components(G)
        metrics["cyclomatic_complexity"] = G.number_of_edges() - G.number_of_nodes() + 2*comps
        degs = [d for _,d in G.degree()]
        freq = Counter(degs)
        metrics["degree_distribution"] = dict(freq)
        total = sum(freq.values())
        metrics["degree_entropy"] = -sum((f/total)*math.log2(f/total) for f in freq.values()) if total>0 else 0
        metrics["density"] = nx.density(G)
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
