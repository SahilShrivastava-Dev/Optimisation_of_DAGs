import random
from itertools import combinations

def generate_named_dag_edges(num_nodes=500, edge_prob=0.01, seed=42):
    random.seed(seed)
    nodes = [f"N{i}" for i in range(num_nodes)]
    random.shuffle(nodes)  # topological order

    edges = []
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < edge_prob:
                edges.append((nodes[i], nodes[j]))

    return edges

# Example usage
if __name__ == "__main__":
    edges = generate_named_dag_edges()
    print(f"Generated {len(edges)} edges in DAG with 500 nodes.\n")

    # Print first 10 edges just to preview
    print("Sample edges = [")
    for edge in edges:
        print(f"    {edge},")
    print("    ...\n]")
