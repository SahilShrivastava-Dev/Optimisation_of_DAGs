export interface Edge {
  source: string
  target: string
  classes?: string[]
}

export interface CriticalPathAnalysis {
  critical_path: string[]
  slack: Record<string, number>
  EST: Record<string, number>
  LST: Record<string, number>
  makespan: number
  parallel_time_saved: number
}

export interface LayerAnalysis {
  layers: Record<string, string[]>  // String keys for JSON serialization
  width: number
  depth: number
  width_efficiency: number
  avg_layer_size: number
  node_to_layer: Record<string, number>
}

export interface EdgeCriticality {
  critical_edges: string[][]  // Array of [source, target] pairs
  redundant_edges: string[][]  // Array of [source, target] pairs
  edge_criticality_scores: Record<string, number>  // "source->target": score
  avg_criticality: number
}

export interface GraphMetrics {
  num_nodes: number
  num_edges: number
  num_leaf_nodes: number
  longest_path_length: number | string
  shortest_path_length: number | string
  depth: number | string
  width: number
  cyclomatic_complexity: number
  degree_distribution: Record<string, number>
  degree_entropy: number
  density: number
  // Advanced Research Metrics
  avg_degree: number
  max_in_degree: number
  max_out_degree: number
  avg_path_length: number
  diameter: number
  transitivity: number
  redundancy_ratio: number
  compactness_score: number
  efficiency_score: number
  bottleneck_nodes: string[]
  critical_path: string[]
  strongly_connected_components: number
  topological_complexity: number
  num_edges_in_transitive_closure: number
  num_edges_in_transitive_reduction: number
  // Research Paper-Based Advanced Features
  critical_path_analysis?: CriticalPathAnalysis
  makespan?: number
  parallel_time_saved?: number
  critical_nodes_count?: number
  layer_analysis?: LayerAnalysis
  dag_width?: number
  dag_depth?: number
  width_efficiency?: number
  parallelism_potential?: number
  edge_criticality?: EdgeCriticality
  critical_edges_count?: number
  redundant_edges_count?: number
  edge_criticality_ratio?: number
}

export interface GraphData {
  edges: Edge[]
  metrics: GraphMetrics
  visualization: string
}

export interface OptimizationResult {
  success: boolean
  original: GraphData
  optimized: GraphData
  timestamp: string
  error?: string
  cycles?: string[][]
}

export interface RandomDAGParams {
  num_nodes: number
  edge_probability: number
}

export interface Neo4jConfig {
  uri: string
  username: string
  password: string
  graph_type: 'original' | 'optimized'
}

