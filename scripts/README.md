# 🚀 DAG Optimizer - Demo Scripts

This folder contains comprehensive demonstration scripts showcasing all features of the DAG Optimizer library.

## 📚 Demo Scripts (Run These!)

### 1. **01_quick_start_demo.py**
**Purpose:** Complete introduction to the library with hands-on examples

**What it demonstrates:**
- ✅ Basic transitive reduction
- ✅ ML pipeline optimization
- ✅ PERT/CPM critical path analysis
- ✅ Layer-based parallelism analysis
- ✅ Edge criticality classification
- ✅ Comprehensive metrics comparison (25+ metrics)
- ✅ Visualization generation
- ✅ Metadata export

**How to run:**
```bash
cd scripts
python 01_quick_start_demo.py
```

**Output:**
- Terminal: Detailed explanations and results
- Files: `dag_comparison.png`, `optimization_metadata.json`

**Recommended for:** New users, learning the library

---

### 2. **02_benchmark_analysis.py**
**Purpose:** Performance analysis on 995 real DAG test cases

**What it demonstrates:**
- ✅ Loading dataset metadata (1000 DAGs)
- ✅ Loading benchmark results
- ✅ Edge reduction analysis by category
- ✅ Processing time analysis
- ✅ Parallelization benefits calculation
- ✅ Density correlation analysis
- ✅ Research paper claims validation
- ✅ Statistical visualizations

**How to run:**
```bash
cd scripts
python 02_benchmark_analysis.py
```

**Requirements:**
- `../DAG_Dataset/` folder with test DAGs
- `../Benchmark_Results/` folder with benchmark data

**Output:**
- Terminal: Comprehensive statistical analysis
- Files: `benchmark_analysis.png` (4 charts)

**Recommended for:** Researchers, performance evaluation

---

### 3. **03_metrics_explained.py**
**Purpose:** Detailed explanation of all 25+ metrics with examples

**What it demonstrates:**
- ✅ Basic metrics (nodes, edges, density, leaf nodes, depth)
- ✅ Path metrics (longest/shortest/average path, diameter)
- ✅ Complexity metrics (cyclomatic, topological, degree distribution/entropy)
- ✅ Efficiency metrics (redundancy ratio, compactness, efficiency score)
- ✅ PERT/CPM formulas and interpretation
- ✅ Layer analysis formulas and interpretation
- ✅ Edge criticality formulas and interpretation
- ✅ Real ML pipeline example with all metrics

**How to run:**
```bash
cd scripts
python 03_metrics_explained.py
```

**Output:**
- Terminal: Detailed metric explanations with formulas
- Mathematical formulas for each metric
- Interpretation guidelines
- Use case examples

**Recommended for:** Deep understanding, research applications

---

## 🛠️ Utility Scripts (Internal Use)

### **benchmark_dags.py**
Runs comprehensive benchmark on dataset. Creates `Benchmark_Results/` folder.

### **generate_challenges_doc.py**
Generates `Challenges_Faced.docx` document.

### **generate_documentation.py**
Generates `DAG_Optimizer_Complete_Guide.docx`.

### **generate_research_paper_pip.py**
Generates ML-focused research paper.

---

## 📦 Publishing Scripts (PyPI Deployment)

### **build_package.py**
**Purpose:** Automates package building for PyPI deployment

**What it does:**
- ✅ Cleans old builds (dist/, build/, *.egg-info)
- ✅ Verifies required files (setup.py, README.md, etc.)
- ✅ Checks build dependencies (build, twine)
- ✅ Builds distribution packages (.tar.gz, .whl)
- ✅ Validates packages with twine

**How to run:**
```bash
python scripts/build_package.py
```

**Output:**
- `dist/dagoptimizer-1.0.0.tar.gz` (source distribution)
- `dist/dagoptimizer-1.0.0-py3-none-any.whl` (wheel distribution)

---

### **publish_package.py**
**Purpose:** Interactive script to upload package to PyPI

**What it does:**
- ✅ Checks for built distributions
- ✅ Shows files to be uploaded
- ✅ Confirms with user before uploading
- ✅ Uploads to TestPyPI or PyPI
- ✅ Provides next steps and verification

**How to run:**
```bash
# Test upload (TestPyPI)
python scripts/publish_package.py --test

# Production upload (PyPI)
python scripts/publish_package.py
```

**Requirements:**
- PyPI account and API token
- Built package (run build_package.py first)

---

### **quick_publish.py**
**Purpose:** One-command build and publish

**What it does:**
- ✅ Builds package (runs build_package.py)
- ✅ Optionally publishes (runs publish_package.py)
- ✅ Handles complete workflow

**How to run:**
```bash
# Build only
python scripts/quick_publish.py

# Build + test upload
python scripts/quick_publish.py --test

# Build + production upload
python scripts/quick_publish.py --prod
```

**Recommended for:** Quick iterations, CI/CD pipelines

---

## 📋 Running All Demos

### Quick Test (1-2 minutes)
```bash
cd scripts
python 01_quick_start_demo.py
```

### Full Analysis (requires dataset, 3-5 minutes)
```bash
cd scripts
python 01_quick_start_demo.py
python 02_benchmark_analysis.py
python 03_metrics_explained.py
```

---

## 📊 Expected Output

### **01_quick_start_demo.py**
```
================================================================================
  DAG OPTIMIZER - QUICK START DEMONSTRATION
================================================================================

================================================================================
  EXAMPLE 1: Basic Transitive Reduction
================================================================================

Original edges:
  A → B
  B → C
  A → C
  C → D
  B → D

📊 Original graph: 5 nodes, 5 edges

✅ Optimized graph: 5 nodes, 3 edges
   Algorithm used: DFS-based TR (sparse graph)

📉 Edge reduction: 40.0%
   Removed 2 redundant edges

[... more examples ...]
```

### **02_benchmark_analysis.py**
```
================================================================================
  DAG OPTIMIZER - BENCHMARK ANALYSIS
================================================================================

================================================================================
  LOADING DATASET
================================================================================

✅ Loaded dataset metadata
   Generated at: 2025-12-28T19:55:52
   Total graphs: 1000

📊 Dataset Distribution:
   sparse_small         200 graphs
   sparse_medium        200 graphs
   [...]

================================================================================
  EDGE REDUCTION ANALYSIS
================================================================================

📊 Edge Reduction by Category:

Category             Count     Mean     Std     Min     Max
----------------------------------------------------------------------
dense_medium           100    86.9%   10.2%   65.0%   95.0%
[...]
```

### **03_metrics_explained.py**
```
================================================================================
  DAG OPTIMIZER - COMPREHENSIVE METRICS GUIDE
================================================================================

================================================================================
  SECTION 1: BASIC METRICS
================================================================================

📊 Number of Nodes (V)
────────────────────────────────────────────────────────────────────────────

🔢 Formula: V = |V|

📝 Explanation:
   The total count of vertices (nodes) in the graph.
   Each node represents a task, state, or entity in your DAG.

💡 Interpretation:
   [...]
```

---

## 🎯 Learning Path

**Beginner:**
1. Start with `01_quick_start_demo.py`
2. Read terminal output carefully
3. Check generated visualizations

**Intermediate:**
1. Run `03_metrics_explained.py`
2. Understand each metric's formula
3. Apply to your own DAGs

**Advanced:**
1. Run `02_benchmark_analysis.py`
2. Analyze statistical results
3. Validate research claims
4. Contribute benchmarks

---

## 📦 Dependencies

All demo scripts require:
```bash
pip install -e ..
```

For benchmark analysis:
```bash
pip install pandas matplotlib numpy
```

---

## 🔧 Troubleshooting

### Import Error
```
ModuleNotFoundError: No module named 'dagoptimizer'
```

**Solution:**
```bash
cd ..
pip install -e .
cd scripts
```

### Dataset Not Found
```
❌ Dataset not found at: ../DAG_Dataset/dataset_metadata.json
```

**Solution:** The benchmark analysis requires the test dataset. If you don't have it, focus on scripts 01 and 03 which work standalone.

### Visualization Error
```
RuntimeError: Invalid DISPLAY variable
```

**Solution:** The scripts save visualizations to files, so this won't affect functionality. Images are saved even if display fails.

---

## 📚 Documentation

- **Main README:** `../README.md`
- **API Documentation:** `../docs/PIP_PACKAGE_GUIDE.md`
- **Research Paper:** `../Research Papers/DAG_Optimization_ML_Workflows.docx`
- **Quick Start:** `../docs/QUICK_START.md`

---

## 🤝 Contributing

Want to add more demos?

1. Create a new script: `04_your_demo.py`
2. Follow the existing structure:
   - Docstring explaining purpose
   - Helper functions with docstrings
   - Clear terminal output
   - Section headers
3. Update this README
4. Test thoroughly

---

## 📄 License

MIT License - See `../LICENSE`

---

## 👤 Author

**Sahil Shrivastava**  
Email: sahilshrivastava28@gmail.com  
GitHub: [@SahilShrivastava-Dev](https://github.com/SahilShrivastava-Dev)

---

**Happy optimizing!** 🚀
