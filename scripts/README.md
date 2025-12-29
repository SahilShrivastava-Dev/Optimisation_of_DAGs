# 🛠️ Scripts Folder

This folder contains utility scripts for documentation generation and benchmarking.

## 📄 Available Scripts

### 1. `generate_documentation.py`
**Purpose:** Generates the complete DAG Optimizer guide as a DOCX file.

**Usage:**
```bash
python scripts/generate_documentation.py
```

**Output:** `DAG_Optimizer_Complete_Guide.docx` in the root directory

**Contents:**
- How to create a pip package
- NetworkX comparison
- Adaptive algorithm details
- Performance analysis
- Publishing guidelines

---

### 2. `generate_challenges_doc.py`
**Purpose:** Generates the challenges and solutions document with mathematical justifications.

**Usage:**
```bash
python scripts/generate_challenges_doc.py
```

**Output:** `Challenges_Faced.docx` in the root directory

**Contents:**
- 6 major challenges identified
- Mathematical formulas and proofs
- Benchmark results (995 DAGs)
- Comparison with conventional methods

---

### 3. `benchmark_dags.py`
**Purpose:** Runs comprehensive benchmarks on the DAG dataset.

**Usage:**
```bash
python scripts/benchmark_dags.py
```

**Output:** `Benchmark_Results/benchmark_results.json`

**What it does:**
- Tests 995+ DAGs from `DAG_Dataset/`
- Measures optimization performance
- Calculates edge reduction percentages
- Generates statistics by density category
- Creates data for research paper tables

**Benchmark Categories:**
- Sparse Small (195 DAGs)
- Sparse Medium (200 DAGs)
- Sparse Large (100 DAGs)
- Medium Small (150 DAGs)
- Medium Medium (150 DAGs)
- Dense Small (100 DAGs)
- Dense Medium (100 DAGs)

---

## 🚀 Quick Commands

```bash
# Regenerate all documentation
python scripts/generate_documentation.py
python scripts/generate_challenges_doc.py

# Run benchmarks
python scripts/benchmark_dags.py

# All at once (PowerShell)
python scripts/generate_documentation.py; python scripts/generate_challenges_doc.py
```

---

## 📦 Dependencies

All scripts require:
- Python 3.8+
- `python-docx` (for DOCX generation)
- `networkx` (for graph operations)
- All packages from `requirements.txt`

Install:
```bash
pip install -r requirements.txt
```

---

## 📝 Notes

- **Documentation scripts**: Run these whenever you update the project and want fresh documentation.
- **Benchmark script**: Only run this if you've modified the optimization algorithm or want to re-test.
- **Output files**: All output files are generated at the root directory, not inside `scripts/`.

---

## 🎯 When to Run

### `generate_documentation.py`
- After adding new features
- When updating pip package instructions
- Before publishing to GitHub

### `generate_challenges_doc.py`
- After solving new challenges
- When adding mathematical justifications
- Before research paper submission

### `benchmark_dags.py`
- After modifying optimization algorithms
- When validating research claims
- Before writing research papers with real data

---

**All scripts are standalone and can be run independently!** 🚀

