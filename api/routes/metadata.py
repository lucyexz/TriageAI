import os

from fastapi import APIRouter
from pymilvus import Collection
from api.schemas.metadata import MetadataResponse
from embeddings.indexing import COLLECTION_NAME
from embeddings.generate import EMBED_MODEL
from rag.llm import LLM_MODEL
from rag.prompt import PREPROCESSING_DESCRIPTION

TOP_K = int(os.getenv("TOP_K", "5"))
VECTOR_DIMS = 768
AVAILABLE_MODELS = ["llama3.2", "phi3", "gemma:2b"]
MLFLOW_EXPERIMENT = "triageai-baseline-oficial"

router = APIRouter()


@router.get(
    "/metadata",
    response_model=MetadataResponse,
    summary="Metadados do sistema",
    description=(
        "Retorna informações sobre o estado do sistema: coleção Milvus, modelos disponíveis, "
        "pipeline de pré-processamento e experimento MLflow."
    ),
)
def get_metadata():
    try:
        collection = Collection(COLLECTION_NAME)
        num_entities = collection.num_entities
        status = "connected"
    except Exception:
        num_entities = 0
        status = "unavailable"
    return MetadataResponse(
        collection=COLLECTION_NAME,
        num_entities=num_entities,
        embedding_model=EMBED_MODEL,
        llm_model=LLM_MODEL,
        milvus_status=status,
        available_models=AVAILABLE_MODELS,
        preprocessing_pipeline=PREPROCESSING_DESCRIPTION,
        mlflow_experiment=MLFLOW_EXPERIMENT,
        top_k=TOP_K,
        vector_dims=VECTOR_DIMS,
    )
