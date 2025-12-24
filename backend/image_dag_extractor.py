"""
Image-based DAG Extraction Module

Extracts graph structure from uploaded DAG images using Vision-Language Models.
Supports both local (Hugging Face) and API-based (OpenAI) approaches.
"""

import base64
import re
from typing import List, Tuple, Optional, Dict
import json

# Option 1: OpenAI GPT-4o-mini Vision (Best Quality)
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Option 2: Hugging Face Transformers (Free, Local)
try:
    from transformers import AutoProcessor, AutoModelForVision2Seq
    from PIL import Image
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class ImageDAGExtractor:
    """Extract DAG structure from images using Vision-Language Models"""
    
    def __init__(self, method: str = "openai", api_key: Optional[str] = None):
        """
        Initialize the extractor
        
        Args:
            method: "openai" (best) or "huggingface" (free/local)
            api_key: OpenAI API key (required for openai method)
        """
        self.method = method
        self.api_key = api_key
        
        if method == "openai" and not HAS_OPENAI:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        if method == "huggingface":
            if not HAS_TRANSFORMERS:
                raise ImportError("Transformers not installed. Run: pip install transformers torch pillow")
            self._load_hf_model()
    
    def _load_hf_model(self):
        """Load Hugging Face model (Florence-2 or BLIP-2)"""
        try:
            # Try Florence-2 (best for this task)
            model_name = "microsoft/Florence-2-base"
            self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForVision2Seq.from_pretrained(model_name, trust_remote_code=True)
            self.model.eval()
            print(f"✅ Loaded {model_name}")
        except Exception as e:
            print(f"⚠️  Could not load Florence-2: {e}")
            # Fallback to BLIP-2
            try:
                model_name = "Salesforce/blip2-opt-2.7b"
                self.processor = AutoProcessor.from_pretrained(model_name)
                self.model = AutoModelForVision2Seq.from_pretrained(model_name)
                self.model.eval()
                print(f"✅ Loaded {model_name}")
            except Exception as e2:
                raise RuntimeError(f"Could not load any vision model: {e2}")
    
    def extract_with_openai(self, image_path: str) -> Dict:
        """Extract DAG using GPT-4 Vision"""
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        client = OpenAI(api_key=self.api_key)
        
        # Read and encode image
        with open(image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Prompt for structured extraction
        prompt = """
        Analyze this directed acyclic graph (DAG) image and extract its structure.
        
        Please identify:
        1. All nodes and their labels
        2. All directed edges (arrows) between nodes
        3. Direction of each edge (from → to)
        
        Return ONLY a JSON object in this exact format:
        {
          "nodes": ["A", "B", "C"],
          "edges": [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"}
          ]
        }
        
        Important:
        - Use exact node labels from the image
        - Include ALL edges you can see
        - Respect arrow directions
        - Return valid JSON only, no other text
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        
        # Parse JSON from response
        try:
            # Extract JSON if wrapped in markdown
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            return json.loads(result)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {result}")
            raise ValueError(f"Could not parse model response as JSON: {e}")
    
    def extract_with_huggingface(self, image_path: str) -> Dict:
        """Extract DAG using Hugging Face model"""
        image = Image.open(image_path).convert("RGB")
        
        prompt = """
        Analyze this graph image and list:
        1. All node labels
        2. All edges with direction (e.g., "A to B", "B to C")
        
        Format: Nodes: [list]. Edges: [list with arrows].
        """
        
        inputs = self.processor(images=image, text=prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_length=500)
        
        description = self.processor.decode(outputs[0], skip_special_tokens=True)
        
        # Parse description to extract nodes and edges
        return self._parse_description(description)
    
    def _parse_description(self, description: str) -> Dict:
        """Parse model description to extract graph structure"""
        nodes = set()
        edges = []
        
        # Try to extract nodes
        node_pattern = r'node[s]?:?\s*\[?([A-Z0-9,\s]+)\]?'
        node_match = re.search(node_pattern, description, re.IGNORECASE)
        if node_match:
            node_text = node_match.group(1)
            nodes.update([n.strip() for n in re.split(r'[,\s]+', node_text) if n.strip()])
        
        # Try to extract edges
        # Pattern: "A to B", "A -> B", "A→B"
        edge_patterns = [
            r'([A-Z0-9]+)\s*(?:to|->|→|-->)\s*([A-Z0-9]+)',
            r'([A-Z0-9]+)\s*,\s*([A-Z0-9]+)',  # fallback
        ]
        
        for pattern in edge_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for source, target in matches:
                source, target = source.strip(), target.strip()
                if source and target:
                    nodes.add(source)
                    nodes.add(target)
                    edges.append({"source": source, "target": target})
        
        return {
            "nodes": sorted(list(nodes)),
            "edges": edges
        }
    
    def extract(self, image_path: str) -> Dict:
        """
        Extract DAG from image
        
        Returns:
            {
                "nodes": ["A", "B", "C"],
                "edges": [
                    {"source": "A", "target": "B"},
                    {"source": "B", "target": "C"}
                ]
            }
        """
        try:
            if self.method == "openai":
                return self.extract_with_openai(image_path)
            else:
                return self.extract_with_huggingface(image_path)
        except Exception as e:
            raise RuntimeError(f"Failed to extract DAG from image: {e}")
    
    @staticmethod
    def validate_dag(graph_data: Dict) -> Tuple[bool, Optional[str]]:
        """Validate extracted graph data"""
        if "nodes" not in graph_data or "edges" not in graph_data:
            return False, "Missing 'nodes' or 'edges' in graph data"
        
        if not isinstance(graph_data["nodes"], list):
            return False, "'nodes' must be a list"
        
        if not isinstance(graph_data["edges"], list):
            return False, "'edges' must be a list"
        
        if len(graph_data["nodes"]) == 0:
            return False, "No nodes found in image"
        
        # Validate edges reference existing nodes
        node_set = set(graph_data["nodes"])
        for edge in graph_data["edges"]:
            if "source" not in edge or "target" not in edge:
                return False, "Edge missing 'source' or 'target'"
            
            if edge["source"] not in node_set or edge["target"] not in node_set:
                return False, f"Edge references unknown node: {edge}"
        
        return True, None


# Example usage
if __name__ == "__main__":
    # Test with OpenAI (requires API key)
    # extractor = ImageDAGExtractor(method="openai", api_key="your-key-here")
    
    # Test with Hugging Face (free, local)
    extractor = ImageDAGExtractor(method="huggingface")
    
    # Extract from image
    result = extractor.extract("path/to/dag-image.png")
    print(json.dumps(result, indent=2))
    
    # Validate
    is_valid, error = ImageDAGExtractor.validate_dag(result)
    if is_valid:
        print("✅ Valid DAG extracted!")
    else:
        print(f"❌ Invalid: {error}")

