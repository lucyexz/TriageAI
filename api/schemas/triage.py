from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class ChunkInfo(BaseModel):
    disease: str = Field(description="Doença associada ao chunk")
    texto_rag: str = Field(description="Texto RAG completo do chunk")
    score: float = Field(description="Score de similaridade coseno (0-1)")


class TriageRequest(BaseModel):
    symptoms: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Descrição dos sintomas do paciente",
        examples=["febre alta, dor de cabeça intensa e rigidez na nuca"],
    )
    client_id: str = Field(
        default="anonymous",
        description="Identificador do cliente/hospital que faz a requisição",
        examples=["hospital-central", "upa-norte"],
    )
    request_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="UUID único da requisição (gerado automaticamente se não informado)",
    )
    model: str | None = Field(
        default=None,
        description="Modelo de inferência a usar. Opções: llama3.2, phi3, gemma:2b. Usa o padrão se não informado.",
        examples=["llama3.2", "phi3", "gemma:2b"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "symptoms": "febre alta, dor de cabeça intensa e rigidez na nuca",
                    "client_id": "hospital-central",
                    "model": "llama3.2",
                }
            ]
        }
    }


class TriageResponse(BaseModel):
    symptoms: str = Field(description="Sintomas informados pelo cliente")
    response: str = Field(description="Análise de triagem gerada pelo LLM")
    request_id: str = Field(description="UUID da requisição")
    client_id: str = Field(description="Identificador do cliente")
    timestamp: datetime = Field(description="Data/hora da resposta (UTC)")
    model_used: str = Field(description="Modelo LLM utilizado na geração")
    embedding_model_used: str = Field(description="Modelo de embedding utilizado")
    latency_ms: float = Field(description="Latência total da inferência em milissegundos")
    embedding_tokens: int = Field(description="Tokens consumidos na geração do embedding")
    generation_tokens: int = Field(description="Tokens consumidos na geração da resposta")
    total_tokens: int = Field(description="Total de tokens consumidos (embedding + geração)")
    chunks: list[ChunkInfo] = Field(description="Chunks RAG recuperados do Milvus com score de similaridade")
    num_chunks: int = Field(description="Número de chunks recuperados")
    preprocessing: str = Field(description="Descrição do pré-processamento aplicado aos dados")
