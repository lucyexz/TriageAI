# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TriageAI is an AI-powered hospital triage assistant using Retrieval-Augmented Generation (RAG). It analyzes patient symptoms, suggests possible conditions, assigns triage priority levels, and recommends initial actions. All LLM inference and embedding generation runs locally via Ollama (`nomic-embed-text`, 768-dim vectors).

## Environment Setup

```bash
cp .env.example .env
make up          # Start all 14 services
```

All services communicate on the internal `mlops-net` Docker bridge network. Service names (not `localhost`) are used as hostnames inside containers.

## Common Commands (Makefile)

```bash
make up                    # Start all services
make down                  # Stop all services
make reset                 # Full clean restart (down -v + up --build)
make up-infra              # Start only infra (postgres, minio, mlflow, etcd, milvus, redis)
make build                 # Rebuild images without cache
make ps                    # Show container status
make health                # Run health checks on all services
make logs s=<service>      # Stream logs (e.g. make logs s=airflow-scheduler)
make restart s=<service>   # Restart a service
make shell s=<service>     # Shell into container
make clean                 # ⚠️ Removes all volumes (destroys all data)
```

## Architecture

### Services & Ports

| Service | Technology | Port |
|---------|-----------|------|
| API backend | FastAPI | 8000 |
| Web UI | HTML/CSS/JS | 7860 |
| Vector DB | Milvus 2.4.5 | 19530 (gRPC), 9091 (HTTP) |
| Embeddings/LLM | Ollama | 11434 |
| Relational DB | PostgreSQL 15 | 5432 |
| Object storage | MinIO (primary) | 9000 (API), 9001 (console) |
| Object storage | MinIO (Milvus) | 9010 (API), 9011 (console) |
| Pipeline orchestration | Apache Airflow 2.9.1 | 8080 |
| Experiment tracking | MLflow 2.13.0 | 5000 |
| Notebooks | Jupyter Lab | 8888 (token: `mlops2025`) |
| Metrics | Prometheus | 9090 |
| Dashboards | Grafana | 3000 |
| Cache/broker | Redis 7 | 6379 |
| Milvus coordination | ETCD v3.5.5 | 2379 |

### Data Flow

```
User (symptoms) → HTML/CSS/JS UI / FastAPI
  → Ollama: generate query embedding (768-dim)
  → Milvus: HNSW COSINE similarity search
  → RAG context retrieved
  → LLM: generate triage response
  → Return: condition, priority, recommended actions
```

### Frontend Architecture

- `frontend/server.py` serves `index.html` on port 7860 and proxies `POST /query` to `http://api:8000/query` — the browser never resolves Docker-internal hostnames.
- To change the upstream API: set the `API_URL` environment variable in the container (default: `http://api:8000`).

### Medallion Data Lake (Airflow DAG: `airflow/dags/pipeline_triageai.py`)

Runs on a weekly schedule, mirrored in MinIO and `data/` locally:

1. **Bronze** (`minio://bronze/`) — raw Kaggle dataset CSV (diseases & symptoms)
2. **Silver** (`minio://silver/`) — cleaned/normalized, symptoms extracted
3. **Gold** (`minio://gold/`) — RAG-formatted text strings ready for embedding
4. **Milvus indexing** — Ollama embeddings generated, HNSW index built in Milvus

### Milvus Collection Schema

- `id` — INT64, auto-increment PK
- `disease` — VARCHAR(200)
- `texto_rag` — VARCHAR(2500), full RAG context string
- `embedding` — FLOAT_VECTOR(768), Ollama `nomic-embed-text`

### MLflow Backend

- Metadata: PostgreSQL (`mlflow` database)
- Artifacts: MinIO (`mlflow-artifacts` bucket, S3-compatible)
- Tracking URI inside containers: `http://mlflow:5000`

## Implementation Status

### Implemented (Sprints 1–8)

- `api/main.py` — FastAPI: `POST /query`, `GET /health`, `GET /metadata`
- `api/routes/` and `api/schemas/` — route handlers and Pydantic models
- `embeddings/generate.py` — Ollama embedding wrapper (`nomic-embed-text`, 768-dim)
- `embeddings/indexing.py` — Milvus CRUD operations
- `api/Dockerfile` — API container image
- `frontend/index.html` — HTML/CSS/JS UI (Unimed-inspired, green #00843D, Inter font)
- `frontend/server.py` — Python stdlib server: serves `index.html` + proxies `/query` to the API
- `frontend/Dockerfile` — frontend container image (no external dependencies)

### Pending / Next Steps

RAG retrieval quality depends on data indexed in Milvus. Verify the collection is populated:

```bash
make shell s=api
# inside the container:
python -c "
from pymilvus import Collection, connections
connections.connect(host='milvus', port=19530)
c = Collection('triageai_knowledge_base')
print('indexed docs:', c.num_entities)
"
```

If `num_entities` is 0 or very low, trigger the `pipeline_triageai` DAG in Airflow (`http://localhost:8080`) to run the full Bronze → Silver → Gold → Milvus pipeline on the Kaggle dataset.

## Default Credentials (dev only, from `.env.example`)

- PostgreSQL: `admin` / `admin123`
- MinIO: `minioadmin` / `minioadmin123`
- Airflow: `admin` / `admin123`
- Jupyter: token `mlops2025`
