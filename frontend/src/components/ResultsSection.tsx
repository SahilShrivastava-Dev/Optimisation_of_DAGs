import { motion } from 'framer-motion'
import { Download, Database, TrendingDown, BarChart, FlaskConical, FileText, Loader2 } from 'lucide-react'
import { OptimizationResult } from '../types'
import MetricsComparison from './MetricsComparison'
import GraphVisualization from './GraphVisualization'
import Neo4jExport from './Neo4jExport'
import ResearchInsights from './ResearchInsights'
import { useState } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

interface ResultsSectionProps {
  result: OptimizationResult
}

const ResultsSection = ({ result }: ResultsSectionProps) => {
  const [showNeo4j, setShowNeo4j] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'research'>('overview')
  const [generatingReport, setGeneratingReport] = useState(false)

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

  const downloadResearchReport = async () => {
    setGeneratingReport(true)
    const toastId = toast.loading('Generating research report...')

    try {
      // Prepare the data (we need the original edges to re-run optimization)
      const requestData = {
        edges: result.original.edges,
        transitive_reduction: true,
        merge_nodes: true,
        handle_cycles: "remove"
      }

      const response = await axios.post('/api/export-research-report', requestData, {
        responseType: 'blob',
        timeout: 60000
      })

      // Create download link
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // Extract filename from Content-Disposition header or use default
      const contentDisposition = response.headers['content-disposition']
      let filename = 'DAG_Optimization_Research_Report.docx'
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '')
        }
      }
      
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.success('Research report downloaded!', { id: toastId })
    } catch (error: any) {
      console.error('Error downloading research report:', error)
      toast.error('Failed to generate research report', { id: toastId })
    } finally {
      setGeneratingReport(false)
    }
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
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <TrendingDown className="w-6 h-6 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-white">Optimization Results</h2>
            </div>
            
            {/* Tab Switcher */}
            <div className="flex items-center bg-slate-800/50 rounded-xl p-1">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  activeTab === 'overview'
                    ? 'bg-blue-500 text-white shadow-lg'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <BarChart className="w-4 h-4 inline mr-2" />
                Overview
              </button>
              <button
                onClick={() => setActiveTab('research')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  activeTab === 'research'
                    ? 'bg-purple-500 text-white shadow-lg'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <FlaskConical className="w-4 h-4 inline mr-2" />
                Research Analysis
              </button>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={downloadJSON}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded-xl font-semibold text-white flex items-center space-x-2 transition-all"
            >
              <Download className="w-4 h-4" />
              <span>Export JSON</span>
            </button>
            
            <button
              onClick={downloadResearchReport}
              disabled={generatingReport}
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-xl font-semibold flex items-center space-x-2 hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generatingReport ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <FileText className="w-4 h-4" />
              )}
              <span>{generatingReport ? 'Generating...' : 'Research Report'}</span>
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
            className="bg-gradient-to-br from-green-900/40 to-emerald-900/40 p-6 rounded-xl border border-green-700/50"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-300">Nodes Reduced</p>
                <p className="text-3xl font-bold text-green-400 mt-1">
                  {result.original.metrics.num_nodes} → {result.optimized.metrics.num_nodes}
                </p>
              </div>
              <div className="text-right">
                <div className="inline-flex items-center px-3 py-1 bg-green-500/20 rounded-full">
                  <TrendingDown className="w-4 h-4 text-green-400 mr-1" />
                  <span className="text-sm font-bold text-green-300">{improvement.nodes}%</span>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-blue-900/40 to-indigo-900/40 p-6 rounded-xl border border-blue-700/50"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-300">Edges Reduced</p>
                <p className="text-3xl font-bold text-blue-400 mt-1">
                  {result.original.metrics.num_edges} → {result.optimized.metrics.num_edges}
                </p>
              </div>
              <div className="text-right">
                <div className="inline-flex items-center px-3 py-1 bg-blue-500/20 rounded-full">
                  <TrendingDown className="w-4 h-4 text-blue-400 mr-1" />
                  <span className="text-sm font-bold text-blue-300">{improvement.edges}%</span>
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

      {/* Conditional Content Based on Active Tab */}
      {activeTab === 'overview' ? (
        <>
          {/* Metrics Comparison */}
          <MetricsComparison result={result} />

          {/* Graph Visualizations */}
          <GraphVisualization result={result} />
        </>
      ) : (
        <>
          {/* Research Insights */}
          <ResearchInsights 
            originalMetrics={result.original.metrics}
            optimizedMetrics={result.optimized.metrics}
          />
          
          {/* Graph Visualizations (also shown in research tab) */}
          <GraphVisualization result={result} />
        </>
      )}
    </motion.section>
  )
}

export default ResultsSection

