# 🚀 Advanced DAG Optimization Framework

<div align="center">

**A Research-Grade System for Directed Acyclic Graph Analysis and Optimization**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Features](#-features)** • **[Demo](#-demo)** • **[Installation](#-installation)** • **[Usage](#-usage)** • **[Research](#-research-paper)** • **[Documentation](#-documentation)**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [What Problem Does This Solve?](#-what-problem-does-this-solve)
- [Key Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Research Paper](#-research-paper)
- [Benchmark Results](#-benchmark-results)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Citation](#-citation)
- [License](#-license)

---

## 🎯 Overview

This project implements a **comprehensive DAG optimization framework** that combines classical graph algorithms with modern research-grade analysis techniques. It provides:

- **Advanced Transitive Reduction**: Adaptive algorithm selection based on graph density (DFS for sparse, matrix-based for dense)
- **PERT/CPM Critical Path Analysis**: Identifies bottlenecks, calculates slack times, and optimizes scheduling
- **Width & Parallelism Optimization**: Layer-based structure analysis for parallel execution
- **Edge Criticality Classification**: Distinguishes critical edges from redundant ones
- **13+ Research-Grade Metrics**: Comprehensive mathematical analysis of graph properties
- **AI-Powered Image Extraction**: Reconstruct DAGs from uploaded images using vision-language models

**Validated on 995 test cases** spanning 7 density categories, achieving **42.9% average edge reduction** while preserving 100% reachability.

---

## 💡 What Problem Does This Solve?

### The Challenge

In software engineering, build systems, CI/CD pipelines, and workflow management, **Directed Acyclic Graphs (DAGs)** are everywhere:

- **Build Systems**: Dependency graphs for compilation order
- **Task Schedulers**: Workflow execution plans (Airflow, Prefect)
- **Package Managers**: Dependency resolution (npm, pip, cargo)
- **CI/CD Pipelines**: Test and deployment ordering
- **Data Pipelines**: ETL/ELT processing workflows

Over time, these DAGs accumulate **redundant edges** (transitive dependencies), leading to:
- ❌ Increased complexity and maintenance burden
- ❌ Longer execution times and reduced parallelism
- ❌ Difficulty understanding critical paths and bottlenecks
- ❌ Wasted computational resources

### Our Solution

This framework provides:

1. **Automated Optimization**: Remove redundant edges while preserving all dependencies
2. **Critical Path Analysis**: Identify bottlenecks and optimize scheduling
3. **Parallelism Potential**: Calculate optimal parallel execution strategies
4. **Mathematical Insights**: 13+ metrics to understand graph efficiency
5. **Visual Analysis**: Interactive graph visualization and comparison
6. **Export Research Reports**: Generate comprehensive DOCX reports for stakeholders

**Real-World Impact** (based on 995-DAG benchmark):
- **68-87% edge reduction** for dense graphs (build systems, workflow managers)
- **40-75% reduction** for medium-density graphs (CI/CD pipelines)
- **Critical path identification** enables up to **3× parallelization** (PERT/CPM analysis)
- **Makespan reduction** from better scheduling (EST/LST optimization)

---

## ✨ Features

### 🔬 Core Optimization Algorithms

| Feature | Description | Impact |
|---------|-------------|--------|
| **Adaptive Transitive Reduction** | Density-aware algorithm selection (DFS/Matrix) | 42.9% avg edge reduction |
| **Node Equivalence Merging** | Merge nodes with identical dependencies | Simplifies graph structure |
| **Cycle Detection & Removal** | Ensures DAG property is maintained | 100% acyclicity guarantee |

### 📊 Research-Grade Analysis

| Category | Metrics | Purpose |
|----------|---------|---------|
| **PERT/CPM Analysis** | EST, LST, Slack, Critical Path, Makespan | Scheduling optimization |
| **Width Optimization** | DAG Width, Depth, Parallelism Potential | Parallel execution planning |
| **Edge Criticality** | Critical vs Redundant Edges, Criticality Ratio | Dependency prioritization |
| **Efficiency Metrics** | Efficiency Score, Redundancy Ratio, Compactness | Overall graph quality |
| **Structural Metrics** | Density, Complexity, Path Length, Diameter | Graph characterization |
| **Degree Analysis** | Avg/Max In/Out-Degree, Degree Entropy | Load distribution |

### 🎨 Modern Web Interface

- **Interactive Graph Visualization**: Neo4j-style physics-based rendering with `vis-network`
- **Real-Time Analysis**: Instant metric calculation and comparison
- **Progress Tracking**: Visual feedback for long-running operations
- **Dark Mode UI**: Beautiful carbon-grey minimalist design
- **Responsive Layout**: Works on desktop and tablet devices

### 🤖 AI-Powered Features

- **Image-to-DAG Extraction**: Upload a photo of a graph, AI reconstructs it
- **Multi-Model Support**: OpenRouter API with multiple free VLM options
- **Smart Parsing**: Handles hand-drawn, screenshots, or diagrammatic DAGs

### 📈 Export & Integration

- **Neo4j Export**: Push optimized graphs directly to Neo4j database
- **Research Reports**: Generate comprehensive DOCX reports with mathematical analysis
- **CSV/JSON Export**: Download graphs and metrics in standard formats
- **Reproducible Results**: All operations are deterministic and verifiable

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (TypeScript)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Input Section│  │Optimization  │  │  Results &   │      │
│  │ • CSV Upload │  │   Panel      │  │ Visualization│      │
│  │ • Paste Text │  │ • TR Toggle  │  │ • Interactive│      │
│  │ • Random Gen │  │ • NEM Toggle │  │ • Metrics    │      │
│  │ • AI Image   │  │ • Optimize   │  │ • Export     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                    FastAPI REST API
                            │
┌─────────────────────────────────────────────────────────────┐
│                   Python Backend (FastAPI)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              DAGOptimizer Core Engine                 │   │
│  │  • Adaptive Transitive Reduction (DFS/Matrix)        │   │
│  │  • Node Equivalence Merging                          │   │
│  │  • PERT/CPM Critical Path Analysis                   │   │
│  │  • Width & Layer Structure Optimization              │   │
│  │  • Edge Criticality Classification                   │   │
│  │  • 13+ Research-Grade Metrics Calculation            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          AI Image Extraction (OpenRouter)            │   │
│  │  • Vision-Language Model Integration                 │   │
│  │  • Multi-Model Support (Gemini, Llama, Qwen)        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Research Report Generator (python-docx)      │   │
│  │  • Comprehensive DOCX Reports                        │   │
│  │  • Mathematical Justifications                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
         Neo4j Database          OpenRouter API
      (Optional Export)      (AI Image Processing)
```

**Tech Stack**:
- **Frontend**: React 18, TypeScript, Tailwind CSS, Framer Motion, vis-network
- **Backend**: Python 3.8+, FastAPI, NetworkX, NumPy, SciPy
- **AI**: OpenRouter API (Gemini, Llama Vision, Qwen VL)
- **Database**: Neo4j (optional export)
- **Docs**: python-docx for research reports

---

## 📦 Installation

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** (for cloning)
- **Neo4j** (optional, for graph export)

### Option 1: Windows Quick Install (Recommended for Windows Users)

```batch
# Clone the repository
git clone https://github.com/YourUsername/dag-optimization-framework.git
cd dag-optimization-framework

# Run automated installer
install_dependencies.bat

# Start both backend and frontend
start_all.bat
```

### Option 2: Manual Installation

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up OpenRouter API key (for AI image extraction)
python setup_api_key.py

# Start the backend server
uvicorn main:app --reload --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the development server
npm run dev
```

### Option 3: Docker (Coming Soon)

```bash
docker-compose up
```

---

## 🚀 Quick Start

### 1. Start the Application

**Windows**:
```batch
start_all.bat
```

**Linux/Mac**:
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 2. Open Your Browser

Navigate to `http://localhost:5173`

### 3. Load a DAG

Choose one of four input methods:

#### Option A: Upload CSV File
```csv
source,target
A,B
A,C
B,D
C,D
```

#### Option B: Paste Edge List
```
A,B
A,C
B,D
C,D
A,D
```
*(Note: `A,D` is redundant via `A→B→D` and `A→C→D`)*

#### Option C: Generate Random DAG
- Set number of nodes (10-500)
- Set edge probability (0.1-0.5)
- Click "Generate Random DAG"

#### Option D: Upload Image
- Take a photo of a hand-drawn DAG
- Upload it via "Upload Image" tab
- AI will reconstruct the graph

### 4. Optimize the DAG

1. **Enable Optimization Options**:
   - ✅ **Transitive Reduction**: Remove redundant edges
   - ✅ **Merge Equivalent Nodes**: Combine identical dependencies

2. **Click "Optimize Graph"**

3. **View Results**:
   - **Overview Tab**: Metrics comparison, before/after graphs
   - **Research Analysis Tab**: Advanced mathematical insights

### 5. Export Results

- **Neo4j Export**: Push optimized graph to database
- **Research Report**: Download comprehensive DOCX report
- **CSV/JSON**: Export graph data for further analysis

---

## 📄 Research Paper

This framework is backed by rigorous academic research. The full paper is available in the [GitHub Wiki](#) and includes:

### Key Contributions

1. **Adaptive Transitive Reduction Algorithm**
   - Density-based algorithm selection (DFS for sparse, matrix for dense)
   - O(n·m) best case, O(n³) worst case
   - Validated on 995 test cases

2. **Integrated PERT/CPM Analysis**
   - Critical path identification with O(n + m) complexity
   - Earliest/Latest Start Times (EST/LST)
   - Slack time calculation for scheduling flexibility

3. **Width-Optimal Layer Decomposition**
   - DAG width and depth calculation
   - Parallelism potential estimation (W/D ratio)
   - Layer-based execution planning

4. **Edge Criticality Classification**
   - Distinguishes critical edges from redundant edges
   - Prioritizes dependencies for incremental updates
   - Criticality ratio as a graph quality metric

### Benchmark Results (995 DAGs Tested)

| Graph Category | Tested | Edge Reduction | Time Overhead | Density Range |
|----------------|--------|----------------|---------------|---------------|
| **Sparse Small** | 195 | 1.2% | 27× | 0.02-0.05 |
| **Sparse Medium** | 200 | 12.0% | 28× | 0.01-0.05 |
| **Sparse Large** | 100 | 16.5% | 30× | 0.005-0.03 |
| **Medium Small** | 150 | 40.5% | 25× | 0.1-0.3 |
| **Medium Medium** | 150 | 75.2% | 21× | 0.1-0.3 |
| **Dense Small** | 100 | 68.0% | 26× | 0.3-0.6 |
| **Dense Medium** | 100 | **86.9%** ⭐ | 22× | 0.3-0.5 |
| **Overall Average** | **995** | **42.9%** | **25.6×** | **0.005-0.6** |

**Key Findings**:
- ✅ **42.9% average edge reduction** across all graph types
- ⭐ **Dense graphs achieve 68-87% reduction** (best case: 86.9%)
- 📊 **25.6× time overhead for 5× feature count** (~17ms per feature)
- 🎯 **Exceeded expectations**: Dense-medium graphs surpassed predicted 80% max
- ✅ **99.5% success rate** on comprehensive benchmark

### Mathematical Formulations

See the [full research paper](../../wiki/Research-Paper) in the GitHub Wiki for detailed mathematical proofs and complexity analysis.

---

## 📊 Benchmark Results

We tested our framework on a comprehensive dataset of **1,000 synthetic DAGs** spanning:
- **Node Range**: 10-500 nodes
- **Density Range**: 0.005-0.6 (sparse to dense)
- **Categories**: 7 distinct density/size combinations

### Performance Summary

```
✅ 995 DAGs successfully processed (99.5% success rate)
⏱️  89.73 seconds total testing time
📉 42.9% average edge reduction
⚡ 25.6× overhead for 5× analytical features
```

### Detailed Results

See [`BENCHMARK_SUMMARY.md`](./BENCHMARK_SUMMARY.md) for:
- Category-by-category breakdown
- Statistical analysis
- Performance vs density correlation
- Scalability observations

---

## 📚 Documentation

### Core Documentation

| Document | Description |
|----------|-------------|
| **[docs/QUICK_START.md](./docs/QUICK_START.md)** | 5-minute setup guide |
| **[docs/ADVANCED_RESEARCH_FEATURES.md](./docs/ADVANCED_RESEARCH_FEATURES.md)** | Detailed feature documentation |
| **[docs/RESEARCH_FEATURES_SUMMARY.md](./docs/RESEARCH_FEATURES_SUMMARY.md)** | Quick reference for all metrics |
| **[docs/BENCHMARK_SUMMARY.md](./docs/BENCHMARK_SUMMARY.md)** | Full benchmark results and analysis |
| **[docs/REAL_NUMBERS_FOR_PAPER.md](./docs/REAL_NUMBERS_FOR_PAPER.md)** | Research paper data reference |

### Setup & Installation

| Document | Description |
|----------|-------------|
| **[docs/WINDOWS_INSTALL.md](./docs/WINDOWS_INSTALL.md)** | Windows-specific installation guide |
| **[docs/OPENROUTER_SETUP.md](./docs/OPENROUTER_SETUP.md)** | AI model configuration |

### Features & Upgrades

| Document | Description |
|----------|-------------|
| **[docs/INTERACTIVE_GRAPH_GUIDE.md](./docs/INTERACTIVE_GRAPH_GUIDE.md)** | Interactive visualization features |
| **[docs/IMAGE_UPLOAD_FEATURE.md](./docs/IMAGE_UPLOAD_FEATURE.md)** | AI image extraction documentation |
| **[docs/RESEARCH_REPORT_FEATURE.md](./docs/RESEARCH_REPORT_FEATURE.md)** | Exporting research reports |
| **[docs/MATHEMATICAL_FEATURES_ROADMAP.md](./docs/MATHEMATICAL_FEATURES_ROADMAP.md)** | Mathematical analysis documentation |

### Complete Documentation

See **[docs/README.md](./docs/README.md)** for the full documentation index.

### API Documentation

- **Backend API**: http://localhost:8000/docs (FastAPI auto-generated)
- **Frontend Components**: See `frontend/src/components/` with TypeScript types

---

## 🤝 Contributing

We welcome contributions! Please see:

1. **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Contribution guidelines
2. **[CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)** - Community standards
3. **[GitHub Issues](../../issues)** - Bug reports and feature requests
4. **[GitHub Discussions](../../discussions)** - Questions and ideas

### Development Setup

```bash
# Clone and install
git clone https://github.com/YourUsername/dag-optimization-framework.git
cd dag-optimization-framework

# Backend development
cd backend
pip install -r requirements.txt
pytest tests/  # Run tests

# Frontend development
cd frontend
npm install
npm run lint   # Lint code
npm run test   # Run tests
```

---

## 📖 Citation

If you use this framework in your research, please cite:

```bibtex
@software{shrivastava2025dag,
  author = {Shrivastava, Sahil},
  title = {Advanced DAG Optimization Framework: Adaptive Transitive Reduction with Integrated PERT/CPM Analysis},
  year = {2025},
  url = {https://github.com/YourUsername/dag-optimization-framework},
  note = {Validated on 995 benchmark cases with 42.9\% average edge reduction}
}
```

**Research Paper**: See the [GitHub Wiki](../../wiki/Research-Paper) for the full academic paper with mathematical proofs.

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](./LICENSE) file for details.

---

## 🌟 Acknowledgments

- **Research Papers**: This work builds on classical transitive reduction algorithms (Aho, Garey & Johnson) and modern DAG optimization techniques (see `Research Papers/` folder)
- **Libraries**: NetworkX, FastAPI, React, vis-network, and the open-source community
- **Inspiration**: Build systems (Bazel, Buck), workflow managers (Airflow, Prefect), and dependency resolvers (npm, cargo)

---

## 📬 Contact

**Author**: Sahil Shrivastava  
**Email**: sahilshrivastava28@gmail.com  
**GitHub**: [@YourUsername](https://github.com/YourUsername)

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

**[Report Bug](../../issues)** • **[Request Feature](../../issues)** • **[Documentation](../../wiki)**

Made with ❤️ for the graph optimization community

</div>
