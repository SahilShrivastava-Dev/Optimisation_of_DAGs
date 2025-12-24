import { useEffect, useRef } from 'react'
import { Network } from 'vis-network'
import { DataSet } from 'vis-data'
import { Edge as GraphEdge } from '../types'

interface InteractiveGraphProps {
  edges: GraphEdge[]
  title?: string
  isOptimized?: boolean
}

const InteractiveGraph = ({ edges, title, isOptimized = false }: InteractiveGraphProps) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const networkRef = useRef<Network | null>(null)

  useEffect(() => {
    if (!containerRef.current || edges.length === 0) return

    // Extract unique nodes from edges
    const nodeSet = new Set<string>()
    edges.forEach(edge => {
      nodeSet.add(edge.source)
      nodeSet.add(edge.target)
    })

    // Create nodes dataset
    const nodes = new DataSet(
      Array.from(nodeSet).map(nodeId => ({
        id: nodeId,
        label: nodeId,
        shape: 'dot',
        size: 20,
        color: {
          background: isOptimized ? '#10b981' : '#3b82f6',
          border: isOptimized ? '#059669' : '#2563eb',
          highlight: {
            background: isOptimized ? '#059669' : '#2563eb',
            border: isOptimized ? '#047857' : '#1d4ed8',
          },
          hover: {
            background: isOptimized ? '#34d399' : '#60a5fa',
            border: isOptimized ? '#10b981' : '#3b82f6',
          }
        },
        font: {
          color: '#1e293b',
          size: 14,
          face: 'Inter, Arial',
          bold: {
            color: '#1e293b',
            size: 14,
            face: 'Inter, Arial',
          }
        },
        shadow: {
          enabled: true,
          color: 'rgba(0,0,0,0.2)',
          size: 10,
          x: 2,
          y: 2
        }
      }))
    )

    // Create edges dataset with class-based coloring
    const visEdges = new DataSet(
      edges.map((edge, index) => {
        const classes = edge.classes || []
        let color = '#3b82f6' // default blue
        
        if (classes.includes('Modify')) {
          color = '#ec4899' // pink/magenta
        } else if (classes.includes('Call_by')) {
          color = '#6b7280' // gray
        }

        return {
          id: index,
          from: edge.source,
          to: edge.target,
          arrows: {
            to: {
              enabled: true,
              scaleFactor: 0.8,
            }
          },
          color: {
            color: color,
            highlight: color,
            hover: color,
            opacity: 0.8
          },
          width: 2,
          smooth: {
            enabled: true,
            type: 'dynamic',
            roundness: 0.5
          },
          shadow: {
            enabled: true,
            color: 'rgba(0,0,0,0.1)',
            size: 5,
            x: 1,
            y: 1
          }
        }
      })
    )

    // Network options with physics
    const options = {
      nodes: {
        borderWidth: 3,
        borderWidthSelected: 4,
      },
      edges: {
        smooth: {
          enabled: true,
          type: 'dynamic',
          roundness: 0.5
        }
      },
      physics: {
        enabled: true,
        stabilization: {
          enabled: true,
          iterations: 200,
          updateInterval: 25
        },
        barnesHut: {
          gravitationalConstant: -8000,
          centralGravity: 0.3,
          springLength: 150,
          springConstant: 0.04,
          damping: 0.09,
          avoidOverlap: 0.5
        },
        maxVelocity: 50,
        minVelocity: 0.1,
        solver: 'barnesHut',
        timestep: 0.5,
        adaptiveTimestep: true
      },
      interaction: {
        dragNodes: true,
        dragView: true,
        zoomView: true,
        hover: true,
        multiselect: false,
        navigationButtons: false,
        keyboard: {
          enabled: false
        },
        tooltipDelay: 200,
      },
      layout: {
        improvedLayout: true,
        hierarchical: false
      }
    }

    // Create network
    const network = new Network(
      containerRef.current,
      { nodes, edges: visEdges },
      options
    )

    networkRef.current = network

    // Add event listeners
    network.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0]
        console.log('Node clicked:', nodeId)
      }
    })

    network.on('stabilizationIterationsDone', () => {
      network.setOptions({ physics: { enabled: true } })
    })

    // Fit to screen after stabilization
    network.once('stabilizationIterationsDone', () => {
      network.fit({
        animation: {
          duration: 1000,
          easingFunction: 'easeInOutQuad'
        }
      })
    })

    // Cleanup
    return () => {
      if (networkRef.current) {
        networkRef.current.destroy()
        networkRef.current = null
      }
    }
  }, [edges, isOptimized])

  return (
    <div className="space-y-3">
      {title && (
        <h4 className={`text-lg font-bold bg-gradient-to-r ${
          isOptimized 
            ? 'from-green-600 to-emerald-600' 
            : 'from-blue-600 to-cyan-600'
        } bg-clip-text text-transparent`}>
          {title}
        </h4>
      )}
      
      <div className="relative rounded-xl overflow-hidden bg-gradient-to-br from-slate-50 to-slate-100 border-2 border-slate-200 shadow-inner">
        <div 
          ref={containerRef} 
          className="w-full"
          style={{ height: '500px' }}
        />
        
        {/* Interactive hints */}
        <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-lg shadow-lg border border-slate-200">
          <p className="text-xs text-slate-600 font-medium">
            🖱️ Drag nodes • 🔍 Scroll to zoom • ✋ Pan to move
          </p>
        </div>
      </div>

      {edges.length > 0 && (
        <p className="text-sm text-slate-600 text-center">
          {Array.from(new Set(edges.flatMap(e => [e.source, e.target]))).length} nodes • {edges.length} edges
        </p>
      )}
    </div>
  )
}

export default InteractiveGraph

