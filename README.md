# DAG Optimizer Streamlit App

A Streamlit‑based dashboard for loading, optimizing and visualizing Directed Acyclic Graphs (DAGs) with:

- **Transitive Reduction**  
- **Node Equivalence Merging**  
- **Rich Graph Metrics** (nodes, edges, depth, width, cyclomatic complexity, degree entropy, density, etc.)  
- **Static side‑by‑side visualization** (original vs. optimized)  
- **Downloadable metadata** (JSON) and visualization (PNG)  
- **Neo4j integration**: push optimized graph as `:Node` & `[:DEPENDS_ON]` relationships  

---

## 🚀 Features

- **Multiple input modes**:  
  - Upload CSV (`source,target`)  
  - Paste comma‑separated edge list  
  - Generate a random DAG  
- **Optimization options**: checkbox toggles for transitive reduction and node‑merging  
- **Interactive sidebar**:  
  - Click **Optimize** to apply your chosen operations  
  - Fill in Bolt URI / Username / Password to **Push to Neo4j**  
- **Metrics dashboard**: side‑by‑side table comparing original vs. optimized graph  
- **Static visualization**: Matplotlib‑based PNG showing original and optimized DAGs  
- **Exports**: one‑click downloads for JSON metadata and PNG visualization  

---

## 📦 Installation

1. **Clone this repository**  
   ```bash
   git clone https://github.com/your-org/dag-optimizer.git
   cd dag-optimizer
   ```

2. **Create & activate a Python 3.7+ virtual environment**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # macOS/Linux
   .venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

   _If you don’t have a `requirements.txt`, you can install directly:_  
   ```bash
   pip install streamlit networkx matplotlib neo4j pydot pandas
   ```

---

## ▶️ Usage

From the project root, run:

```bash
streamlit run streamlit_app.py
```

1. **Load or generate** a DAG:  
   - Upload a CSV with `source,target` columns  
   - Paste your edges (one `A,B` per line)  
   - Generate a random DAG by specifying node count & edge probability  

2. **Optimize**:  
   - Toggle **Transitive Reduction** and/or **Merge Equivalent Nodes** on the sidebar  
   - Click **Optimize**  

3. **Push to Neo4j** (optional):  
   - Enter your Bolt URI (e.g. `bolt://localhost:7687` or Aura URI)  
   - Enter Username & Password  
   - Click **Push to Neo4j**  

4. **View results**:  
   - Metrics comparison table appears  
   - Static side‑by‑side PNG visualization renders  
   - Download JSON metadata or PNG via provided buttons  

---

## ⚙️ Configuration

- **Bolt URI**: your Neo4j instance address (e.g. `bolt://localhost:7687` or Aura’s `bolt://<your‑instance>.databases.neo4j.io`)  
- **Authentication**: valid Neo4j credentials  
- **CSV format**: two columns named `source` and `target`  

---

## 📁 Project Structure

```
.
├── README.md
├── requirements.txt
├── streamlit_app.py
└── src
    └── dag_optimiser
        └── dag_class.py    # DAGOptimizer implementation
```

---

## 🤝 Contributing

1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/XYZ`)  
3. Commit your changes (`git commit -m "Add XYZ"`)  
4. Push to your branch (`git push origin feature/XYZ`)  
5. Open a Pull Request  

---
.  

