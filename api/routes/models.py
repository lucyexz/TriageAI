from fastapi import APIRouter
from rag.query import ALLOWED_MODELS
from rag.llm import LLM_MODEL

router = APIRouter()


@router.get(
    "/models",
    summary="Modelos de inferência disponíveis",
    description="Lista os modelos LLM disponíveis para seleção na requisição POST /query.",
)
def list_models():
    return {
        "models": sorted(ALLOWED_MODELS),
        "default": LLM_MODEL,
    }
