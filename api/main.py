import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from embeddings.indexing import connect
from api.routes.triage import router as triage_router
from api.routes.metadata import router as metadata_router

MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect(host=MILVUS_HOST, port=MILVUS_PORT)
    yield


app = FastAPI(
    title="TriageAI API",
    description="API de triagem hospitalar baseada em RAG + LLM local",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(triage_router)
app.include_router(metadata_router)


@app.get("/health")
def health():
    return {"status": "ok"}
