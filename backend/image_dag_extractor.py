"""
Image-based DAG Extraction Module

Extracts graph structure from uploaded DAG images using Vision-Language Models.
Supports OpenRouter API for access to multiple vision models.
"""

import base64
import re
from typing import List, Tuple, Optional, Dict
import json
import requests


class ImageDAGExtractor:
    """Extract DAG structure from images using OpenRouter API"""
    
    def __init__(self, api_key: str, model: str = "google/gemini-2.0-flash-exp:free"):
        """
        Initialize the extractor
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (default: google/gemini-2.0-flash-exp:free)
                   Options:
                   - google/gemini-2.0-flash-exp:free (FREE, recommended)
                   - google/gemini-flash-1.5 (cheap, fast)
                   - anthropic/claude-3-haiku (excellent)
                   - openai/gpt-4o-mini (best quality)
        """
        if not api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def extract_from_image(self, image_path: str) -> Dict:
        """Extract DAG using OpenRouter API"""
        # Read and encode image
        with open(image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Detect image format
        image_format = "jpeg"
        if image_path.lower().endswith('.png'):
            image_format = "png"
        elif image_path.lower().endswith('.webp'):
            image_format = "webp"
        
        # Prompt for structured extraction
        prompt = """Analyze this directed acyclic graph (DAG) image and extract its structure.

Please identify:
1. All nodes and their labels (look for circles, boxes, or any shapes with text)
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
- If node labels are unclear, use numbers (1, 2, 3...)"""
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_format};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Make API request
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse JSON from response
        try:
            # Extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {content}")
            raise ValueError(f"Could not parse model response as JSON: {e}")
    
    def extract(self, image_path: str) -> Dict:
        """
        Extract DAG from image using OpenRouter API
        
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
            return self.extract_from_image(image_path)
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
    # Initialize with OpenRouter API key
    # Get your free API key from: https://openrouter.ai/keys
    extractor = ImageDAGExtractor(
        api_key="your-openrouter-api-key",
        model="google/gemini-2.0-flash-exp:free"  # FREE model!
    )
    
    # Extract from image
    result = extractor.extract("path/to/dag-image.png")
    print(json.dumps(result, indent=2))
    
    # Validate
    is_valid, error = ImageDAGExtractor.validate_dag(result)
    if is_valid:
        print("✅ Valid DAG extracted!")
    else:
        print(f"❌ Invalid: {error}")

