import random
from collections import defaultdict

def generate_hierarchical_dag(num_nodes=15, num_levels=5, max_edges_per_node=3, seed=42):
    random.seed(seed)

    # Split nodes into levels
    nodes = [f"N{i}" for i in range(num_nodes)]
    levels = [[] for _ in range(num_levels)]
    for i, node in enumerate(nodes):
        level = i * num_levels // num_nodes
        levels[level].append(node)

    edges = []
    for level in range(num_levels - 1):  # last level has no children
        current_level = levels[level]
        next_levels = levels[level + 1:level + 3]  # allow skip-1 levels

        if not next_levels:
            continue
        possible_targets = sum(next_levels, [])

        for src in current_level:
            num_edges = random.randint(1, max_edges_per_node)
            targets = random.sample(possible_targets, min(num_edges, len(possible_targets)))
            for tgt in targets:
                edges.append((src, tgt))

    return edges

# Example usage
if __name__ == "__main__":
    edges = generate_hierarchical_dag()
    print(f"Generated {len(edges)} edges in hierarchical DAG.\n")

    # Show first few edges
    print("edges = [")
    for edge in edges:
        print(f"    {edge},")
    print("]")