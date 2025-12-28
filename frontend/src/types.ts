export interface Edge {
  source: string
  target: string
  classes?: string[]
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

