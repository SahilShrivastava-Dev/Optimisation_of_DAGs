import { useState } from 'react'
import { motion } from 'framer-motion'
import { X, Database, Loader, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'
import { OptimizationResult } from '../types'

interface Neo4jExportProps {
  result: OptimizationResult
  onClose: () => void
}

const Neo4jExport = ({ result, onClose }: Neo4jExportProps) => {
  const [uri, setUri] = useState('bolt://localhost:7687')
  const [username, setUsername] = useState('neo4j')
  const [password, setPassword] = useState('')
  const [graphType, setGraphType] = useState<'original' | 'optimized'>('optimized')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handlePush = async () => {
    if (!password) {
      toast.error('Please enter password')
      return
    }

    setLoading(true)
    
    try {
      await axios.post('/api/neo4j/push', {
        config: {
          uri,
          username,
          password,
          graph_type: graphType
        },
        options: {
          edges: result[graphType].edges,
          transitive_reduction: true,
          merge_nodes: true,
          handle_cycles: 'error'
        }
      })

      setSuccess(true)
      toast.success('Successfully pushed to Neo4j!')
      setTimeout(() => {
        onClose()
      }, 2000)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to push to Neo4j')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="glass-morphism p-8 rounded-2xl max-w-md w-full shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-2xl font-bold text-slate-800">Push to Neo4j</h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-600" />
          </button>
        </div>

        {success ? (
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-center py-8"
          >
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <p className="text-lg font-semibold text-slate-800">Successfully Pushed!</p>
            <p className="text-sm text-slate-600 mt-2">Your graph is now in Neo4j</p>
          </motion.div>
        ) : (
          <div className="space-y-6">
            {/* Graph Type Selection */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-slate-700">
                Which graph to push?
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setGraphType('original')}
                  className={`
                    p-3 rounded-xl border-2 transition-all font-medium
                    ${graphType === 'original'
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                    }
                  `}
                >
                  Original
                </button>
                <button
                  onClick={() => setGraphType('optimized')}
                  className={`
                    p-3 rounded-xl border-2 transition-all font-medium
                    ${graphType === 'optimized'
                      ? 'border-green-500 bg-green-50 text-green-700'
                      : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                    }
                  `}
                >
                  Optimized
                </button>
              </div>
            </div>

            {/* Connection Details */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Bolt URI
                </label>
                <input
                  type="text"
                  value={uri}
                  onChange={(e) => setUri(e.target.value)}
                  placeholder="bolt://localhost:7687"
                  className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="neo4j"
                  className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Push Button */}
            <button
              onClick={handlePush}
              disabled={loading || !password}
              className="w-full py-3 px-6 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  <span>Pushing...</span>
                </>
              ) : (
                <>
                  <Database className="w-5 h-5" />
                  <span>Push to Neo4j</span>
                </>
              )}
            </button>
          </div>
        )}
      </motion.div>
    </motion.div>
  )
}

export default Neo4jExport

