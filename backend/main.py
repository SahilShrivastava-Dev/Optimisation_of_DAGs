from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
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
    
    print("\n" + "="*80)
    print("🖼️  IMAGE UPLOAD RECEIVED")
    print("="*80)
    print(f"📁 File: {file.filename}")
    print(f"📏 Size: {file.size if hasattr(file, 'size') else 'unknown'} bytes")
    print(f"🎨 Type: {file.content_type}")
    
    try:
        # Save uploaded file temporarily
        print("\n💾 Saving image temporarily...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        print(f"✅ Saved to: {tmp_path}")
        
        # Try to use AI extraction with OpenRouter
        print("\n🤖 Starting AI extraction with OpenRouter...")
        try:
            # Attempt to import the extractor
            try:
                print("📦 Loading AI extractor module...")
                from image_dag_extractor import ImageDAGExtractor
                print("✅ AI extractor loaded successfully")
            except ImportError as e:
                print(f"❌ AI extractor not available: {e}")
                response = {
                    "success": False,
                    "error": "setup_required",
                    "message": "AI extractor module not found",
                    "details": str(e)
                }
                print(f"\n📤 Response: {json.dumps(response, indent=2)}")
                return response
            
            # Check for OpenRouter API key
            api_key = os.getenv("OPENROUTER_API_KEY")
            
            if not api_key:
                print("❌ No OpenRouter API key found")
                response = {
                    "success": False,
                    "error": "api_key_required",
                    "message": "OpenRouter API key required",
                    "instructions": {
                        "step1": "Get free API key from: https://openrouter.ai/keys",
                        "step2": "Set environment variable: set OPENROUTER_API_KEY=your-key",
                        "step3": "Restart backend server",
                        "note": "Free tier includes google/gemini-2.0-flash-exp:free model!"
                    }
                }
                print(f"\n📤 Response: {json.dumps(response, indent=2)}")
                return response
            
            # Get model name from env or use default
            model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
            
            print(f"\n🔑 OpenRouter API key found")
            print(f"🤖 Using model: {model}")
            print("📸 Sending image to OpenRouter API...")
            print("⏳ This may take 2-5 seconds...")
            
            try:
                extractor = ImageDAGExtractor(api_key=api_key, model=model)
                result = extractor.extract(tmp_path)
                print(f"✅ Extraction completed!")
                print(f"📊 Raw result: {json.dumps(result, indent=2)}")
            except Exception as e:
                print(f"❌ Extraction failed: {e}")
                response = {
                    "success": False,
                    "error": "extraction_failed",
                    "message": f"Could not extract graph: {str(e)}",
                    "suggestion": "Check API key is valid or try a different model"
                }
                print(f"\n📤 Response: {json.dumps(response, indent=2)}")
                return response
            
            # Validate extracted graph
            print("\n🔍 Validating extracted graph...")
            is_valid, error = ImageDAGExtractor.validate_dag(result)
            
            if not is_valid:
                print(f"❌ Validation failed: {error}")
                response = {
                    "success": False,
                    "error": "invalid_graph",
                    "message": f"Extracted graph is invalid: {error}",
                    "suggestion": "Try a clearer image or use manual input"
                }
                print(f"\n📤 Response: {json.dumps(response, indent=2)}")
                return response
            
            print("✅ Graph is valid!")
            
            # Convert to Edge format
            print("\n🔄 Converting to application format...")
            edges = [
                {"source": e["source"], "target": e["target"], "classes": []}
                for e in result["edges"]
            ]
            
            print(f"📊 Extracted:")
            print(f"   - Nodes: {result['nodes']}")
            print(f"   - Edges: {len(edges)}")
            for i, edge in enumerate(edges[:10], 1):  # Show first 10 edges
                print(f"     {i}. {edge['source']} → {edge['target']}")
            if len(edges) > 10:
                print(f"     ... and {len(edges) - 10} more")
            
            response = {
                "success": True,
                "method": "openrouter",
                "model": model,
                "edges": edges,
                "nodes": result["nodes"],
                "message": f"✅ Extracted {len(result['nodes'])} nodes and {len(edges)} edges using {model}"
            }
            
            print(f"\n📤 Sending response to frontend:")
            print(f"   Success: {response['success']}")
            print(f"   Method: {response['method']}")
            print(f"   Model: {response['model']}")
            print(f"   Nodes: {len(response['nodes'])}")
            print(f"   Edges: {len(response['edges'])}")
            print("="*80 + "\n")
            
            return response
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print(f"   Type: {type(e).__name__}")
            import traceback
            print(f"   Traceback:\n{traceback.format_exc()}")
            response = {
                "success": False,
                "error": "unexpected_error",
                "message": f"Unexpected error: {str(e)}",
                "trace": str(type(e).__name__)
            }
            print(f"\n📤 Response: {json.dumps(response, indent=2)}")
            return response
    
    except Exception as e:
        print(f"\n❌ File processing error: {e}")
        response = {
            "success": False,
            "error": "file_error",
            "message": f"Could not process uploaded file: {str(e)}"
        }
        print(f"\n📤 Response: {json.dumps(response, indent=2)}")
        return response
    
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                print(f"\n🧹 Cleaning up temporary file: {tmp_path}")
                os.unlink(tmp_path)
                print("✅ Cleanup complete")
            except Exception as e:
                print(f"⚠️  Cleanup warning: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/image-extraction/status")
async def check_image_extraction_status():
    """Check if OpenRouter API is configured"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
    status = {
        "image_extraction_available": bool(api_key),
        "openrouter_configured": bool(api_key),
        "model": model if api_key else None,
        "method": "OpenRouter API" if api_key else None,
        "setup_url": "https://openrouter.ai/keys" if not api_key else None,
        "message": "Ready for image extraction" if api_key else "OpenRouter API key required"
    }
    
    if not status["image_extraction_available"]:
        status["installation_instructions"] = {
            "option1": "pip install openai (then set OPENAI_API_KEY)",
            "option2": "pip install transformers torch pillow"
        }
    
    return status

@app.post("/api/export-research-report")
async def export_research_report(options: OptimizationOptions):
    """Generate and download a research paper-style DOCX report"""
    try:
        # Perform optimization
        edge_list, edge_attrs = edges_to_optimizer(options.edges)
        G = nx.DiGraph(edge_list)
        
        # Handle cycles if present
        if not nx.is_directed_acyclic_graph(G):
            if options.handle_cycles == "error":
                cycles = [list(cycle) for cycle in nx.simple_cycles(G)]
                raise HTTPException(
                    status_code=400, 
                    detail=f"Graph contains cycles. Remove cycles before generating report."
                )
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
        
        # Create optimizer and apply optimizations
        optimizer = DAGOptimizer(edge_list, edge_attrs)
        
        if options.transitive_reduction:
            optimizer.transitive_reduction()
        if options.merge_nodes:
            optimizer.merge_equivalent_nodes()
        
        # Get metrics
        original_metrics = optimizer.evaluate_graph_metrics(optimizer.original_graph)
        optimized_metrics = optimizer.evaluate_graph_metrics(optimizer.graph)
        
        # Prepare edge data
        original_edges = [
            {"source": u, "target": v, "classes": edge_attrs.get((u, v), [])}
            for u, v in optimizer.original_graph.edges()
        ]
        optimized_edges = [
            {"source": u, "target": v, "classes": optimizer.edge_attrs.get((u, v), [])}
            for u, v in optimizer.graph.edges()
        ]
        
        # Prepare optimization data
        optimization_data = {
            "original": {
                "edges": original_edges,
                "metrics": original_metrics
            },
            "optimized": {
                "edges": optimized_edges,
                "metrics": optimized_metrics
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate report
        from research_report_generator import ResearchReportGenerator
        
        generator = ResearchReportGenerator()
        report_buffer = generator.generate_report(optimization_data)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"DAG_Optimization_Research_Report_{timestamp}.docx"
        
        # Return as downloadable file
        return StreamingResponse(
            report_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        import traceback
        print(f"Error generating research report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

