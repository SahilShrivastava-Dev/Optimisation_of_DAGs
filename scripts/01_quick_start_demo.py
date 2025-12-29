"""
===============================================================================
DAG OPTIMIZER - QUICK START DEMO
===============================================================================

This script demonstrates the basic usage of the DAGOptimizer library.

Features Demonstrated:
1. Basic transitive reduction
2. ML pipeline optimization
3. PERT/CPM critical path analysis
4. Layer-based parallelism analysis
5. Edge criticality classification
6. Comprehensive metrics comparison
7. Visualization

Author: Sahil Shrivastava
GitHub: https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs
===============================================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dagoptimizer import DAGOptimizer
import networkx as nx
import matplotlib.pyplot as plt
import json
from datetime import datetime


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subsection(title):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---\n")


def example_1_basic_transitive_reduction():
    """
    Example 1: Basic Transitive Reduction
    
    Demonstrates removing redundant edges from a simple DAG.
    A redundant edge is one that can be inferred through other edges.
    
    For example, if A->B and B->C exist, then A->C is redundant.
    """
    print_section("EXAMPLE 1: Basic Transitive Reduction")
    
    # Define a DAG with redundant edges
    edges = [
        ('A', 'B'),
        ('B', 'C'),
        ('A', 'C'),  # Redundant! A->B->C already implies A->C
        ('C', 'D'),
        ('B', 'D'),  # Redundant! B->C->D already implies B->D
    ]
    
    print("Original edges:")
    for u, v in edges:
        print(f"  {u} -> {v}")
    
    # Create optimizer
    optimizer = DAGOptimizer(edges)
    
    print(f"\n📊 Original graph: {optimizer.original_graph.number_of_nodes()} nodes, "
          f"{optimizer.original_graph.number_of_edges()} edges")
    
    # Apply transitive reduction
    optimizer.transitive_reduction()
    
    print(f"\n✅ Optimized graph: {optimizer.graph.number_of_nodes()} nodes, "
          f"{optimizer.graph.number_of_edges()} edges")
    print(f"   Algorithm used: {optimizer.optimization_method}")
    
    print("\nOptimized edges (redundant edges removed):")
    for u, v in optimizer.graph.edges():
        print(f"  {u} -> {v}")
    
    reduction_pct = ((optimizer.original_graph.number_of_edges() - optimizer.graph.number_of_edges()) / 
                     optimizer.original_graph.number_of_edges()) * 100
    
    print(f"\n📉 Edge reduction: {reduction_pct:.1f}%")
    print(f"   Removed {optimizer.original_graph.number_of_edges() - optimizer.graph.number_of_edges()} redundant edges")
    
    return optimizer


def example_2_ml_pipeline():
    """
    Example 2: ML Training Pipeline Optimization
    
    Demonstrates optimization of a typical machine learning training pipeline.
    This is a real-world use case where DAG optimization can reduce
    unnecessary dependencies in ML workflows.
    """
    print_section("EXAMPLE 2: ML Training Pipeline Optimization")
    
    # ML Pipeline with some redundant dependencies
    ml_edges = [
        ('DataIngestion', 'DataValidation'),
        ('DataValidation', 'FeatureEngineering'),
        ('FeatureEngineering', 'DataSplit'),
        ('DataSplit', 'ModelTraining'),
        ('DataSplit', 'ModelValidation'),
        ('ModelTraining', 'ModelEvaluation'),
        ('ModelValidation', 'ModelEvaluation'),
        ('ModelEvaluation', 'ModelRegistry'),
        ('ModelRegistry', 'Deployment'),
        ('Deployment', 'Monitoring'),
        # Redundant edges that slow down the pipeline
        ('DataIngestion', 'FeatureEngineering'),  # Redundant via DataValidation
        ('FeatureEngineering', 'ModelTraining'),  # Redundant via DataSplit
    ]
    
    print("ML Training Pipeline stages:")
    stages = set()
    for u, v in ml_edges:
        stages.add(u)
        stages.add(v)
    for stage in sorted(stages):
        print(f"  - {stage}")
    
    ml_optimizer = DAGOptimizer(ml_edges)
    
    print(f"\n📊 Original pipeline: {ml_optimizer.original_graph.number_of_edges()} dependencies")
    
    ml_optimizer.transitive_reduction()
    
    print(f"✅ Optimized pipeline: {ml_optimizer.graph.number_of_edges()} dependencies")
    
    reduction_pct = ((ml_optimizer.original_graph.number_of_edges() - ml_optimizer.graph.number_of_edges()) / 
                     ml_optimizer.original_graph.number_of_edges()) * 100
    
    print(f"\n📉 Dependency reduction: {reduction_pct:.1f}%")
    print(f"   This means {reduction_pct:.1f}% fewer blocking dependencies!")
    
    return ml_optimizer


def example_3_critical_path_analysis(optimizer):
    """
    Example 3: PERT/CPM Critical Path Analysis
    
    Identifies the critical path (bottleneck) in the workflow and calculates
    slack times for each task. This helps in:
    - Identifying which tasks are on the critical path (no flexibility)
    - Finding tasks with slack (can be delayed without affecting total time)
    - Optimizing resource allocation
    
    Mathematical formulas:
    - EST(v) = max(EST(u) + 1) for all u->v
    - LST(v) = min(LST(w) - 1) for all v->w
    - Slack(v) = LST(v) - EST(v)
    - Critical Path = nodes where Slack(v) = 0
    """
    print_section("EXAMPLE 3: PERT/CPM Critical Path Analysis")
    
    # Compute critical path
    critical_path_data = optimizer.compute_critical_path_with_slack(optimizer.graph)
    
    print("📍 Critical Path Metrics:")
    print(f"\n   Makespan (total execution time): {critical_path_data['makespan']} time units")
    print(f"   Parallel time saved: {critical_path_data['parallel_time_saved']} time units")
    print(f"   Sequential time would be: {optimizer.graph.number_of_nodes()} time units")
    
    speedup = optimizer.graph.number_of_nodes() / critical_path_data['makespan']
    print(f"   Speedup with parallelization: {speedup:.2f}×")
    
    print(f"\n🔴 Critical path (bottleneck - MUST be optimized):")
    print(f"   {' -> '.join(critical_path_data['critical_path'])}")
    
    print("\n📊 Node Slack Times (flexibility for scheduling):")
    print("   (Slack = 0 means CRITICAL - no flexibility to delay)")
    print("   (Slack > 0 means can be delayed without affecting total time)\n")
    
    sorted_slack = sorted(critical_path_data['slack'].items(), key=lambda x: x[1])
    for node, slack in sorted_slack[:8]:  # Show first 8
        status = "🔴 CRITICAL" if slack == 0 else f"🟢 Flexible ({slack} units)"
        print(f"   {node:25} Slack: {slack:2} time units  {status}")
    
    return critical_path_data


def example_4_layer_analysis(optimizer):
    """
    Example 4: Layer-Based Parallelism Analysis
    
    Analyzes the DAG structure in layers to determine:
    - Maximum parallelism (width): How many tasks can run simultaneously
    - Minimum stages (depth): How many sequential stages are needed
    - Width efficiency: How well-balanced the parallelism is
    
    This is crucial for:
    - Distributed systems design
    - Resource allocation planning
    - Identifying parallelization opportunities
    
    Mathematical formula:
    - Layer(v) = max(Layer(u) + 1) for all u->v
    - Width W = max |Layer_i|
    """
    print_section("EXAMPLE 4: Layer-Based Parallelism Analysis")
    
    # Compute layer structure
    layer_data = optimizer.compute_layer_structure(optimizer.graph)
    
    print("🔄 Parallelism Potential:")
    print(f"\n   Max parallel tasks (width): {layer_data['width']} tasks can run simultaneously")
    print(f"   Minimum execution stages (depth): {layer_data['depth']} sequential stages required")
    print(f"   Width efficiency: {layer_data['width_efficiency']:.1%}")
    print(f"   Average layer size: {layer_data['avg_layer_size']:.2f} tasks per stage")
    
    ideal_parallelism = optimizer.graph.number_of_nodes() / layer_data['depth']
    print(f"\n   Ideal parallelism: {ideal_parallelism:.2f} tasks/stage")
    print(f"   Actual max parallelism: {layer_data['width']} tasks/stage")
    
    if layer_data['width'] < ideal_parallelism:
        print(f"   ⚠️  Parallelism bottleneck detected! Some stages have fewer tasks.")
    else:
        print(f"   ✅ Well-balanced parallelism across stages!")
    
    print("\n📋 Layer Structure (execution stages):\n")
    for layer_id, nodes in sorted(layer_data['layers'].items(), key=lambda x: int(x[0])):
        print(f"   Stage {layer_id}: {len(nodes)} tasks")
        for node in nodes[:5]:  # Show first 5 nodes per layer
            print(f"      - {node}")
        if len(nodes) > 5:
            print(f"      ... and {len(nodes) - 5} more tasks")
    
    return layer_data


def example_5_edge_criticality(optimizer):
    """
    Example 5: Edge Criticality Analysis
    
    Classifies edges into:
    - Critical edges: Cannot be removed without breaking reachability
    - Redundant edges: Can be removed (transitive edges)
    
    This helps identify:
    - Which dependencies are essential
    - Which dependencies can be removed to simplify the graph
    - Optimization opportunities
    
    Mathematical principle:
    - An edge (u,v) is critical if removing it breaks reachability from u to v
    - An edge is redundant if there's an alternative path
    """
    print_section("EXAMPLE 5: Edge Criticality Analysis")
    
    # Compute edge criticality
    edge_data = optimizer.compute_edge_criticality(optimizer.graph)
    
    print("🔗 Edge Classification Results:")
    print(f"\n   Critical edges (essential): {len(edge_data['critical_edges'])}")
    print(f"   Redundant edges (can be removed): {len(edge_data['redundant_edges'])}")
    print(f"   Criticality ratio: {edge_data['avg_criticality']:.1%}")
    
    print("\n✅ All edges in optimized graph are CRITICAL")
    print("   (Transitive reduction already removed redundant edges)")
    
    if edge_data['critical_edges']:
        print(f"\n📋 Critical edges (first 10):")
        for i, edge in enumerate(edge_data['critical_edges'][:10]):
            print(f"   {i+1}. {edge[0]} -> {edge[1]}")
    
    return edge_data


def example_6_comprehensive_metrics(optimizer):
    """
    Example 6: Comprehensive Metrics Comparison
    
    Compares 25+ metrics between original and optimized graphs:
    - Basic metrics: nodes, edges, density
    - Path metrics: longest/shortest paths, diameter
    - Complexity metrics: cyclomatic, topological
    - Efficiency metrics: redundancy ratio, compactness, efficiency score
    - Advanced metrics: PERT/CPM, layers, edge criticality
    """
    print_section("EXAMPLE 6: Comprehensive Metrics Comparison")
    
    # Get all metrics
    original_metrics = optimizer.evaluate_graph_metrics(optimizer.original_graph)
    optimized_metrics = optimizer.evaluate_graph_metrics(optimizer.graph)
    
    print("📊 Key Metrics Comparison:\n")
    print(f"{'Metric':<30} {'Original':>12} {'Optimized':>12} {'Change':>12}")
    print("-" * 70)
    
    metrics_to_show = [
        ('num_nodes', 'Number of Nodes'),
        ('num_edges', 'Number of Edges'),
        ('density', 'Graph Density'),
        ('efficiency_score', 'Efficiency Score'),
        ('redundancy_ratio', 'Redundancy Ratio'),
        ('longest_path_length', 'Longest Path'),
        ('avg_path_length', 'Avg Path Length'),
        ('makespan', 'Makespan (PERT)'),
        ('dag_width', 'Max Parallelism'),
        ('dag_depth', 'Min Stages'),
    ]
    
    for key, label in metrics_to_show:
        orig = original_metrics.get(key, 'N/A')
        opt = optimized_metrics.get(key, 'N/A')
        
        if isinstance(orig, (int, float)) and isinstance(opt, (int, float)):
            change = ((opt - orig) / orig * 100) if orig != 0 else 0
            change_str = f"{change:+.1f}%" if change != 0 else "---"
            print(f"{label:<30} {orig:>12.4f} {opt:>12.4f} {change_str:>12}")
        else:
            print(f"{label:<30} {str(orig):>12} {str(opt):>12} {'---':>12}")
    
    print("\n💡 Key Insights:")
    
    # Efficiency improvement
    if optimized_metrics['efficiency_score'] > original_metrics['efficiency_score']:
        improvement = (optimized_metrics['efficiency_score'] - original_metrics['efficiency_score']) * 100
        print(f"   ✅ Efficiency improved by {improvement:.1f} percentage points")
    
    # Redundancy reduction
    if original_metrics['redundancy_ratio'] > optimized_metrics['redundancy_ratio']:
        print(f"   ✅ Redundancy reduced from {original_metrics['redundancy_ratio']:.1%} "
              f"to {optimized_metrics['redundancy_ratio']:.1%}")
    
    # Parallelism
    if optimized_metrics.get('dag_width', 0) > 0:
        print(f"   ✅ Can parallelize up to {optimized_metrics['dag_width']} tasks simultaneously")
    
    return original_metrics, optimized_metrics


def example_7_visualization(optimizer):
    """
    Example 7: Visualization
    
    Creates side-by-side visualization of original and optimized graphs.
    """
    print_section("EXAMPLE 7: Visualization")
    
    print("Creating visualization...")
    
    # Create a simpler graph for better visualization
    viz_edges = [
        ('Start', 'Task1'),
        ('Start', 'Task2'),
        ('Task1', 'Task3'),
        ('Task2', 'Task3'),
        ('Task3', 'Task4'),
        ('Start', 'Task3'),  # Redundant
        ('Task1', 'Task4'),  # Redundant
        ('Task2', 'Task4'),  # Redundant
    ]
    
    viz_optimizer = DAGOptimizer(viz_edges)
    viz_optimizer.transitive_reduction()
    
    # Create visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Original graph
    pos1 = nx.spring_layout(viz_optimizer.original_graph, seed=42)
    nx.draw(viz_optimizer.original_graph, pos1, ax=axes[0], 
            with_labels=True, node_color='lightblue', node_size=2000,
            font_size=10, font_weight='bold', arrows=True, 
            edge_color='gray', arrowsize=20, width=2)
    axes[0].set_title(f'Original DAG\n({viz_optimizer.original_graph.number_of_edges()} edges)', 
                      fontsize=14, fontweight='bold')
    
    # Optimized graph
    pos2 = nx.spring_layout(viz_optimizer.graph, seed=42)
    nx.draw(viz_optimizer.graph, pos2, ax=axes[1], 
            with_labels=True, node_color='lightgreen', node_size=2000,
            font_size=10, font_weight='bold', arrows=True, 
            edge_color='darkgreen', arrowsize=20, width=2)
    axes[1].set_title(f'Optimized DAG\n({viz_optimizer.graph.number_of_edges()} edges)', 
                      fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save figure
    output_path = 'dag_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Visualization saved to: {output_path}")
    
    plt.close()
    
    reduction = viz_optimizer.original_graph.number_of_edges() - viz_optimizer.graph.number_of_edges()
    print(f"\n📉 Removed {reduction} redundant edges from the simple example")


def example_8_export_metadata(optimizer):
    """
    Example 8: Export Metadata
    
    Exports complete optimization metadata including all metrics and graphs.
    """
    print_section("EXAMPLE 8: Export Metadata")
    
    # Get complete metadata
    metadata = optimizer.metadata()
    
    print("📦 Metadata Contents:")
    print(f"\n   Timestamp: {metadata['timestamp']}")
    print(f"   Original edges: {len(metadata['original_edges'])}")
    print(f"   Optimized edges: {len(metadata['optimized_edges'])}")
    print(f"   Changed metrics: {len(metadata['changed_metrics'])}")
    
    # Save to JSON
    output_file = 'optimization_metadata.json'
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    print(f"\n✅ Metadata exported to: {output_file}")
    print(f"   File size: {os.path.getsize(output_file) / 1024:.2f} KB")
    
    return metadata


def main():
    """
    Main function to run all examples.
    """
    print("\n" + "=" * 80)
    print("  DAG OPTIMIZER - QUICK START DEMONSTRATION")
    print("  Comprehensive Guide to DAG Optimization Features")
    print("=" * 80)
    print(f"\nExecution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all examples
    optimizer1 = example_1_basic_transitive_reduction()
    optimizer2 = example_2_ml_pipeline()
    example_3_critical_path_analysis(optimizer2)
    example_4_layer_analysis(optimizer2)
    example_5_edge_criticality(optimizer2)
    example_6_comprehensive_metrics(optimizer2)
    example_7_visualization(optimizer2)
    example_8_export_metadata(optimizer2)
    
    # Final summary
    print_section("SUMMARY")
    print("✅ All examples completed successfully!\n")
    print("What you learned:")
    print("  1. ✅ Basic transitive reduction - Remove redundant edges")
    print("  2. ✅ ML pipeline optimization - Real-world application")
    print("  3. ✅ PERT/CPM analysis - Critical path and scheduling")
    print("  4. ✅ Layer analysis - Parallelism potential")
    print("  5. ✅ Edge criticality - Identify essential edges")
    print("  6. ✅ Comprehensive metrics - 25+ research-grade metrics")
    print("  7. ✅ Visualization - Compare before/after")
    print("  8. ✅ Metadata export - Save complete analysis")
    
    print("\n📚 Next Steps:")
    print("  - Run 02_benchmark_analysis.py to see performance on 995 DAGs")
    print("  - Run 03_metrics_explained.py for detailed metric explanations")
    print("  - Check the research paper in Research Papers/ folder")
    print("  - Try the Streamlit demo: streamlit run app.py")
    
    print("\n" + "=" * 80)
    print(f"Execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

