import { motion } from 'framer-motion'
import { TrendingDown, TrendingUp, AlertTriangle, CheckCircle, Activity, Zap, Target, GitBranch, HelpCircle } from 'lucide-react'
import { GraphMetrics } from '../types'
import { useState } from 'react'

interface ResearchInsightsProps {
  originalMetrics: GraphMetrics
  optimizedMetrics: GraphMetrics
}

// Tooltip Component
interface TooltipProps {
  children: React.ReactNode
  content: React.ReactNode
  borderColor?: string
}

function Tooltip({ children, content, borderColor = 'border-blue-500/50' }: TooltipProps) {
  const [show, setShow] = useState(false)
  
  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      {children}
      
      {/* Tooltip Content - positioned above and to the right */}
      {show && (
        <div 
          className={`absolute left-0 bottom-full mb-2 w-[28rem] bg-slate-900 border ${borderColor} rounded-lg p-4 shadow-2xl z-[99999]`}
          style={{ maxWidth: 'calc(100vw - 2rem)' }}
        >
          <div className={`absolute -bottom-2 left-4 w-4 h-4 bg-slate-900 border-r border-b ${borderColor} transform rotate-45`}></div>
          <div className="relative">
            {content}
          </div>
        </div>
      )}
    </div>
  )
}

// Helper function to determine if metric improved
const hasImproved = (original: number, optimized: number, lowerIsBetter: boolean = true): 'improved' | 'worsened' | 'unchanged' => {
  const diff = Math.abs(original - optimized)
  if (diff < 0.001) return 'unchanged' // Effectively no change
  
  if (lowerIsBetter) {
    return optimized < original ? 'improved' : 'worsened'
  } else {
    return optimized > original ? 'improved' : 'worsened'
  }
}

// Formula explanations
const formulaExplanations: Record<string, {
  name: string
  formula: string
  symbols: string[]
  description: string
  calculation: (orig: GraphMetrics, opt: GraphMetrics) => { original: string, optimized: string }
}> = {
  'Efficiency Score': {
    name: 'Efficiency Score',
    formula: 'E = [(1 - R) + (1 - D) + C] / 3',
    symbols: [
      'E = Efficiency Score (0-1, higher is better)',
      'R = Redundancy Ratio',
      'D = Graph Density',
      'C = Compactness Score'
    ],
    description: 'Composite metric combining redundancy, density, and compactness. Higher score means more efficient graph structure.',
    calculation: (orig, opt) => ({
      original: `[(1 - ${orig.redundancy_ratio.toFixed(3)}) + (1 - ${orig.density.toFixed(3)}) + ${orig.compactness_score.toFixed(3)}] / 3 = ${orig.efficiency_score.toFixed(3)}`,
      optimized: `[(1 - ${opt.redundancy_ratio.toFixed(3)}) + (1 - ${opt.density.toFixed(3)}) + ${opt.compactness_score.toFixed(3)}] / 3 = ${opt.efficiency_score.toFixed(3)}`
    })
  },
  'Redundancy Ratio': {
    name: 'Redundancy Ratio',
    formula: 'R = (|TC| - |TR|) / |E|',
    symbols: [
      'R = Redundancy Ratio (0-1, lower is better)',
      '|TC| = Edges in Transitive Closure',
      '|TR| = Edges in Transitive Reduction',
      '|E| = Total edges in graph'
    ],
    description: 'Percentage of edges that are transitive (redundant). Lower means fewer unnecessary edges.',
    calculation: (orig, opt) => ({
      original: `Redundant edges / Total edges = ${(orig.redundancy_ratio * 100).toFixed(1)}%`,
      optimized: `Redundant edges / Total edges = ${(opt.redundancy_ratio * 100).toFixed(1)}%`
    })
  },
  'Graph Density': {
    name: 'Graph Density',
    formula: 'D = |E| / (|V| × (|V| - 1))',
    symbols: [
      'D = Density (0-1, context-dependent)',
      '|E| = Number of edges',
      '|V| = Number of nodes'
    ],
    description: 'Ratio of actual edges to maximum possible edges. Lower usually means sparser, more efficient graph.',
    calculation: (orig, opt) => ({
      original: `${orig.num_edges} / (${orig.num_nodes} × ${orig.num_nodes - 1}) = ${(orig.density * 100).toFixed(2)}%`,
      optimized: `${opt.num_edges} / (${opt.num_nodes} × ${opt.num_nodes - 1}) = ${(opt.density * 100).toFixed(2)}%`
    })
  },
  'Topological Complexity': {
    name: 'Topological Complexity',
    formula: 'TC = max(level(v)) for all v',
    symbols: [
      'TC = Topological Complexity (integer, lower is better)',
      'level(v) = Longest path from any source to node v'
    ],
    description: 'Maximum depth of the DAG. Lower means flatter structure with more parallelism potential.',
    calculation: (orig, opt) => ({
      original: `Maximum topological level = ${orig.topological_complexity}`,
      optimized: `Maximum topological level = ${opt.topological_complexity}`
    })
  },
  'Cyclomatic Complexity': {
    name: 'Cyclomatic Complexity',
    formula: 'CC = |E| - |V| + 2×P',
    symbols: [
      'CC = Cyclomatic Complexity (integer)',
      '|E| = Number of edges',
      '|V| = Number of nodes',
      'P = Number of connected components'
    ],
    description: 'Measures structural complexity. Lower means simpler graph with fewer decision paths.',
    calculation: (orig, opt) => ({
      original: `${orig.num_edges} - ${orig.num_nodes} + 2×${orig.strongly_connected_components} = ${orig.cyclomatic_complexity}`,
      optimized: `${opt.num_edges} - ${opt.num_nodes} + 2×${opt.strongly_connected_components} = ${opt.cyclomatic_complexity}`
    })
  },
  'Compactness Score': {
    name: 'Compactness Score',
    formula: 'C = 1 - (|E| / (n(n-1)/2))',
    symbols: [
      'C = Compactness (0-1, higher is better)',
      '|E| = Number of edges',
      'n = Number of nodes',
      'n(n-1)/2 = Maximum possible edges'
    ],
    description: 'Measures how compact/sparse the graph is. Higher means fewer edges relative to nodes.',
    calculation: (orig, opt) => ({
      original: `1 - (${orig.num_edges} / ${orig.num_nodes * (orig.num_nodes - 1) / 2}) = ${orig.compactness_score.toFixed(3)}`,
      optimized: `1 - (${opt.num_edges} / ${opt.num_nodes * (opt.num_nodes - 1) / 2}) = ${opt.compactness_score.toFixed(3)}`
    })
  }
}

export default function ResearchInsights({ originalMetrics, optimizedMetrics }: ResearchInsightsProps) {
  // Calculate improvements
  const edgeReduction = ((originalMetrics.num_edges - optimizedMetrics.num_edges) / originalMetrics.num_edges * 100).toFixed(1)
  const redundancyReduction = ((originalMetrics.redundancy_ratio - optimizedMetrics.redundancy_ratio) * 100).toFixed(1)
  const efficiencyGain = ((optimizedMetrics.efficiency_score - originalMetrics.efficiency_score) * 100).toFixed(1)
  const complexityReduction = ((originalMetrics.topological_complexity - optimizedMetrics.topological_complexity) / originalMetrics.topological_complexity * 100).toFixed(1)

  const insights = [
    {
      title: "Graph Efficiency Analysis",
      icon: Zap,
      color: "text-yellow-400",
      bgColor: "bg-yellow-500/10",
      metrics: [
        { 
          label: "Efficiency Score", 
          original: (originalMetrics.efficiency_score * 100).toFixed(1), 
          optimized: (optimizedMetrics.efficiency_score * 100).toFixed(1), 
          unit: "%", 
          status: hasImproved(originalMetrics.efficiency_score, optimizedMetrics.efficiency_score, false),
          hasHelp: true
        },
        { 
          label: "Redundancy Ratio", 
          original: (originalMetrics.redundancy_ratio * 100).toFixed(1), 
          optimized: (optimizedMetrics.redundancy_ratio * 100).toFixed(1), 
          unit: "%", 
          status: hasImproved(originalMetrics.redundancy_ratio, optimizedMetrics.redundancy_ratio, true),
          hasHelp: true
        },
        { 
          label: "Graph Density", 
          original: (originalMetrics.density * 100).toFixed(2), 
          optimized: (optimizedMetrics.density * 100).toFixed(2), 
          unit: "%", 
          status: hasImproved(originalMetrics.density, optimizedMetrics.density, true),
          hasHelp: true
        },
      ]
    },
    {
      title: "Structural Complexity",
      icon: GitBranch,
      color: "text-blue-400",
      bgColor: "bg-blue-500/10",
      metrics: [
        { 
          label: "Topological Complexity", 
          original: originalMetrics.topological_complexity, 
          optimized: optimizedMetrics.topological_complexity, 
          unit: "levels", 
          status: hasImproved(originalMetrics.topological_complexity, optimizedMetrics.topological_complexity, true),
          hasHelp: true
        },
        { 
          label: "Cyclomatic Complexity", 
          original: originalMetrics.cyclomatic_complexity, 
          optimized: optimizedMetrics.cyclomatic_complexity, 
          unit: "", 
          status: hasImproved(originalMetrics.cyclomatic_complexity, optimizedMetrics.cyclomatic_complexity, true),
          hasHelp: true
        },
        { 
          label: "Average Path Length", 
          original: originalMetrics.avg_path_length.toFixed(2), 
          optimized: optimizedMetrics.avg_path_length.toFixed(2), 
          unit: "hops", 
          status: hasImproved(originalMetrics.avg_path_length, optimizedMetrics.avg_path_length, true),
          hasHelp: false
        },
      ]
    },
    {
      title: "Degree Distribution",
      icon: Activity,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10",
      metrics: [
        { 
          label: "Average Degree", 
          original: originalMetrics.avg_degree.toFixed(2), 
          optimized: optimizedMetrics.avg_degree.toFixed(2), 
          unit: "", 
          status: hasImproved(originalMetrics.avg_degree, optimizedMetrics.avg_degree, true),
          hasHelp: false
        },
        { 
          label: "Max In-Degree", 
          original: originalMetrics.max_in_degree, 
          optimized: optimizedMetrics.max_in_degree, 
          unit: "", 
          status: hasImproved(originalMetrics.max_in_degree, optimizedMetrics.max_in_degree, true),
          hasHelp: false
        },
        { 
          label: "Max Out-Degree", 
          original: originalMetrics.max_out_degree, 
          optimized: optimizedMetrics.max_out_degree, 
          unit: "", 
          status: hasImproved(originalMetrics.max_out_degree, optimizedMetrics.max_out_degree, true),
          hasHelp: false
        },
      ]
    },
    {
      title: "Critical Path Analysis",
      icon: Target,
      color: "text-green-400",
      bgColor: "bg-green-500/10",
      metrics: [
        { 
          label: "Critical Path Length", 
          original: originalMetrics.critical_path.length, 
          optimized: optimizedMetrics.critical_path.length, 
          unit: "nodes", 
          status: hasImproved(originalMetrics.critical_path.length, optimizedMetrics.critical_path.length, true),
          hasHelp: false
        },
        { 
          label: "Graph Diameter", 
          original: originalMetrics.diameter, 
          optimized: optimizedMetrics.diameter, 
          unit: "", 
          status: hasImproved(typeof originalMetrics.diameter === 'number' ? originalMetrics.diameter : 0, 
                           typeof optimizedMetrics.diameter === 'number' ? optimizedMetrics.diameter : 0, true),
          hasHelp: false
        },
        { 
          label: "Bottleneck Nodes", 
          original: originalMetrics.bottleneck_nodes.length, 
          optimized: optimizedMetrics.bottleneck_nodes.length, 
          unit: "", 
          status: hasImproved(originalMetrics.bottleneck_nodes.length, optimizedMetrics.bottleneck_nodes.length, true),
          hasHelp: false
        },
      ]
    }
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="research-card border-l-4 border-blue-500">
        <h2 className="text-2xl font-bold text-white mb-2">📊 Research-Grade Analysis</h2>
        <p className="text-slate-400">Mathematical insights into DAG optimization efficiency</p>
      </div>

      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="research-card border-l-4 border-green-500"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm">Edge Reduction</span>
            {parseFloat(edgeReduction) > 0 ? (
              <TrendingDown className="w-5 h-5 text-green-400" />
            ) : (
              <CheckCircle className="w-5 h-5 text-slate-500" />
            )}
          </div>
          <div className="text-3xl font-bold text-white">{edgeReduction}%</div>
          <div className="text-xs text-slate-500 mt-1">
            {originalMetrics.num_edges} → {optimizedMetrics.num_edges} edges
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="research-card border-l-4 border-yellow-500"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm">Efficiency Gain</span>
            {parseFloat(efficiencyGain) > 0 ? (
              <TrendingUp className="w-5 h-5 text-yellow-400" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-slate-500" />
            )}
          </div>
          <div className="text-3xl font-bold text-white">{efficiencyGain > '0' ? '+' : ''}{efficiencyGain}%</div>
          <div className="text-xs text-slate-500 mt-1">
            Composite efficiency metric
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="research-card border-l-4 border-purple-500"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm">Redundancy ↓</span>
            {parseFloat(redundancyReduction) > 0 ? (
              <TrendingDown className="w-5 h-5 text-purple-400" />
            ) : (
              <CheckCircle className="w-5 h-5 text-slate-500" />
            )}
          </div>
          <div className="text-3xl font-bold text-white">{redundancyReduction}%</div>
          <div className="text-xs text-slate-500 mt-1">
            Transitive edge removal
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.02 }}
          className="research-card border-l-4 border-blue-500"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm">Complexity ↓</span>
            {parseFloat(complexityReduction) > 0 ? (
              <TrendingDown className="w-5 h-5 text-blue-400" />
            ) : (
              <CheckCircle className="w-5 h-5 text-slate-500" />
            )}
          </div>
          <div className="text-3xl font-bold text-white">{complexityReduction}%</div>
          <div className="text-xs text-slate-500 mt-1">
            Topological simplification
          </div>
        </motion.div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {insights.map((section, idx) => {
          const Icon = section.icon
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="research-card"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className={`p-3 rounded-lg ${section.bgColor}`}>
                  <Icon className={`w-6 h-6 ${section.color}`} />
                </div>
                <h3 className="text-lg font-semibold text-white">{section.title}</h3>
              </div>

              <div className="space-y-3">
                {section.metrics.map((metric, metricIdx) => (
                  <div key={metricIdx} className="bg-slate-900/50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-slate-400">{metric.label}</span>
                        {metric.hasHelp && (
                          <Tooltip
                            content={
                              <>
                                <div className="mb-3">
                                  <div className="text-xs font-semibold text-blue-400 mb-1">Formula</div>
                                  <code className="text-sm text-white font-mono bg-slate-800 px-2 py-1 rounded block">
                                    {formulaExplanations[metric.label].formula}
                                  </code>
                                </div>
                                <div className="mb-3">
                                  <div className="text-xs font-semibold text-blue-400 mb-1">What it means</div>
                                  <p className="text-xs text-slate-300 leading-relaxed">
                                    {formulaExplanations[metric.label].description}
                                  </p>
                                </div>
                                <div>
                                  <div className="text-xs font-semibold text-blue-400 mb-2">Your values</div>
                                  <div className="space-y-2">
                                    <div className="bg-blue-900/20 border border-blue-700/30 rounded px-2 py-1">
                                      <div className="text-xs text-blue-300 mb-0.5">Original</div>
                                      <code className="text-xs text-slate-200 font-mono">
                                        {formulaExplanations[metric.label].calculation(originalMetrics, optimizedMetrics).original}
                                      </code>
                                    </div>
                                    <div className="bg-green-900/20 border border-green-700/30 rounded px-2 py-1">
                                      <div className="text-xs text-green-300 mb-0.5">Optimized</div>
                                      <code className="text-xs text-slate-200 font-mono">
                                        {formulaExplanations[metric.label].calculation(originalMetrics, optimizedMetrics).optimized}
                                      </code>
                                    </div>
                                  </div>
                                </div>
                              </>
                            }
                          >
                            <HelpCircle className="w-4 h-4 text-blue-400 cursor-help" />
                          </Tooltip>
                        )}
                      </div>
                      {metric.status === 'improved' ? (
                        <span className="text-xs text-green-400 flex items-center gap-1">
                          <TrendingDown className="w-3 h-3" />
                          Improved
                        </span>
                      ) : metric.status === 'worsened' ? (
                        <span className="text-xs text-orange-400 flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          Worsened
                        </span>
                      ) : (
                        <span className="text-xs text-slate-500">No change</span>
                      )}
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-baseline gap-2">
                        <span className="text-slate-500 text-sm line-through">
                          {metric.original}{metric.unit}
                        </span>
                        <span className="text-white font-semibold">
                          {metric.optimized}{metric.unit}
                        </span>
                      </div>
                      {metric.status !== 'unchanged' && (
                        <span className={`text-xs ${metric.status === 'improved' ? 'text-green-400' : 'text-orange-400'}`}>
                          {Math.abs(((parseFloat(String(metric.original)) - parseFloat(String(metric.optimized))) / parseFloat(String(metric.original)) * 100)).toFixed(1)}%
                        </span>
                      )}
                    </div>
                  </div>
                ))}
      </div>

    </motion.div>
  )
})}
      </div>

      {/* Critical Path Visualization */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="research-card"
      >
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-red-400" />
          Critical Path & Bottlenecks
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-slate-400 mb-3">Critical Path (Longest)</h4>
            <div className="flex flex-wrap gap-2">
              {optimizedMetrics.critical_path.slice(0, 10).map((node, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-red-500/20 border border-red-500/30 rounded-full text-sm text-red-300"
                >
                  {node}
                </span>
              ))}
              {optimizedMetrics.critical_path.length > 10 && (
                <span className="px-3 py-1 text-sm text-slate-500">
                  +{optimizedMetrics.critical_path.length - 10} more
                </span>
              )}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-slate-400 mb-3">Bottleneck Nodes (High Centrality)</h4>
            <div className="flex flex-wrap gap-2">
              {optimizedMetrics.bottleneck_nodes.map((node, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-orange-500/20 border border-orange-500/30 rounded-full text-sm text-orange-300"
                >
                  {node}
                </span>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Mathematical Formulas */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="research-card bg-slate-900/50"
      >
        <h3 className="text-lg font-semibold text-white mb-4">📐 Mathematical Definitions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <div className="text-slate-300">
              <div className="flex items-center gap-2 mb-1">
                <strong className="text-blue-400">Efficiency Score:</strong>
                <Tooltip
                  borderColor="border-blue-500/50"
                  content={
                    <>
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-blue-400 mb-1">Formula</div>
                        <code className="text-sm text-white font-mono bg-slate-800 px-2 py-1 rounded block">
                          {formulaExplanations['Efficiency Score'].formula}
                        </code>
                      </div>
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-blue-400 mb-1">What it means</div>
                        <p className="text-xs text-slate-300 leading-relaxed">
                          {formulaExplanations['Efficiency Score'].description}
                        </p>
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-blue-400 mb-2">Your values</div>
                        <div className="space-y-2">
                          <div className="bg-blue-900/20 border border-blue-700/30 rounded px-2 py-1">
                            <div className="text-xs text-blue-300 mb-0.5">Original</div>
                            <code className="text-xs text-slate-200 font-mono">
                              {formulaExplanations['Efficiency Score'].calculation(originalMetrics, optimizedMetrics).original}
                            </code>
                          </div>
                          <div className="bg-green-900/20 border border-green-700/30 rounded px-2 py-1">
                            <div className="text-xs text-green-300 mb-0.5">Optimized</div>
                            <code className="text-xs text-slate-200 font-mono">
                              {formulaExplanations['Efficiency Score'].calculation(originalMetrics, optimizedMetrics).optimized}
                            </code>
                          </div>
                        </div>
                      </div>
                    </>
                  }
                >
                  <HelpCircle className="w-4 h-4 text-blue-400 cursor-help" />
                </Tooltip>
              </div>
              <code className="block mt-1 p-2 bg-slate-800 rounded text-xs">
                E = (1 - R) + (1 - D) + C / 3
              </code>
              <span className="text-slate-500 text-xs">R=redundancy, D=density, C=compactness</span>
            </div>
            <div className="text-slate-300">
              <div className="flex items-center gap-2 mb-1">
                <strong className="text-purple-400">Redundancy Ratio:</strong>
                <Tooltip
                  borderColor="border-purple-500/50"
                  content={
                    <>
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-purple-400 mb-1">Formula</div>
                        <code className="text-sm text-white font-mono bg-slate-800 px-2 py-1 rounded block">
                          {formulaExplanations['Redundancy Ratio'].formula}
                        </code>
                      </div>
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-purple-400 mb-1">What it means</div>
                        <p className="text-xs text-slate-300 leading-relaxed">
                          {formulaExplanations['Redundancy Ratio'].description}
                        </p>
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-purple-400 mb-2">Your values</div>
                        <div className="space-y-2">
                          <div className="bg-blue-900/20 border border-blue-700/30 rounded px-2 py-1">
                            <div className="text-xs text-blue-300 mb-0.5">Original</div>
                            <code className="text-xs text-slate-200 font-mono">
                              {formulaExplanations['Redundancy Ratio'].calculation(originalMetrics, optimizedMetrics).original}
                            </code>
                          </div>
                          <div className="bg-green-900/20 border border-green-700/30 rounded px-2 py-1">
                            <div className="text-xs text-green-300 mb-0.5">Optimized</div>
                            <code className="text-xs text-slate-200 font-mono">
                              {formulaExplanations['Redundancy Ratio'].calculation(originalMetrics, optimizedMetrics).optimized}
                            </code>
                          </div>
                        </div>
                      </div>
                    </>
                  }
                >
                  <HelpCircle className="w-4 h-4 text-purple-400 cursor-help" />
                </Tooltip>
              </div>
              <code className="block mt-1 p-2 bg-slate-800 rounded text-xs">
                R = (|TC| - |TR|) / |E|
              </code>
              <span className="text-slate-500 text-xs">TC=transitive closure, TR=transitive reduction</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-slate-300">
              <div className="flex items-center gap-2 mb-1">
                <strong className="text-green-400">Compactness Score:</strong>
                <Tooltip
                  borderColor="border-green-500/50"
                  content={
                    <>
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-green-400 mb-1">Formula</div>
                        <code className="text-sm text-white font-mono bg-slate-800 px-2 py-1 rounded block">
                          {formulaExplanations['Compactness Score'].formula}
                        </code>
                      </div>
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-green-400 mb-1">What it means</div>
                        <p className="text-xs text-slate-300 leading-relaxed">
                          {formulaExplanations['Compactness Score'].description}
                        </p>
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-green-400 mb-2">Your values</div>
                        <div className="space-y-2">
                          <div className="bg-blue-900/20 border border-blue-700/30 rounded px-2 py-1">
                            <div className="text-xs text-blue-300 mb-0.5">Original</div>
                            <code className="text-xs text-slate-200 font-mono">
                              {formulaExplanations['Compactness Score'].calculation(originalMetrics, optimizedMetrics).original}
                            </code>
                          </div>
                          <div className="bg-green-900/20 border border-green-700/30 rounded px-2 py-1">
                            <div className="text-xs text-green-300 mb-0.5">Optimized</div>
                            <code className="text-xs text-slate-200 font-mono">
                              {formulaExplanations['Compactness Score'].calculation(originalMetrics, optimizedMetrics).optimized}
                            </code>
                          </div>
                        </div>
                      </div>
                    </>
                  }
                >
                  <HelpCircle className="w-4 h-4 text-green-400 cursor-help" />
                </Tooltip>
              </div>
              <code className="block mt-1 p-2 bg-slate-800 rounded text-xs">
                C = 1 - (|E| / (n(n-1)/2))
              </code>
              <span className="text-slate-500 text-xs">n=nodes, E=edges</span>
            </div>
            <div className="text-slate-300">
              <div className="flex items-center gap-2 mb-1">
                <strong className="text-yellow-400">Degree Entropy:</strong>
                <Tooltip
                  borderColor="border-yellow-500/50"
                  content={
                    <>
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-yellow-400 mb-1">What it measures</div>
                        <p className="text-xs text-slate-300 leading-relaxed">
                          Measures the diversity of node degrees in your graph. Higher entropy means more varied connectivity patterns. Low entropy indicates uniform structure (many nodes with same degree).
                        </p>
                      </div>
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-yellow-400 mb-1">Formula</div>
                        <code className="text-sm text-white font-mono bg-slate-800 px-2 py-1 rounded block">
                          H = -Σ(p_i × log₂(p_i))
                        </code>
                        <p className="text-xs text-slate-400 mt-1">where p_i = probability of degree i</p>
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-yellow-400 mb-2">Your values</div>
                        <div className="space-y-2">
                          <div className="bg-blue-900/20 border border-blue-700/30 rounded px-2 py-1">
                            <div className="text-xs text-blue-300 mb-0.5">Original</div>
                            <code className="text-xs text-slate-200 font-mono">
                              Entropy = {originalMetrics.degree_entropy.toFixed(4)}
                            </code>
                          </div>
                          <div className="bg-green-900/20 border border-green-700/30 rounded px-2 py-1">
                            <div className="text-xs text-green-300 mb-0.5">Optimized</div>
                            <code className="text-xs text-slate-200 font-mono">
                              Entropy = {optimizedMetrics.degree_entropy.toFixed(4)}
                            </code>
                          </div>
                        </div>
                      </div>
                      <div className="mt-3 pt-3 border-t border-slate-700">
                        <p className="text-xs text-slate-400">
                          💡 <strong>Use case:</strong> Helps identify whether your graph has balanced connectivity or if some nodes are hubs while others are isolated.
                        </p>
                      </div>
                    </>
                  }
                >
                  <HelpCircle className="w-4 h-4 text-yellow-400 cursor-help" />
                </Tooltip>
              </div>
              <code className="block mt-1 p-2 bg-slate-800 rounded text-xs">
                H = -Σ(p_i × log₂(p_i))
              </code>
              <span className="text-slate-500 text-xs">p_i=probability of degree i</span>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}


