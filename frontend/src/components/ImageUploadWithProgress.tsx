import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, X, Loader2, Sparkles, CheckCircle } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

interface ImageUploadWithProgressProps {
  onEdgesExtracted: (edges: any[]) => void
  onBackendError?: (error: any) => void
}

type ProgressStage = 'idle' | 'uploading' | 'analyzing' | 'extracting' | 'validating' | 'complete'

const AI_MODELS = [
  { 
    value: 'google/gemma-3-4b-it:free', 
    label: 'Google Gemma 3 4B (Free)', 
    description: 'Fast & Free',
    tier: 'free'
  },
  { 
    value: 'nvidia/nemotron-nano-12b-v2-vl:free', 
    label: 'NVIDIA Nemotron Nano 12B (Free)', 
    description: 'Vision optimized, Free',
    tier: 'free'
  },
  { 
    value: 'qwen/qwen-2.5-vl-7b-instruct:free', 
    label: 'Qwen 2.5 VL 7B (Free)', 
    description: 'Vision-language, Free',
    tier: 'free'
  },
  { 
    value: 'google/gemma-3-4b-it', 
    label: 'Google Gemma 3 4B (Paid)', 
    description: 'Better quality',
    tier: 'paid'
  },
  { 
    value: 'google/gemma-3-12b-it', 
    label: 'Google Gemma 3 12B (Paid)', 
    description: 'Best quality',
    tier: 'paid'
  }
]

export default function ImageUploadWithProgress({ onEdgesExtracted, onBackendError }: ImageUploadWithProgressProps) {
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState<ProgressStage>('idle')
  const [isDragging, setIsDragging] = useState(false)
  const [selectedModel, setSelectedModel] = useState(AI_MODELS[0].value)

  const stageMessages = {
    idle: 'Drop image or click to upload',
    uploading: 'Uploading image...',
    analyzing: 'AI analyzing image structure...',
    extracting: 'Extracting nodes and edges...',
    validating: 'Validating graph structure...',
    complete: 'Extraction complete!'
  }

  const stageProgress = {
    idle: 0,
    uploading: 20,
    analyzing: 40,
    extracting: 70,
    validating: 90,
    complete: 100
  }

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file')
      return
    }

    setSelectedImage(file)
    
    // Create image preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    if (file) handleFileSelect(file)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFileSelect(file)
  }

  const clearImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    setProgress(0)
    setStage('idle')
  }

  const extractFromImage = async () => {
    if (!selectedImage) return

    try {
      // Stage 1: Uploading
      setStage('uploading')
      setProgress(stageProgress.uploading)

      const formData = new FormData()
      formData.append('file', selectedImage)

      // Stage 2: Analyzing
      setTimeout(() => {
        setStage('analyzing')
        setProgress(stageProgress.analyzing)
      }, 500)

      const response = await axios.post('/api/extract-from-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        params: { model: selectedModel },
        timeout: 60000
      })

      // Stage 3: Extracting
      setStage('extracting')
      setProgress(stageProgress.extracting)
      await new Promise(resolve => setTimeout(resolve, 500))

      const data = response.data

      if (data.success) {
        // Stage 4: Validating
        setStage('validating')
        setProgress(stageProgress.validating)
        await new Promise(resolve => setTimeout(resolve, 300))

        // Stage 5: Complete
        setStage('complete')
        setProgress(100)

        const extractedEdges = data.edges
        onEdgesExtracted(extractedEdges)
        
        toast.success(data.message, { duration: 3000 })
        const modelName = data.model || 'OpenRouter API'
        toast(`✨ Extracted using ${modelName}`, { icon: '🤖', duration: 3000 })

        // Reset after a delay
        setTimeout(() => {
          clearImage()
        }, 2000)
      } else {
        handleExtractionError(data)
      }
    } catch (error: any) {
      console.error('Image extraction error:', error)
      
      setStage('idle')
      setProgress(0)

      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error('Request timed out. Image might be too large or backend is slow.')
      } else if (error.response?.status === 500) {
        toast.error('Backend error. Check backend console for details.')
      } else {
        toast.error(error.response?.data?.message || 'Failed to extract graph from image')
      }

      if (onBackendError) {
        onBackendError({
          type: 'error',
          message: error.message
        })
      }
    }
  }

  const handleExtractionError = (data: any) => {
    setStage('idle')
    setProgress(0)

    const errorType = data.error || 'unknown'
    
    if (errorType === 'api_key_required') {
      toast.error('OpenRouter API key required')
      toast(
        <div className="space-y-2">
          <p className="font-semibold">To enable AI extraction:</p>
          <p className="text-xs">1. Get free API key: openrouter.ai/keys</p>
          <p className="text-xs">2. Set: OPENROUTER_API_KEY=your-key</p>
          <p className="text-xs">3. Restart backend</p>
          <p className="text-xs mt-2 text-green-400">✨ Free tier available!</p>
        </div>,
        { duration: 10000, icon: '🔑' }
      )
    } else {
      toast.error(data.message || 'Extraction failed')
      
      if (data.suggestion) {
        toast(data.suggestion, { icon: '💡', duration: 5000 })
      }
    }

    if (onBackendError) {
      onBackendError({ type: 'error', message: data.message })
    }
  }

  return (
    <div className="space-y-4">
      {/* AI Model Selector */}
      <div className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-xl p-4">
        <label className="block text-sm font-semibold text-white mb-3 flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span>Select AI Model</span>
        </label>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          disabled={stage !== 'idle'}
          className="w-full px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white 
                   focus:ring-2 focus:ring-purple-500 focus:border-transparent
                   disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <optgroup label="✨ Free Models (Recommended)">
            {AI_MODELS.filter(m => m.tier === 'free').map(model => (
              <option key={model.value} value={model.value}>
                {model.label} - {model.description}
              </option>
            ))}
          </optgroup>
          <optgroup label="💎 Premium Models">
            {AI_MODELS.filter(m => m.tier === 'paid').map(model => (
              <option key={model.value} value={model.value}>
                {model.label} - {model.description}
              </option>
            ))}
          </optgroup>
        </select>
        <p className="text-xs text-slate-300 mt-2">
          💡 Free models work great for most DAG diagrams. Premium models offer better accuracy for complex images.
        </p>
      </div>

      {/* Drop Zone / Image Preview */}
      <AnimatePresence mode="wait">
        {!imagePreview ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`
              relative border-2 border-dashed rounded-lg p-8
              transition-all duration-200 cursor-pointer
              ${isDragging 
                ? 'border-blue-500 bg-blue-500/10' 
                : 'border-gray-600 hover:border-gray-500 bg-gray-800/50'
              }
            `}
          >
            <input
              type="file"
              accept="image/*"
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            
            <div className="flex flex-col items-center justify-center space-y-3">
              <Upload className={`w-12 h-12 ${isDragging ? 'text-blue-500' : 'text-slate-300'}`} />
              <div className="text-center">
                <p className="text-lg font-medium text-white">
                  {isDragging ? 'Drop image here' : 'Upload DAG Image'}
                </p>
                <p className="text-sm text-slate-300 mt-1">
                  PNG, JPG, or WEBP • Max 10MB
                </p>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="preview"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative"
          >
            {/* Image Preview */}
            <div className="relative bg-gray-800 rounded-lg overflow-hidden">
              <img
                src={imagePreview}
                alt="DAG Preview"
                className="w-full h-auto max-h-96 object-contain"
              />
              
              {/* Remove button */}
              {stage === 'idle' && (
                <button
                  onClick={clearImage}
                  className="absolute top-2 right-2 p-2 bg-red-500/90 hover:bg-red-600 
                           rounded-full transition-colors"
                  title="Remove image"
                >
                  <X className="w-5 h-5 text-white" />
                </button>
              )}

              {/* Progress Overlay */}
              {stage !== 'idle' && stage !== 'complete' && (
                <div className="absolute inset-0 bg-black/60 backdrop-blur-sm 
                              flex items-center justify-center">
                  <div className="text-center space-y-4 px-4">
                    <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto" />
                    <div>
                      <p className="text-lg font-medium text-white">
                        {stageMessages[stage]}
                      </p>
                      <p className="text-sm text-white mt-1">
                        {progress}% complete
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Success Overlay */}
              {stage === 'complete' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="absolute inset-0 bg-green-500/20 backdrop-blur-sm 
                           flex items-center justify-center"
                >
                  <div className="text-center space-y-2">
                    <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
                    <p className="text-xl font-bold text-green-500">
                      {stageMessages.complete}
                    </p>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Progress Bar */}
            {stage !== 'idle' && (
              <div className="mt-4 space-y-2">
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5, ease: 'easeInOut' }}
                  />
                </div>
                
                <div className="flex items-center justify-between text-xs text-slate-300">
                  <span>{stageMessages[stage]}</span>
                  <span>{progress}%</span>
                </div>
              </div>
            )}

            {/* Extract Button */}
            {stage === 'idle' && (
              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                onClick={extractFromImage}
                className="mt-4 w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 
                         hover:from-blue-600 hover:to-purple-700 text-white font-medium rounded-lg 
                         transition-all duration-200 flex items-center justify-center space-x-2
                         shadow-lg hover:shadow-xl"
              >
                <Sparkles className="w-5 h-5" />
                <span>Extract Graph with AI</span>
              </motion.button>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Info */}
      <div className="text-xs text-slate-300 space-y-1">
        <p>💡 Upload a clear image of your DAG diagram</p>
        <p>🤖 AI will automatically detect nodes and edges</p>
        <p>⚡ Powered by OpenRouter's free vision models</p>
      </div>
    </div>
  )
}

