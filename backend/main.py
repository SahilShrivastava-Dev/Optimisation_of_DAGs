from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple
import networkx as nx
import numpy as np
import json
import base64
import io
from datetime import datetime
import tempfile
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

# Try to import graphviz_layout, fall back to spring_layout if not available
try:
    from networkx.drawing.nx_agraph import graphviz_layout
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False
from collections import defaultdict
from neo4j import GraphDatabase

# Import the DAG optimizer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.dag_optimiser.dag_class import DAGOptimizer

app = FastAPI(title="DAG Optimizer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Edge(BaseModel):
    source: str
    target: str
    classes: Optional[List[str]] = []

class GraphInput(BaseModel):
    edges: List[Edge]

class OptimizationOptions(BaseModel):
    edges: List[Edge]
    transitive_reduction: bool = True
    merge_nodes: bool = True
    handle_cycles: str = "error"  # "error" or "remove"

class RandomDAGParams(BaseModel):
    num_nodes: int
    edge_probability: float

class Neo4jConfig(BaseModel):
    uri: str
    username: str
    password: str
    graph_type: str  # "original" or "optimized"

# Helper functions
def edges_to_optimizer(edges: List[Edge]) -> Tuple[List[Tuple[str, str]], Dict]:
    edge_list = [(e.source, e.target) for e in edges]
    edge_attrs = {(e.source, e.target): e.classes or [] for e in edges}
    return edge_list, edge_attrs

def create_visualization(optimizer: DAGOptimizer, optimized: bool = False) -> str:
    """Create a visualization and return base64 encoded PNG"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    G = optimizer.graph if optimized else optimizer.original_graph
    
    # Use graphviz layout if available, otherwise use spring layout
    if HAS_GRAPHVIZ:
        try:
            pos = graphviz_layout(G, prog='dot')
        except:
            pos = nx.spring_layout(G, seed=42, k=1/np.sqrt(len(G.nodes())))
    else:
        pos = nx.spring_layout(G, seed=42, k=1/np.sqrt(len(G.nodes())) if len(G.nodes()) > 0 else 1)
    
    # Color edges based on classes
    edge_colors = []
    for u, v in G.edges():
        cls = optimizer.edge_attrs.get((u, v), [])
        if 'Modify' in cls:
            edge_colors.append('#ec4899')  # Pink
        elif 'Call_by' in cls:
            edge_colors.append('#6b7280')  # Gray
        else:
            edge_colors.append('#3b82f6')  # Blue
    
    node_color = '#10b981' if optimized else '#3b82f6'  # Green for optimized, blue for original
    
    nx.draw(
        G, pos, ax=ax, 
        with_labels=True,
        node_color=node_color,
        edge_color=edge_colors if edge_colors else '#3b82f6',
        node_size=800,
        font_size=10,
        font_color='white',
        font_weight='bold',
        arrows=True,
        arrowsize=20,
        arrowstyle='->',
        width=2,
        alpha=0.9
    )
    
    ax.set_title('Optimized Graph' if optimized else 'Original Graph', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()
    
    # Convert to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    return img_base64

# Endpoints
@app.get("/")
async def root():
    return {"message": "DAG Optimizer API", "version": "2.0"}

@app.post("/api/validate")
async def validate_graph(graph_input: GraphInput):
    """Validate if the input forms a valid DAG"""
    try:
        edge_list, _ = edges_to_optimizer(graph_input.edges)
        G = nx.DiGraph(edge_list)
        
        is_dag = nx.is_directed_acyclic_graph(G)
        num_components = nx.number_weakly_connected_components(G)
        cycles = []
        
        if not is_dag:
            cycles = [list(cycle) for cycle in nx.simple_cycles(G)]
        
        return {
            "is_dag": is_dag,
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "num_components": num_components,
            "cycles": cycles[:5]  # Return first 5 cycles
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/optimize")
async def optimize_graph(options: OptimizationOptions):
    """Optimize a DAG with specified options"""
    try:
        edge_list, edge_attrs = edges_to_optimizer(options.edges)
        G = nx.DiGraph(edge_list)
        
        # Handle cycles
        if not nx.is_directed_acyclic_graph(G):
            if options.handle_cycles == "error":
                cycles = [list(cycle) for cycle in nx.simple_cycles(G)]
                return {
                    "error": "Graph contains cycles",
                    "cycles": cycles[:5]
                }
            else:
                # Remove cycles
                try:
                    from networkx.algorithms.approximation import minimum_feedback_arc_set
                    fas = minimum_feedback_arc_set(G)
                    G.remove_edges_from(fas)
                except:
                    for cycle in nx.simple_cycles(G):
                        cycle_edges = list(zip(cycle, cycle[1:] + [cycle[0]]))
                        for u, v in cycle_edges:
                            if G.has_edge(u, v):
                                G.remove_edge(u, v)
                                break
                edge_list = list(G.edges())
        
        # Create optimizer
        optimizer = DAGOptimizer(edge_list, edge_attrs)
        
        # Apply optimizations
        if options.transitive_reduction:
            optimizer.transitive_reduction()
        if options.merge_nodes:
            optimizer.merge_equivalent_nodes()
        
        # Get metrics
        original_metrics = optimizer.evaluate_graph_metrics(optimizer.original_graph)
        optimized_metrics = optimizer.evaluate_graph_metrics(optimizer.graph)
        
        # Create visualizations
        original_viz = create_visualization(optimizer, optimized=False)
        optimized_viz = create_visualization(optimizer, optimized=True)
        
        # Prepare edge data
        original_edges = [
            {"source": u, "target": v, "classes": edge_attrs.get((u, v), [])}
            for u, v in optimizer.original_graph.edges()
        ]
        optimized_edges = [
            {"source": u, "target": v, "classes": optimizer.edge_attrs.get((u, v), [])}
            for u, v in optimizer.graph.edges()
        ]
        
        return {
            "success": True,
            "original": {
                "edges": original_edges,
                "metrics": original_metrics,
                "visualization": original_viz
            },
            "optimized": {
                "edges": optimized_edges,
                "metrics": optimized_metrics,
                "visualization": optimized_viz
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/random-dag")
async def generate_random_dag(params: RandomDAGParams):
    """Generate a random DAG"""
    try:
        import random
        
        nodes = [str(i) for i in range(params.num_nodes)]
        edges = []
        
        for i in range(params.num_nodes):
            for j in range(i + 1, params.num_nodes):
                if random.random() < params.edge_probability:
                    edges.append({"source": nodes[i], "target": nodes[j], "classes": []})
        
        return {"edges": edges}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse-csv")
async def parse_csv(file: UploadFile = File(...)):
    """Parse uploaded CSV/Excel file"""
    try:
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Detect columns
        columns = df.columns.tolist()
        
        # Try to auto-detect source and target columns
        source_col = None
        target_col = None
        
        for col in columns:
            col_lower = col.lower()
            if 'source' in col_lower or 'from' in col_lower:
                source_col = col
            elif 'target' in col_lower or 'to' in col_lower or 'dest' in col_lower:
                target_col = col
        
        # Default to first two columns if not found
        if not source_col:
            source_col = columns[0]
        if not target_col:
            target_col = columns[1] if len(columns) > 1 else columns[0]
        
        # Get unique values for filters
        filters = {}
        if 'report_name' in df.columns:
            filters['report_name'] = df['report_name'].unique().tolist()
        if 'classes' in df.columns:
            filters['classes'] = df['classes'].unique().tolist()
        
        return {
            "columns": columns,
            "source_column": source_col,
            "target_column": target_col,
            "row_count": len(df),
            "filters": filters,
            "preview": df.head(10).to_dict(orient='records')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class Neo4jPushRequest(BaseModel):
    config: Neo4jConfig
    options: OptimizationOptions

@app.post("/api/neo4j/push")
async def push_to_neo4j(request: Neo4jPushRequest):
    """Push graph to Neo4j"""
    try:
        config = request.config
        options = request.options
        
        edge_list, edge_attrs = edges_to_optimizer(options.edges)
        optimizer = DAGOptimizer(edge_list, edge_attrs)
        
        if options.transitive_reduction:
            optimizer.transitive_reduction()
        if options.merge_nodes:
            optimizer.merge_equivalent_nodes()
        
        graph_to_push = optimizer.original_graph if config.graph_type == "original" else optimizer.graph
        
        driver = GraphDatabase.driver(config.uri, auth=(config.username, config.password))
        
        def create_graph(tx):
            for node in graph_to_push.nodes():
                tx.run("MERGE (n:Node {name: $name})", name=node)
            
            for u, v in graph_to_push.edges():
                classes = optimizer.edge_attrs.get((u, v), [])
                tx.run(
                    "MATCH (a:Node {name: $u}) "
                    "MATCH (b:Node {name: $v}) "
                    "MERGE (a)-[r:DEPENDS_ON]->(b) "
                    "SET r.classes = $classes",
                    u=u, v=v, classes=classes
                )
        
        with driver.session() as session:
            session.write_transaction(create_graph)
        
        driver.close()
        
        return {"success": True, "message": "Successfully pushed to Neo4j"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j error: {str(e)}")

@app.post("/api/extract-from-image")
async def extract_dag_from_image(
    file: UploadFile = File(...)
):
    """Extract DAG structure from uploaded image"""
    tmp_path = None
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Try to use AI extraction
        try:
            # Attempt to import the extractor
            try:
                from image_dag_extractor import ImageDAGExtractor
            except ImportError:
                # Module not found, return helpful message
                return {
                    "success": False,
                    "error": "setup_required",
                    "message": "AI vision models not installed",
                    "installation": {
                        "option1": "pip install openai (for GPT-4 Vision - best quality)",
                        "option2": "pip install transformers torch pillow (for free local models)",
                        "tip": "After installation, restart the backend server"
                    }
                }
            
            # Try OpenAI first (if API key available)
            api_key = os.getenv("OPENAI_API_KEY")
            
            if api_key:
                try:
                    extractor = ImageDAGExtractor(method="openai", api_key=api_key)
                    result = extractor.extract(tmp_path)
                except Exception as e:
                    return {
                        "success": False,
                        "error": "openai_failed",
                        "message": f"OpenAI extraction failed: {str(e)}",
                        "suggestion": "Check your API key or try local models: pip install transformers torch pillow"
                    }
            else:
                # Try Hugging Face models
                try:
                    extractor = ImageDAGExtractor(method="huggingface")
                    result = extractor.extract(tmp_path)
                except ImportError as e:
                    return {
                        "success": False,
                        "error": "dependencies_missing",
                        "message": "AI model dependencies not installed",
                        "missing": str(e),
                        "install": "pip install transformers torch pillow"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": "extraction_failed",
                        "message": f"Could not extract graph: {str(e)}",
                        "suggestion": "Make sure the image has clear nodes and arrows"
                    }
            
            # Validate extracted graph
            is_valid, error = ImageDAGExtractor.validate_dag(result)
            
            if not is_valid:
                return {
                    "success": False,
                    "error": "invalid_graph",
                    "message": f"Extracted graph is invalid: {error}",
                    "suggestion": "Try a clearer image or use manual input"
                }
            
            # Convert to Edge format
            edges = [
                {"source": e["source"], "target": e["target"], "classes": []}
                for e in result["edges"]
            ]
            
            return {
                "success": True,
                "method": "openai" if api_key else "huggingface",
                "edges": edges,
                "nodes": result["nodes"],
                "message": f"✅ Extracted {len(result['nodes'])} nodes and {len(edges)} edges"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": "unexpected_error",
                "message": f"Unexpected error: {str(e)}",
                "trace": str(type(e).__name__)
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": "file_error",
            "message": f"Could not process uploaded file: {str(e)}"
        }
    
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass  # Ignore cleanup errors

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/image-extraction/status")
async def check_image_extraction_status():
    """Check if image extraction dependencies are available"""
    status = {
        "image_extraction_available": False,
        "openai_available": False,
        "huggingface_available": False,
        "methods": []
    }
    
    # Check OpenAI
    try:
        import openai
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            status["openai_available"] = True
            status["methods"].append("GPT-4 Vision (best quality)")
    except ImportError:
        pass
    
    # Check Hugging Face
    try:
        import transformers
        import torch
        status["huggingface_available"] = True
        status["methods"].append("Florence-2/BLIP-2 (free, local)")
    except ImportError:
        pass
    
    status["image_extraction_available"] = status["openai_available"] or status["huggingface_available"]
    
    if not status["image_extraction_available"]:
        status["installation_instructions"] = {
            "option1": "pip install openai (then set OPENAI_API_KEY)",
            "option2": "pip install transformers torch pillow"
        }
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

