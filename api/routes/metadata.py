from fastapi import APIRouter
from pymilvus import Collection
from api.schemas.metadata import MetadataResponse
from embeddings.indexing import COLLECTION_NAME
from embeddings.generate import EMBED_MODEL
from rag.llm import LLM_MODEL

router = APIRouter()


@router.get("/metadata", response_model=MetadataResponse)
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
    )
