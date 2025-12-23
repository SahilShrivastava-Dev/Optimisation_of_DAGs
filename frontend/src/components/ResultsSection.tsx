import { motion } from 'framer-motion'
import { Download, Database, TrendingDown, BarChart } from 'lucide-react'
import { OptimizationResult } from '../types'
import MetricsComparison from './MetricsComparison'
import GraphVisualization from './GraphVisualization'
import Neo4jExport from './Neo4jExport'
import { useState } from 'react'

interface ResultsSectionProps {
  result: OptimizationResult
}

const ResultsSection = ({ result }: ResultsSectionProps) => {
  const [showNeo4j, setShowNeo4j] = useState(false)

  const improvement = {
    nodes: ((result.original.metrics.num_nodes - result.optimized.metrics.num_nodes) / result.original.metrics.num_nodes * 100).toFixed(1),
    edges: ((result.original.metrics.num_edges - result.optimized.metrics.num_edges) / result.original.metrics.num_edges * 100).toFixed(1)
  }

  const downloadJSON = () => {
    const dataStr = JSON.stringify(result, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `dag-optimization-${new Date().getTime()}.json`
    link.click()
  }

  return (
    <motion.section
      id="results-section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      {/* Header with Stats */}
      <div className="glass-morphism p-8 rounded-2xl">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingDown className="w-6 h-6 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-800">Optimization Results</h2>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={downloadJSON}
              className="px-4 py-2 bg-white hover:bg-slate-50 border border-slate-200 rounded-xl font-semibold text-slate-700 flex items-center space-x-2 transition-all"
            >
              <Download className="w-4 h-4" />
              <span>Export JSON</span>
            </button>
            
            <button
              onClick={() => setShowNeo4j(!showNeo4j)}
              className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-semibold flex items-center space-x-2 hover:shadow-lg transition-all"
            >
              <Database className="w-4 h-4" />
              <span>Push to Neo4j</span>
            </button>
          </div>
        </div>

        {/* Improvement Cards */}
        <div className="grid md:grid-cols-2 gap-4">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-xl border border-green-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-700">Nodes Reduced</p>
                <p className="text-3xl font-bold text-green-600 mt-1">
                  {result.original.metrics.num_nodes} → {result.optimized.metrics.num_nodes}
                </p>
              </div>
              <div className="text-right">
                <div className="inline-flex items-center px-3 py-1 bg-green-100 rounded-full">
                  <TrendingDown className="w-4 h-4 text-green-600 mr-1" />
                  <span className="text-sm font-bold text-green-700">{improvement.nodes}%</span>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-700">Edges Reduced</p>
                <p className="text-3xl font-bold text-blue-600 mt-1">
                  {result.original.metrics.num_edges} → {result.optimized.metrics.num_edges}
                </p>
              </div>
              <div className="text-right">
                <div className="inline-flex items-center px-3 py-1 bg-blue-100 rounded-full">
                  <TrendingDown className="w-4 h-4 text-blue-600 mr-1" />
                  <span className="text-sm font-bold text-blue-700">{improvement.edges}%</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Neo4j Export Modal */}
      {showNeo4j && (
        <Neo4jExport 
          result={result} 
          onClose={() => setShowNeo4j(false)} 
        />
      )}

      {/* Metrics Comparison */}
      <MetricsComparison result={result} />

      {/* Graph Visualizations */}
      <GraphVisualization result={result} />
    </motion.section>
  )
}

export default ResultsSection

