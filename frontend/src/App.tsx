import { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import Header from './components/Header'
import InputSection from './components/InputSection'
import OptimizationPanel from './components/OptimizationPanel'
import ResultsSection from './components/ResultsSection'
import { Edge, OptimizationResult } from './types'

function App() {
  const [edges, setEdges] = useState<Edge[]>([])
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen pb-20">
      <Toaster 
        position="top-right"
        toastOptions={{
          className: 'glass-morphism',
          duration: 3000,
        }}
      />
      
      <Header />
      
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="space-y-8">
          {/* Input Section */}
          <InputSection 
            edges={edges}
            setEdges={setEdges}
            loading={loading}
          />
          
          {/* Optimization Panel */}
          {edges.length > 0 && (
            <OptimizationPanel
              edges={edges}
              setResult={setResult}
              loading={loading}
              setLoading={setLoading}
            />
          )}
          
          {/* Results Section */}
          {result && (
            <ResultsSection result={result} />
          )}
        </div>
      </main>
    </div>
  )
}

export default App

