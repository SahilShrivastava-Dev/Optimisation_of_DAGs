# 🚀 Quick Start Guide

Get up and running with the DAG Optimizer in 5 minutes!

## Step 1: Install Dependencies

Run the installation script:
```bash
install_dependencies.bat
```

This will install:
- Python packages (FastAPI, NetworkX, etc.)
- Node.js packages (React, TypeScript, etc.)

**Note:** Make sure you have Graphviz installed on your system:
- Download from: https://graphviz.org/download/
- Add to PATH during installation

## Step 2: Start the Application

### Easy Way (Recommended)
Double-click `start_all.bat` - This starts both backend and frontend automatically!

### Manual Way
Open two terminals:

**Terminal 1 - Backend:**
```bash
start_backend.bat
```

**Terminal 2 - Frontend:**
```bash
start_frontend.bat
```

## Step 3: Open Your Browser

Navigate to: `http://localhost:5173`

## Step 4: Try It Out!

### Option 1: Upload a CSV File
1. Click "Upload File"
2. Drop your CSV with columns: `source`, `target`
3. Click "Build DAG"

### Option 2: Generate Random DAG
1. Click "Random DAG"
2. Adjust sliders (try: 10 nodes, 0.3 probability)
3. Click "Generate Random DAG"

### Option 3: Paste Edges
1. Click "Paste Edges"
2. Enter edges like:
   ```
   A,B
   B,C
   A,C
   ```
3. Click "Build DAG"

## Step 5: Optimize!

1. Keep both options checked:
   - ✅ Transitive Reduction
   - ✅ Merge Equivalent Nodes

2. Click **"Optimize Graph"**

3. View your results:
   - Improvement stats
   - Metrics comparison
   - Before/after visualizations

## 🎉 That's It!

You're now ready to optimize your DAGs!

## Common Issues

### "Port already in use"
- Close other applications using ports 8000 or 5173
- Or modify the ports in the config files

### "Module not found"
- Run `install_dependencies.bat` again
- Make sure you have Python 3.8+ and Node.js 18+

### "Graphviz not found"
- Install Graphviz from: https://graphviz.org/download/
- Add to system PATH
- Restart your terminal/command prompt

## Need Help?

Check out `README_NEW.md` for detailed documentation!

