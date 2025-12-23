import { motion } from 'framer-motion'
import { Download, Maximize2, Image } from 'lucide-react'
import { OptimizationResult } from '../types'
import { useState } from 'react'

interface GraphVisualizationProps {
  result: OptimizationResult
}

const GraphVisualization = ({ result }: GraphVisualizationProps) => {
  const [fullscreen, setFullscreen] = useState<'original' | 'optimized' | null>(null)

  const downloadImage = (base64: string, filename: string) => {
    const link = document.createElement('a')
    link.href = `data:image/png;base64,${base64}`
    link.download = filename
    link.click()
  }

  const GraphCard = ({ 
    title, 
    base64, 
    type,
    gradient 
  }: { 
    title: string
    base64: string
    type: 'original' | 'optimized'
    gradient: string
  }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-morphism p-6 rounded-2xl space-y-4"
    >
      <div className="flex items-center justify-between">
        <h4 className={`text-xl font-bold bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}>
          {title}
        </h4>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setFullscreen(type)}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            title="View fullscreen"
          >
            <Maximize2 className="w-5 h-5 text-slate-600" />
          </button>
          <button
            onClick={() => downloadImage(base64, `${type}-graph.png`)}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            title="Download image"
          >
            <Download className="w-5 h-5 text-slate-600" />
          </button>
        </div>
      </div>

      <div className="relative rounded-xl overflow-hidden bg-white border border-slate-200 shadow-inner">
        <img
          src={`data:image/png;base64,${base64}`}
          alt={title}
          className="w-full h-auto"
        />
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-600">
          {result[type].metrics.num_nodes} nodes, {result[type].metrics.num_edges} edges
        </span>
      </div>
    </motion.div>
  )

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-pink-100 rounded-lg">
            <Image className="w-6 h-6 text-pink-600" />
          </div>
          <h3 className="text-2xl font-bold text-slate-800">Graph Visualization</h3>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <GraphCard
            title="Original Graph"
            base64={result.original.visualization}
            type="original"
            gradient="from-blue-600 to-cyan-600"
          />
          <GraphCard
            title="Optimized Graph"
            base64={result.optimized.visualization}
            type="optimized"
            gradient="from-green-600 to-emerald-600"
          />
        </div>
      </motion.div>

      {/* Fullscreen Modal */}
      {fullscreen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-8"
          onClick={() => setFullscreen(null)}
        >
          <div className="relative max-w-6xl w-full">
            <button
              onClick={() => setFullscreen(null)}
              className="absolute -top-12 right-0 text-white hover:text-slate-300 text-lg font-semibold"
            >
              Close ✕
            </button>
            <img
              src={`data:image/png;base64,${result[fullscreen].visualization}`}
              alt={`${fullscreen} graph`}
              className="w-full h-auto rounded-xl shadow-2xl"
            />
          </div>
        </motion.div>
      )}
    </>
  )
}

export default GraphVisualization

