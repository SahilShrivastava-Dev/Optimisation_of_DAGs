import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Upload, FileText, Sparkles, X, Eye, Image as ImageIcon } from 'lucide-react'
import toast from 'react-hot-toast'
import { Edge } from '../types'
import axios from 'axios'
import InteractiveGraph from './InteractiveGraph'

interface InputSectionProps {
  edges: Edge[]
  setEdges: (edges: Edge[]) => void
  loading: boolean
}

type InputMode = 'upload' | 'paste' | 'random' | 'image'

const InputSection = ({ edges, setEdges, loading }: InputSectionProps) => {
  const [mode, setMode] = useState<InputMode>('upload')
  const [textInput, setTextInput] = useState('')
  const [numNodes, setNumNodes] = useState(10)
  const [edgeProbability, setEdgeProbability] = useState(0.3)
  const [showPreview, setShowPreview] = useState(true)
  const [graphStats, setGraphStats] = useState<{nodes: number, components: number} | null>(null)
  const [loadingStats, setLoadingStats] = useState(false)
  const [loadingImageExtraction, setLoadingImageExtraction] = useState(false)
  const [imageExtractionStatus, setImageExtractionStatus] = useState<any>(null)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post('/api/parse-csv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      const data = response.data
      const preview = data.preview
      const sourceCol = data.source_column
      const targetCol = data.target_column

      const newEdges: Edge[] = preview.map((row: any) => ({
        source: String(row[sourceCol]),
        target: String(row[targetCol]),
        classes: row.classes ? [row.classes] : []
      }))

      setEdges(newEdges)
      toast.success(`Loaded ${newEdges.length} edges from ${file.name}`)
    } catch (error) {
      toast.error('Failed to parse file')
      console.error(error)
    }
  }

  const handlePasteInput = () => {
    const lines = textInput.trim().split('\n')
    const newEdges: Edge[] = []

    for (const line of lines) {
      const parts = line.split(',').map(s => s.trim())
      if (parts.length >= 2) {
        newEdges.push({
          source: parts[0],
          target: parts[1],
          classes: parts[2] ? [parts[2]] : []
        })
      }
    }

    if (newEdges.length > 0) {
      setEdges(newEdges)
      toast.success(`Created ${newEdges.length} edges`)
    } else {
      toast.error('No valid edges found')
    }
  }

  const handleRandomGeneration = async () => {
    try {
      const response = await axios.post('/api/random-dag', {
        num_nodes: numNodes,
        edge_probability: edgeProbability
      })

      setEdges(response.data.edges)
      toast.success(`Generated random DAG with ${response.data.edges.length} edges`)
    } catch (error) {
      toast.error('Failed to generate random DAG')
      console.error(error)
    }
  }

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Check if it's an image
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file (JPG, PNG, etc.)')
      return
    }

    setLoadingImageExtraction(true)
    const loadingToast = toast.loading('🤖 AI is analyzing your image...')

    try {
      console.log('🖼️ IMAGE UPLOAD STARTED')
      console.log('📁 File:', file.name, file.type, file.size, 'bytes')
      
      const formData = new FormData()
      formData.append('file', file)

      console.log('📤 Sending to backend...')
      const response = await axios.post('/api/extract-from-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000  // 60 second timeout for AI processing
      })

      console.log('📥 Response received:', response.status)
      console.log('📊 Response data:', response.data)

      const data = response.data

      if (data.success) {
        console.log('✅ Extraction successful!')
        console.log('📊 Extracted edges:', data.edges)
        console.log('📊 Extracted nodes:', data.nodes)
        console.log('🔧 Method used:', data.method)
        
        const extractedEdges = data.edges
        console.log('🔄 Setting edges in state...')
        setEdges(extractedEdges)
        console.log('✅ Edges set! Length:', extractedEdges.length)
        
        toast.success(data.message, { id: loadingToast })
        
        // Show which method/model was used
        const modelName = data.model || 'OpenRouter API'
        toast(`✨ Extracted using ${modelName}`, { icon: '🤖', duration: 3000 })
      } else {
        console.log('❌ Extraction failed')
        console.log('Error type:', data.error)
        console.log('Error message:', data.message)
        // Handle different error types
        const errorType = data.error || 'unknown'
        
        if (errorType === 'api_key_required') {
          toast.error('OpenRouter API key required', { id: loadingToast })
          toast(
            <div className="space-y-2">
              <p className="font-semibold">To enable AI extraction:</p>
              <p className="text-xs">1. Get free API key: openrouter.ai/keys</p>
              <p className="text-xs">2. Set: OPENROUTER_API_KEY=your-key</p>
              <p className="text-xs">3. Restart backend</p>
              <p className="text-xs mt-2 text-green-400">✨ Free tier available!</p>
            </div>,
            {
              duration: 10000,
              icon: '🔑'
            }
          )
        } else if (errorType === 'setup_required' || errorType === 'dependencies_missing') {
          toast.error('Setup required', { id: loadingToast })
          toast(
            <div className="space-y-2">
              <p className="font-semibold">Backend setup needed</p>
              <p className="text-xs">{data.message}</p>
            </div>,
            {
              duration: 8000,
              icon: '📦'
            }
          )
        } else if (errorType === 'invalid_graph') {
          toast.error('Could not extract a valid graph', { id: loadingToast })
          toast('💡 Try a clearer image with labeled nodes (A, B, C) and visible arrows (→)', {
            duration: 6000,
            icon: '💡'
          })
        } else if (errorType === 'extraction_failed') {
          toast.error('Extraction failed', { id: loadingToast })
          toast('💡 Make sure: Clear nodes, visible arrows, good lighting', {
            duration: 5000,
            icon: '💡'
          })
        } else {
          toast.error(data.message || 'Could not extract DAG from image', { id: loadingToast })
        }
      }
    } catch (error: any) {
      console.error('❌ IMAGE EXTRACTION ERROR')
      console.error('Error object:', error)
      console.error('Error code:', error.code)
      console.error('Error message:', error.message)
      console.error('Error response:', error.response)
      
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error('Request timed out - image processing took too long', { id: loadingToast })
        toast('💡 Try a simpler image or check backend logs', { duration: 5000, icon: '⏱️' })
      } else if (error.response?.status === 500) {
        toast.error('Backend error during extraction', { id: loadingToast })
        toast('Check if backend is running and AI models are installed', {
          duration: 6000,
          icon: '⚠️'
        })
      } else if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        toast.error('Cannot connect to backend', { id: loadingToast })
        toast('Make sure backend is running on port 8000', { duration: 5000, icon: '🔌' })
      } else {
        const errorMsg = error.response?.data?.message || error.message || 'Unknown error occurred'
        toast.error(errorMsg, { id: loadingToast })
      }
    } finally {
      setLoadingImageExtraction(false)
      // Reset file input
      event.target.value = ''
    }
  }

  const fetchGraphStats = async (edgeList: Edge[]) => {
    if (edgeList.length === 0) return
    
    setLoadingStats(true)
    try {
      // Validate and get graph stats
      const validateResponse = await axios.post('/api/validate', {
        edges: edgeList
      })

      if (validateResponse.data) {
        setGraphStats({
          nodes: validateResponse.data.num_nodes,
          components: validateResponse.data.num_components
        })
      }
    } catch (error) {
      console.error('Failed to fetch graph stats:', error)
    } finally {
      setLoadingStats(false)
    }
  }

  useEffect(() => {
    console.log('🔄 Edges state changed! Length:', edges.length)
    if (edges.length > 0) {
      console.log('📊 Fetching graph stats for', edges.length, 'edges')
      fetchGraphStats(edges)
    } else {
      console.log('🗑️ No edges, clearing stats')
      setGraphStats(null)
    }
  }, [edges])

  const clearEdges = () => {
    setEdges([])
    setTextInput('')
    setGraphStats(null)
    toast.success('Cleared all edges')
  }

  const modes = [
    { id: 'upload', label: 'Upload CSV', icon: Upload },
    { id: 'image', label: 'Upload Image', icon: ImageIcon },
    { id: 'paste', label: 'Paste Edges', icon: FileText },
    { id: 'random', label: 'Random DAG', icon: Sparkles }
  ]

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-slate-800">Input Your Graph</h2>
        <p className="text-slate-500">Choose how you'd like to provide your DAG</p>
      </div>

      {/* Mode Selection */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {modes.map((m) => {
          const Icon = m.icon
          const isActive = mode === m.id
          return (
            <button
              key={m.id}
              onClick={() => setMode(m.id as InputMode)}
              disabled={loading}
              className={`
                relative p-6 rounded-2xl transition-all duration-300
                ${isActive 
                  ? 'glass-morphism ring-2 ring-blue-500 shadow-lg' 
                  : 'bg-white/50 hover:bg-white/70 border border-slate-200'
                }
                ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer card-hover'}
              `}
            >
              <div className="flex flex-col items-center space-y-3">
                <div className={`
                  p-3 rounded-xl transition-colors
                  ${isActive 
                    ? 'bg-gradient-to-r from-blue-500 to-indigo-600' 
                    : 'bg-slate-100'
                  }
                `}>
                  <Icon className={`w-6 h-6 ${isActive ? 'text-white' : 'text-slate-600'}`} />
                </div>
                <span className={`font-semibold ${isActive ? 'text-blue-600' : 'text-slate-700'}`}>
                  {m.label}
                </span>
              </div>
            </button>
          )
        })}
      </div>

      {/* Input Content */}
      <motion.div
        key={mode}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-morphism p-8 rounded-2xl"
      >
        {mode === 'upload' && (
          <div className="space-y-4">
            <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-slate-300 rounded-xl cursor-pointer hover:border-blue-500 transition-colors bg-slate-50/50">
              <div className="flex flex-col items-center justify-center space-y-4">
                <Upload className="w-12 h-12 text-slate-400" />
                <div className="text-center">
                  <p className="text-lg font-semibold text-slate-700">Drop your CSV or Excel file here</p>
                  <p className="text-sm text-slate-500 mt-1">or click to browse</p>
                </div>
              </div>
              <input
                type="file"
                className="hidden"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileUpload}
                disabled={loading}
              />
            </label>
            <p className="text-xs text-slate-500 text-center">
              Expected format: columns named "source" and "target"
            </p>
          </div>
        )}

        {mode === 'image' && (
          <div className="space-y-4">
            <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-purple-300 rounded-xl cursor-pointer hover:border-purple-500 transition-colors bg-gradient-to-br from-purple-50 to-pink-50">
              <div className="flex flex-col items-center justify-center space-y-4">
                <ImageIcon className="w-12 h-12 text-purple-400" />
                <div className="text-center">
                  <p className="text-lg font-semibold text-slate-700">Drop DAG image here</p>
                  <p className="text-sm text-slate-500 mt-1">or click to browse</p>
                  <p className="text-xs text-purple-600 mt-2 font-medium">🤖 AI will extract the graph structure</p>
                </div>
              </div>
              <input
                type="file"
                className="hidden"
                accept="image/*"
                onChange={handleImageUpload}
                disabled={loading || loadingImageExtraction}
              />
            </label>
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4 space-y-2">
              <p className="text-sm font-semibold text-purple-900">📸 Upload a DAG Image</p>
              <ul className="text-xs text-purple-700 space-y-1 ml-4 list-disc">
                <li>Photo of a whiteboard diagram</li>
                <li>Screenshot of a graph</li>
                <li>Hand-drawn DAG</li>
                <li>Any image with nodes and arrows</li>
              </ul>
              <p className="text-xs text-purple-600 mt-2">
                💡 AI will detect nodes and edges automatically!
              </p>
            </div>
          </div>
        )}

        {mode === 'paste' && (
          <div className="space-y-4">
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="source1,target1&#10;source2,target2,class_name&#10;source3,target3"
              disabled={loading}
              className="w-full h-64 px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm"
            />
            <button
              onClick={handlePasteInput}
              disabled={loading || !textInput.trim()}
              className="w-full py-3 px-6 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Build DAG
            </button>
          </div>
        )}

        {mode === 'random' && (
          <div className="space-y-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Number of Nodes: {numNodes}
                </label>
                <input
                  type="range"
                  min="2"
                  max="50"
                  value={numNodes}
                  onChange={(e) => setNumNodes(Number(e.target.value))}
                  disabled={loading}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Edge Probability: {edgeProbability.toFixed(2)}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={edgeProbability}
                  onChange={(e) => setEdgeProbability(Number(e.target.value))}
                  disabled={loading}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
                />
              </div>
            </div>

            <button
              onClick={handleRandomGeneration}
              disabled={loading}
              className="w-full py-3 px-6 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Generate Random DAG
            </button>
          </div>
        )}
      </motion.div>

      {/* Current Edges Summary with Preview */}
      {edges.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-morphism p-6 rounded-2xl space-y-4"
        >
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-green-100 rounded-xl">
                <FileText className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="font-semibold text-slate-800">Graph Loaded</p>
                <p className="text-sm text-slate-500">
                  {graphStats ? (
                    <>{graphStats.nodes} nodes • {edges.length} edges • {graphStats.components} component{graphStats.components !== 1 ? 's' : ''}</>
                  ) : (
                    <>{edges.length} edges ready for optimization</>
                  )}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowPreview(!showPreview)}
                className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                title={showPreview ? "Hide preview" : "Show preview"}
              >
                <Eye className={`w-5 h-5 ${showPreview ? 'text-blue-500' : 'text-slate-400'}`} />
              </button>
              <button
                onClick={clearEdges}
                className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                title="Clear graph"
              >
                <X className="w-5 h-5 text-red-500" />
              </button>
            </div>
          </div>

          {/* Interactive Graph Preview */}
          {showPreview && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-3"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-700">Interactive Graph Preview</h3>
                {loadingStats && (
                  <span className="text-xs text-slate-500 animate-pulse">Loading stats...</span>
                )}
              </div>
              
              <InteractiveGraph 
                edges={edges} 
                isOptimized={false}
              />
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-xs text-blue-700 font-medium">
                  💡 <strong>Tip:</strong> Drag nodes to rearrange • Scroll to zoom • Click and drag background to pan
                </p>
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
    </motion.section>
  )
}

export default InputSection

