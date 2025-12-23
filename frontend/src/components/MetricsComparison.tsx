import { motion } from 'framer-motion'
import { BarChart, TrendingDown, TrendingUp, Minus } from 'lucide-react'
import { OptimizationResult, GraphMetrics } from '../types'

interface MetricsComparisonProps {
  result: OptimizationResult
}

const MetricsComparison = ({ result }: MetricsComparisonProps) => {
  const metrics: Array<{ key: keyof GraphMetrics; label: string; format?: (val: any) => string }> = [
    { key: 'num_nodes', label: 'Nodes' },
    { key: 'num_edges', label: 'Edges' },
    { key: 'num_leaf_nodes', label: 'Leaf Nodes' },
    { key: 'depth', label: 'Depth' },
    { key: 'width', label: 'Width' },
    { key: 'density', label: 'Density', format: (val) => typeof val === 'number' ? val.toFixed(4) : val },
    { key: 'cyclomatic_complexity', label: 'Complexity' },
    { key: 'degree_entropy', label: 'Entropy', format: (val) => typeof val === 'number' ? val.toFixed(3) : val },
  ]

  const getChangeIndicator = (original: any, optimized: any) => {
    if (typeof original !== 'number' || typeof optimized !== 'number') {
      return <Minus className="w-4 h-4 text-slate-400" />
    }
    
    const diff = optimized - original
    if (diff < 0) {
      return <TrendingDown className="w-4 h-4 text-green-500" />
    } else if (diff > 0) {
      return <TrendingUp className="w-4 h-4 text-red-500" />
    }
    return <Minus className="w-4 h-4 text-slate-400" />
  }

  const formatValue = (value: any, formatter?: (val: any) => string) => {
    if (formatter) return formatter(value)
    return typeof value === 'number' ? value.toString() : String(value)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-morphism p-8 rounded-2xl"
    >
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-2 bg-indigo-100 rounded-lg">
          <BarChart className="w-6 h-6 text-indigo-600" />
        </div>
        <h3 className="text-2xl font-bold text-slate-800">Metrics Comparison</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-slate-200">
              <th className="text-left py-4 px-4 font-semibold text-slate-700">Metric</th>
              <th className="text-center py-4 px-4 font-semibold text-slate-700">Original</th>
              <th className="text-center py-4 px-4 font-semibold text-slate-700">Optimized</th>
              <th className="text-center py-4 px-4 font-semibold text-slate-700">Change</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((metric, idx) => {
              const original = result.original.metrics[metric.key]
              const optimized = result.optimized.metrics[metric.key]
              
              return (
                <motion.tr
                  key={metric.key}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors"
                >
                  <td className="py-4 px-4 font-medium text-slate-700">{metric.label}</td>
                  <td className="py-4 px-4 text-center">
                    <span className="inline-block px-3 py-1 bg-blue-50 text-blue-700 rounded-lg font-semibold">
                      {formatValue(original, metric.format)}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className="inline-block px-3 py-1 bg-green-50 text-green-700 rounded-lg font-semibold">
                      {formatValue(optimized, metric.format)}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex justify-center">
                      {getChangeIndicator(original, optimized)}
                    </div>
                  </td>
                </motion.tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}

export default MetricsComparison

