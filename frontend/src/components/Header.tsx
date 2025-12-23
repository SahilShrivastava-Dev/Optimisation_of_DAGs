import { motion } from 'framer-motion'
import { Network, Zap } from 'lucide-react'

const Header = () => {
  return (
    <header className="sticky top-0 z-50 glass-morphism border-b border-slate-200/50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="flex items-center justify-between h-20">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-4"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl blur-lg opacity-50 animate-pulse-slow"></div>
              <div className="relative bg-gradient-to-r from-blue-500 to-indigo-600 p-3 rounded-xl">
                <Network className="w-8 h-8 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                DAG Optimizer
              </h1>
              <p className="text-sm text-slate-500 font-medium">Minimize your directed acyclic graphs</p>
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="hidden md:flex items-center space-x-2 glass-morphism px-4 py-2 rounded-full"
          >
            <Zap className="w-4 h-4 text-amber-500" />
            <span className="text-sm font-semibold text-slate-700">Powered by AI</span>
          </motion.div>
        </div>
      </div>
    </header>
  )
}

export default Header

