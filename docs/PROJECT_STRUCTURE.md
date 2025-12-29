# 📁 Project Structure

This document provides a comprehensive overview of the Advanced DAG Optimization Framework's file organization.

---

## 🏗️ High-Level Structure

```
dag-optimization-framework/
├── 📂 backend/              # Python FastAPI backend
├── 📂 frontend/             # React TypeScript frontend
├── 📂 src/                  # Core optimization algorithms
├── 📂 docs/                 # Comprehensive documentation
├── 📂 utils/                # DAG generation utilities
├── 📂 notebooks/            # Jupyter notebooks (optional)
├── 📂 Research Papers/      # Academic references (gitignored)
├── 📂 DAG_Dataset/          # Benchmark test cases (gitignored)
├── 📂 Benchmark_Results/    # Test results (gitignored)
├── 📄 README.md             # Main project documentation
├── 📄 CONTRIBUTING.md       # Contribution guidelines
├── 📄 CODE_OF_CONDUCT.md    # Community standards
├── 📄 LICENSE               # MIT License
└── 📄 .gitignore            # Git exclusions
```

---

## 📂 Detailed Structure

### Backend (`backend/`)

Python FastAPI application and API logic.

```
backend/
├── main.py                        # FastAPI app entry point
├── image_dag_extractor.py        # AI image-to-DAG extraction
├── research_report_generator.py  # DOCX report generation
├── setup_api_key.py              # OpenRouter API key setup
├── requirements.txt              # Python dependencies
└── README.md                      # Backend-specific docs
```

**Key Files**:
- **`main.py`**: FastAPI routes (`/api/optimize`, `/api/export-research-report`, etc.)
- **`image_dag_extractor.py`**: Integrates OpenRouter API for vision-language models
- **`research_report_generator.py`**: Generates comprehensive DOCX reports using `python-docx`

### Frontend (`frontend/`)

React TypeScript application with Tailwind CSS.

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.tsx                   # App header
│   │   ├── InputSection.tsx             # DAG input interface
│   │   ├── OptimizationPanel.tsx        # Optimization controls
│   │   ├── ResultsSection.tsx           # Results display
│   │   ├── MetricsComparison.tsx        # Metrics table
│   │   ├── GraphVisualization.tsx       # Graph display wrapper
│   │   ├── InteractiveGraph.tsx         # vis-network integration
│   │   ├── ResearchInsights.tsx         # Advanced metrics display
│   │   ├── ImageUploadWithProgress.tsx  # Image upload with progress bar
│   │   └── Neo4jExport.tsx              # Neo4j database export
│   ├── App.tsx                          # Main React component
│   ├── main.tsx                         # React entry point
│   ├── index.css                        # Global styles (Tailwind)
│   ├── types.ts                         # TypeScript type definitions
│   └── vite-env.d.ts                    # Vite types
├── index.html                           # HTML template
├── package.json                         # Node dependencies
├── tsconfig.json                        # TypeScript config
├── vite.config.ts                       # Vite config
├── tailwind.config.js                   # Tailwind CSS config
└── postcss.config.js                    # PostCSS config
```

**Key Components**:
- **`InputSection.tsx`**: Handles CSV upload, text input, random generation, and AI image extraction
- **`InteractiveGraph.tsx`**: Neo4j-style interactive graph with physics simulation
- **`ResearchInsights.tsx`**: Displays 13+ research-grade metrics with mathematical formulas

### Core Algorithms (`src/`)

Core DAG optimization logic implemented in Python.

```
src/
├── dag_optimiser/
│   ├── __init__.py
│   └── dag_class.py          # DAGOptimizer class (main algorithm)
└── algo/
    ├── __init__.py
    ├── agutr_dfs.py          # DFS-based transitive reduction
    ├── agutr_fw.py           # Floyd-Warshall transitive reduction
    ├── no_tears_dag_optimisation.py  # NO TEARS algorithm
    └── ver_mrg_opt.py        # Vertex merging optimization
```

**Key Algorithms**:
- **`dag_class.py`**: 
  - `transitive_reduction()`: Adaptive algorithm (DFS for sparse, matrix for dense)
  - `compute_critical_path_with_slack()`: PERT/CPM analysis
  - `compute_layer_structure()`: Width and parallelism calculation
  - `compute_edge_criticality()`: Edge classification
  - `evaluate_graph_metrics()`: 13+ metrics calculation

### Documentation (`docs/`)

Comprehensive project documentation.

```
docs/
├── README.md                             # Documentation index
├── QUICK_START.md                        # 5-minute setup guide
├── QUICK_START_RESEARCH.md              # Research features guide
├── QUICK_START_REPORT_FEATURE.md        # Report generation guide
├── ADVANCED_RESEARCH_FEATURES.md        # Feature documentation
├── RESEARCH_FEATURES_SUMMARY.md         # Metrics reference
├── BENCHMARK_SUMMARY.md                 # 995-DAG benchmark results
├── REAL_NUMBERS_FOR_PAPER.md            # Research paper data
├── MATHEMATICAL_FEATURES_ROADMAP.md     # Mathematical analysis guide
├── WINDOWS_INSTALL.md                   # Windows installation
├── INSTALLATION_SUCCESS.md              # Troubleshooting
├── OPENROUTER_SETUP.md                  # AI model configuration
├── INTERACTIVE_GRAPH_GUIDE.md           # Interactive features
├── IMAGE_UPLOAD_FEATURE.md              # AI image extraction
├── RESEARCH_REPORT_FEATURE.md           # DOCX report export
├── FORMULA_HELP_FEATURE.md              # Formula tooltips
├── UI_DESIGN_OVERVIEW.md                # Design system
├── TRANSFORMATION_SUMMARY.md            # Migration history
├── RESEARCH_MODE_UPGRADE.md             # Research upgrade log
├── UPGRADE_TO_INTERACTIVE.md            # Interactive graph log
├── OPENROUTER_MIGRATION_SUMMARY.md      # AI API migration log
├── TRADEOFF_ANALYSIS_SUMMARY.md         # Algorithm tradeoffs
├── TEXT_COLOR_FIXES_SUMMARY.md          # UI fixes log
├── TOOLTIP_IMPROVEMENTS.md              # Tooltip UX log
├── IMAGE_UPLOAD_PROGRESS_FEATURE.md     # Progress bar log
├── DEBUG_IMAGE_UPLOAD.md                # Debug guide
├── QUICK_FIX_IMAGE_UPLOAD.md            # Quick fixes
├── FREE_AI_MODELS_GUIDE.md              # AI models list
└── LATEST_UPDATES.md                    # Recent changes
```

### Utilities (`utils/`)

Helper scripts for DAG generation.

```
utils/
├── random_dag_generator.py      # Random DAG generator
└── rdm_dag_tree_generator.py    # Tree-based DAG generator
```

### Research Assets (Git-Ignored)

These folders contain research materials not pushed to GitHub.

```
Research Papers/                  # Academic papers (gitignored)
├── DAG_Optimization_Sahil_Shrivastava.docx
├── DAGs with No Curl.pdf
├── DAGs with NO TEARS.pdf
├── Maintenance of transitive closures.pdf
├── On the calculation of transitive reduction.pdf
└── ...

DAG_Dataset/                      # 1000 synthetic DAGs (gitignored)
├── dag_0000.json
├── dag_0001.json
├── ...
├── dag_0999.json
└── dataset_metadata.json

Benchmark_Results/                # Test results (gitignored)
├── benchmark_results.json
└── paper_tables.txt
```

### Root Files

```
📄 README.md                         # Main project README
📄 CONTRIBUTING.md                   # Contribution guidelines
📄 CODE_OF_CONDUCT.md                # Community standards
📄 LICENSE                           # MIT License
📄 PROJECT_STRUCTURE.md              # This file
📄 GITHUB_WIKI_GUIDE.md              # GitHub Wiki setup guide
📄 DOCUMENTATION_README.md           # Documentation index
📄 .gitignore                        # Git exclusions
📄 app.py                            # Legacy Streamlit app (deprecated)
📄 requirements.txt                  # Root Python dependencies
📄 tradeoff.docx                     # Algorithm tradeoff analysis
📄 DAG_Optimizer_Complete_Guide.docx # Complete pip package guide
📄 Challenges_Faced.docx             # Challenges & solutions document
```


---

## 🔑 Key Entry Points

### For Users

1. **Start Application**: Start backend and frontend in separate terminals (see README.md)
2. **Read Documentation**: `README.md` → `docs/QUICK_START.md`
3. **Setup AI Models**: `docs/OPENROUTER_SETUP.md`

### For Developers

1. **Backend Development**: `backend/main.py` (FastAPI routes)
2. **Core Algorithms**: `src/dag_optimiser/dag_class.py`
3. **Frontend Components**: `frontend/src/components/`
4. **Type Definitions**: `frontend/src/types.ts`

### For Researchers

1. **Research Paper**: `Research Papers/DAG_Optimization_Sahil_Shrivastava.docx`
2. **Benchmark Data**: `docs/BENCHMARK_SUMMARY.md` + `docs/REAL_NUMBERS_FOR_PAPER.md`
3. **Algorithm Analysis**: `tradeoff.docx` + `docs/TRADEOFF_ANALYSIS_SUMMARY.md`

---

## 📦 Dependencies

### Backend (Python)

See `backend/requirements.txt`:
- **FastAPI**: Web framework
- **NetworkX**: Graph algorithms
- **NumPy/SciPy**: Numerical operations
- **python-docx**: DOCX generation
- **python-dotenv**: Environment variables
- **neo4j**: Database integration (optional)

### Frontend (Node.js)

See `frontend/package.json`:
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **vis-network**: Interactive graphs
- **Framer Motion**: Animations
- **Axios**: HTTP client

---

## 🚀 Build Process

### Development

```bash
# Backend
cd backend
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

### Production

```bash
# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npm run preview
```

---

## 📊 Data Flow

```
User Input (CSV/Text/Random/Image)
          ↓
  Frontend (React)
          ↓
  FastAPI Backend (/api/optimize)
          ↓
  DAGOptimizer (src/dag_optimiser/dag_class.py)
          ↓
  [Optimization Algorithms]
    - Transitive Reduction
    - Node Merging
    - PERT/CPM Analysis
    - Edge Criticality
          ↓
  Results (Metrics + Optimized Graph)
          ↓
  Frontend Display (Interactive Graph + Metrics)
          ↓
  Optional Exports:
    - Neo4j Database
    - DOCX Research Report
    - CSV/JSON Files
```

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `backend/.env` | OpenRouter API key, model selection |
| `.gitignore` | Files excluded from version control |
| `frontend/vite.config.ts` | Vite build configuration |
| `frontend/tailwind.config.js` | Tailwind CSS theme |
| `frontend/tsconfig.json` | TypeScript compiler options |
| `backend/requirements.txt` | Python dependencies |
| `frontend/package.json` | Node dependencies |

---

## 📝 Notes

- **Legacy Streamlit App**: `app.py` is the old Streamlit version, kept for reference
- **Research Papers**: Not included in Git due to copyright (add your own)
- **Generated Data**: Datasets and benchmarks are gitignored (regenerate with `benchmark_dags.py`)
- **Documentation**: Moved from root to `docs/` for better organization

---

## 🌟 Well-Organized Structure Benefits

✅ **Clear separation** between backend, frontend, and algorithms  
✅ **Comprehensive documentation** in dedicated folder  
✅ **Easy onboarding** with batch scripts and quick start guides  
✅ **Research reproducibility** with benchmark scripts and datasets  
✅ **Professional presentation** ready for GitHub showcase  

---

**This structure is designed for maximum clarity and ease of contribution!** 🚀

