# DAG Optimizer Backend

FastAPI backend for DAG optimization.

## Development

```bash
pip install -r requirements.txt
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### POST /api/validate
Validate if input forms a valid DAG

### POST /api/optimize
Optimize a DAG with specified options

### POST /api/random-dag
Generate a random DAG

### POST /api/parse-csv
Parse uploaded CSV/Excel file

### POST /api/neo4j/push
Push graph to Neo4j database

### GET /health
Health check endpoint

## Dependencies

- **FastAPI** - Web framework
- **NetworkX** - Graph algorithms
- **Matplotlib** - Visualizations
- **Neo4j** - Database driver
- **Pandas** - Data processing

