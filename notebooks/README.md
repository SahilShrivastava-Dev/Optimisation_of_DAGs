# 📓 Jupyter Notebooks

Professional notebooks showcasing the DAG Optimizer library.

## Notebooks

### 1. **01_Quick_Start_Guide.ipynb**
Getting started with the library - installation, basic usage, and key features.

**Topics covered:**
- Installation
- Basic transitive reduction
- ML pipeline optimization example
- PERT/CPM critical path analysis
- Layer-based parallelism analysis
- Edge criticality classification
- Comprehensive metrics
- Visualization

**Recommended for:** New users, quick overview

---

### 2. **02_Benchmark_Analysis.ipynb**
Performance analysis and comparison over 995 DAG test cases.

**Topics covered:**
- Loading benchmark dataset
- Statistical analysis of optimization results
- Comparison: Original vs Optimized metrics
- Density-based performance analysis
- Algorithm selection justification (DFS vs Floyd-Warshall)
- Visual performance charts

**Recommended for:** Researchers, performance evaluation

---

### 3. **03_Metrics_Explained.ipynb**
Detailed explanation of all 25+ metrics with examples.

**Topics covered:**
- Basic metrics (nodes, edges, density)
- Path metrics (longest/shortest path, diameter)
- Complexity metrics (cyclomatic, topological)
- Efficiency metrics (redundancy ratio, compactness)
- Advanced metrics (PERT/CPM, layers, edge criticality)
- Mathematical formulas and interpretations
- Real-world use cases for each metric

**Recommended for:** Deep understanding, research applications

---

## Running the Notebooks

### Prerequisites

```bash
# Install library
pip install -e ..

# Install Jupyter
pip install jupyter notebook

# Optional: Install visualization tools
pip install matplotlib seaborn pandas
```

### Launch Jupyter

```bash
cd notebooks
jupyter notebook
```

Then open any `.ipynb` file in the browser.

---

## Converting to Other Formats

### To Python Script

```bash
jupyter nbconvert --to python 01_Quick_Start_Guide.ipynb
```

### To HTML

```bash
jupyter nbconvert --to html 01_Quick_Start_Guide.ipynb
```

### To PDF

```bash
jupyter nbconvert --to pdf 01_Quick_Start_Guide.ipynb
```

---

## Contributing

If you'd like to add more notebooks:

1. Create a new `.ipynb` file with a descriptive name
2. Follow the existing structure (markdown intro, code cells with comments)
3. Include visualizations where helpful
4. Add citations to research paper where relevant
5. Update this README

---

## Citations

When using these notebooks in your work, please cite:

```bibtex
@software{shrivastava2024dagoptimizer,
  author = {Shrivastava, Sahil},
  title = {DAG Optimizer: Advanced Python Library for DAG Optimization},
  year = {2024},
  url = {https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs}
}
```

