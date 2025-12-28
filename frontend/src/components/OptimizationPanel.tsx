import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, Loader, Settings } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'
import { Edge, OptimizationResult } from '../types'

interface OptimizationPanelProps {
  edges: Edge[]
  setResult: (result: OptimizationResult) => void
  loading: boolean
  setLoading: (loading: boolean) => void
}

const OptimizationPanel = ({ edges, setResult, loading, setLoading }: OptimizationPanelProps) => {
  const [transitiveReduction, setTransitiveReduction] = useState(true)
  const [mergeNodes, setMergeNodes] = useState(true)
  const [handleCycles, setHandleCycles] = useState<'error' | 'remove'>('error')

  const handleOptimize = async () => {
    setLoading(true)
    
    try {
      const response = await axios.post('/api/optimize', {
        edges,
        transitive_reduction: transitiveReduction,
        merge_nodes: mergeNodes,
        handle_cycles: handleCycles
      })

      if (response.data.error) {
        toast.error(response.data.error)
        return
      }

      setResult(response.data)
      toast.success('Optimization completed!')
      
      // Scroll to results
      setTimeout(() => {
        document.getElementById('results-section')?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
      }, 100)
    } catch (error) {
      toast.error('Optimization failed')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-morphism p-8 rounded-2xl"
    >
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-2 bg-purple-500/20 rounded-lg">
          <Settings className="w-6 h-6 text-purple-400" />
        </div>
        <h2 className="text-2xl font-bold text-white">Optimization Settings</h2>
      </div>

      <div className="space-y-6">
        {/* Options */}
        <div className="grid md:grid-cols-2 gap-4">
          {/* Transitive Reduction */}
          <div 
            onClick={() => !loading && setTransitiveReduction(!transitiveReduction)}
            className={`
              p-6 rounded-xl border-2 transition-all cursor-pointer
              ${transitiveReduction 
                ? 'border-blue-500 bg-blue-900/30' 
                : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
              }
              ${loading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                checked={transitiveReduction}
                onChange={() => {}}
                disabled={loading}
                className="mt-1 w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex-1">
                <h3 className="font-semibold text-white mb-1">Transitive Reduction</h3>
                <p className="text-sm text-slate-300">
                  Remove redundant edges while preserving reachability
                </p>
              </div>
            </div>
          </div>

          {/* Merge Nodes */}
          <div 
            onClick={() => !loading && setMergeNodes(!mergeNodes)}
            className={`
              p-6 rounded-xl border-2 transition-all cursor-pointer
              ${mergeNodes 
                ? 'border-blue-500 bg-blue-900/30' 
                : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
              }
              ${loading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                checked={mergeNodes}
                onChange={() => {}}
                disabled={loading}
                className="mt-1 w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex-1">
                <h3 className="font-semibold text-white mb-1">Merge Equivalent Nodes</h3>
                <p className="text-sm text-slate-300">
                  Combine nodes with identical parents and children
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Cycle Handling */}
        <div className="space-y-3">
          <label className="block text-sm font-semibold text-white">
            If cycles are detected:
          </label>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setHandleCycles('error')}
              disabled={loading}
              className={`
                p-4 rounded-xl border-2 transition-all
                ${handleCycles === 'error' 
                  ? 'border-red-500 bg-red-900/30' 
                  : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                }
                ${loading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <p className="font-semibold text-white">Show Error</p>
              <p className="text-xs text-slate-300 mt-1">Stop optimization</p>
            </button>
            <button
              onClick={() => setHandleCycles('remove')}
              disabled={loading}
              className={`
                p-4 rounded-xl border-2 transition-all
                ${handleCycles === 'remove' 
                  ? 'border-amber-500 bg-amber-900/30' 
                  : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                }
                ${loading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <p className="font-semibold text-white">Auto Remove</p>
              <p className="text-xs text-slate-300 mt-1">Break cycles automatically</p>
            </button>
          </div>
        </div>

        {/* Optimize Button */}
        <button
          onClick={handleOptimize}
          disabled={loading || !transitiveReduction && !mergeNodes}
          className="w-full py-4 px-6 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl font-bold text-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3"
        >
          {loading ? (
            <>
              <Loader className="w-6 h-6 animate-spin" />
              <span>Optimizing...</span>
            </>
          ) : (
            <>
              <Play className="w-6 h-6" />
              <span>Optimize Graph</span>
            </>
          )}
        </button>
      </div>
    </motion.section>
  )
}

export default OptimizationPanel

