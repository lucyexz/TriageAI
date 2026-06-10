from fastapi import APIRouter, HTTPException
from api.schemas.triage import ChunkInfo, TriageRequest, TriageResponse
from rag.query import run_rag, ALLOWED_MODELS

router = APIRouter()


@router.post(
    "/query",
    response_model=TriageResponse,
    summary="Análise de triagem",
    description=(
        "Recebe sintomas do paciente e retorna análise de triagem pelo Protocolo de Manchester. "
        "Inclui rastreabilidade completa: modelo utilizado, latência, tokens consumidos e chunks RAG recuperados."
    ),
)
def query_triage(request: TriageRequest):
    model = request.model if request.model in ALLOWED_MODELS else None
    try:
        result = run_rag(
            symptoms=request.symptoms,
            model=model,
            client_id=request.client_id,
            request_id=request.request_id,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno na análise de triagem")

    return TriageResponse(
        symptoms=request.symptoms,
        response=result["response"],
        request_id=result["request_id"],
        client_id=result["client_id"],
        timestamp=result["timestamp"],
        model_used=result["model_used"],
        embedding_model_used=result["embedding_model_used"],
        latency_ms=result["latency_ms"],
        embedding_tokens=result["embedding_tokens"],
        generation_tokens=result["generation_tokens"],
        total_tokens=result["total_tokens"],
        chunks=[ChunkInfo(**c) for c in result["chunks"]],
        num_chunks=result["num_chunks"],
        preprocessing=result["preprocessing"],
    )
