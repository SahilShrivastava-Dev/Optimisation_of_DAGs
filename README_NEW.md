# 🚀 DAG Optimizer - Modern React Application

A beautiful, minimalist web application for optimizing Directed Acyclic Graphs (DAGs) with a modern React frontend and FastAPI backend.

![DAG Optimizer](https://img.shields.io/badge/version-2.0.0-blue.svg)
![React](https://img.shields.io/badge/React-18.2-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178c6.svg)

## ✨ Features

### 🎨 Beautiful Minimalist UI
- **Glass-morphism design** with smooth animations
- **Responsive layout** that works on all devices
- **Dark gradient backgrounds** with modern aesthetics
- **Framer Motion animations** for fluid interactions

### 📊 Graph Optimization
- **Transitive Reduction**: Remove redundant edges while preserving reachability
- **Node Merging**: Combine equivalent nodes with identical parents/children
- **Cycle Detection**: Automatic cycle detection and optional removal
- **Real-time Metrics**: Compare original vs optimized graphs

### 📈 Advanced Metrics
- Node and edge counts
- Graph depth and width
- Cyclomatic complexity
- Degree distribution and entropy
- Graph density
- Longest/shortest path lengths

### 🔄 Multiple Input Methods
1. **Upload CSV/Excel files** - Drag & drop or browse
2. **Paste edge list** - Direct text input
3. **Generate random DAG** - Configurable node count and edge probability

### 🎯 Export Options
- **JSON metadata** download
- **PNG visualizations** download
- **Neo4j database** integration
- **Full-screen graph viewing**

## 🏗️ Architecture

```
dag-optimizer/
├── backend/                 # FastAPI backend
│   ├── main.py             # API endpoints
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Header.tsx
│   │   │   ├── InputSection.tsx
│   │   │   ├── OptimizationPanel.tsx
│   │   │   ├── ResultsSection.tsx
│   │   │   ├── MetricsComparison.tsx
│   │   │   ├── GraphVisualization.tsx
│   │   │   └── Neo4jExport.tsx
│   │   ├── App.tsx        # Main application
│   │   ├── main.tsx       # Entry point
│   │   ├── types.ts       # TypeScript types
│   │   └── index.css      # Global styles
│   ├── package.json
│   └── vite.config.ts
│
└── src/                    # Original Python modules
    ├── dag_optimiser/
    └── algo/
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 18+**
- **npm or yarn**

### Installation

#### 1. Clone the repository
```bash
git clone <your-repo-url>
cd "Optimisation of DAGs"
```

#### 2. Set up the Backend
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Note: You may need to install graphviz separately
# On Windows: download from https://graphviz.org/download/
# On macOS: brew install graphviz
# On Ubuntu: sudo apt-get install graphviz graphviz-dev
```

#### 3. Set up the Frontend
```bash
cd frontend
npm install
# or
yarn install
```

### Running the Application

#### Terminal 1 - Backend (FastAPI)
```bash
# From project root
cd backend
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on `http://localhost:8000`

#### Terminal 2 - Frontend (React)
```bash
# From project root
cd frontend
npm run dev
# or
yarn dev
```

The frontend will start on `http://localhost:5173`

### Access the Application
Open your browser and navigate to:
```
http://localhost:5173
```

## 📖 Usage Guide

### 1. Input Your Graph

**Option A: Upload File**
- Click on the "Upload File" tab
- Drag & drop or browse for a CSV/Excel file
- File should have columns: `source`, `target`, and optionally `classes`

**Option B: Paste Edges**
- Click on the "Paste Edges" tab
- Enter edges in format: `source,target,classes` (one per line)
- Click "Build DAG"

**Option C: Generate Random**
- Click on the "Random DAG" tab
- Adjust sliders for node count and edge probability
- Click "Generate Random DAG"

### 2. Configure Optimization

Choose your optimization options:
- ✅ **Transitive Reduction**: Remove redundant transitive edges
- ✅ **Merge Equivalent Nodes**: Combine nodes with same neighbors
- ⚠️ **Cycle Handling**: Show error or auto-remove cycles

### 3. Optimize

Click the **"Optimize Graph"** button to run the optimization

### 4. View Results

- **Improvement Stats**: See how many nodes/edges were reduced
- **Metrics Comparison**: Detailed table comparing all metrics
- **Visualizations**: Side-by-side comparison of original and optimized graphs

### 5. Export

- **Download JSON**: Get complete metadata
- **Download Images**: Save visualizations as PNG
- **Push to Neo4j**: Export to Neo4j graph database

## 🎨 Design Philosophy

### Minimalist Aesthetics
- Clean, uncluttered interface
- Generous whitespace
- Clear visual hierarchy
- Subtle animations

### Polymorphic Design
- Glass-morphism effects
- Gradient accents
- Smooth transitions
- Adaptive layouts

### Modern Tech Stack
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lucide Icons** for iconography
- **FastAPI** for high-performance backend

## 🔧 API Endpoints

### POST `/api/validate`
Validate if input forms a valid DAG

### POST `/api/optimize`
Optimize a DAG with specified options

### POST `/api/random-dag`
Generate a random DAG

### POST `/api/parse-csv`
Parse uploaded CSV/Excel file

### POST `/api/neo4j/push`
Push graph to Neo4j database

### GET `/health`
Health check endpoint

## 🐛 Troubleshooting

### Backend Issues

**Graphviz not found**
```bash
# Install graphviz system package
# Windows: Download from https://graphviz.org/download/
# macOS: brew install graphviz
# Ubuntu: sudo apt-get install graphviz graphviz-dev

# Then reinstall pygraphviz
pip install --force-reinstall pygraphviz
```

**Port 8000 already in use**
```bash
# Change port in backend/main.py or use different port
uvicorn main:app --reload --port 8001
```

### Frontend Issues

**Port 5173 already in use**
```bash
# Vite will automatically try the next available port
# Or specify a different port in vite.config.ts
```

**Module not found errors**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 🌟 Key Features Highlights

### 1. Real-time Graph Optimization
Optimize DAGs in seconds with visual feedback

### 2. Comprehensive Metrics
Track 10+ different graph metrics before and after optimization

### 3. Beautiful Visualizations
High-quality graph layouts using Graphviz

### 4. Neo4j Integration
Seamlessly export your graphs to Neo4j

### 5. Responsive Design
Works perfectly on desktop, tablet, and mobile

## 🔮 Future Enhancements

- [ ] Interactive graph editing
- [ ] Undo/redo functionality
- [ ] Graph comparison mode
- [ ] Custom optimization algorithms
- [ ] Batch processing
- [ ] Graph templates library
- [ ] Collaborative editing
- [ ] Cloud storage integration

## 📝 License

This project is part of research on DAG optimization.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Built with ❤️ using React, TypeScript, FastAPI, and modern web technologies**

