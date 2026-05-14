from fastapi import APIRouter, HTTPException
from api.schemas.triage import TriageRequest, TriageResponse
from rag.query import run_rag

router = APIRouter()


@router.post("/query", response_model=TriageResponse)
def query_triage(request: TriageRequest):
    try:
        result = run_rag(request.symptoms)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno na análise de triagem")
    return TriageResponse(symptoms=request.symptoms, response=result)
