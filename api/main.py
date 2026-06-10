import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from embeddings.indexing import connect
from api.routes.triage import router as triage_router
from api.routes.metadata import router as metadata_router
from api.routes.models import router as models_router

MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect(host=MILVUS_HOST, port=MILVUS_PORT)
    yield


app = FastAPI(
    title="TriageAI API",
    description=(
        "## TriageAI — Assistente de Triagem Hospitalar com RAG\n\n"
        "API REST que expõe um pipeline RAG (Retrieval-Augmented Generation) para suporte à "
        "decisão de triagem hospitalar pelo Protocolo de Manchester.\n\n"
        "### Fluxo de uma requisição\n"
        "1. Recebe sintomas do paciente (`POST /query`)\n"
        "2. Gera embedding via Ollama (`nomic-embed-text`, 768-dim)\n"
        "3. Busca semântica HNSW COSINE no Milvus (`TOP_K=5` chunks)\n"
        "4. LLM local (Ollama) gera resposta estruturada com prioridade Manchester\n"
        "5. Retorna resposta com rastreabilidade completa: modelo, latência, tokens, chunks\n\n"
        "### Governança\n"
        "Cada requisição retorna `request_id`, `client_id`, `timestamp`, `model_used`, "
        "`latency_ms`, tokens consumidos e lista de chunks com score de similaridade.\n\n"
        "### Modelos de inferência disponíveis\n"
        "`llama3.2` (padrão), `phi3`, `gemma:2b`"
    ),
    version="2.0.0",
    contact={"name": "TriageAI Team", "email": "admin@mlops.local"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.include_router(triage_router, tags=["Triagem"])
app.include_router(metadata_router, tags=["Sistema"])
app.include_router(models_router, tags=["Sistema"])


@app.get("/health", tags=["Sistema"], summary="Health check", description="Verifica se a API está em execução.")
def health():
    return {"status": "ok"}
