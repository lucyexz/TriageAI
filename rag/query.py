import os
import sys
import time
from datetime import datetime, timezone

from embeddings.generate import get_client, EMBED_MODEL
from embeddings.indexing import connect, search
from rag.llm import generate_response, LLM_MODEL
from rag.prompt import build_prompt, PREPROCESSING_DESCRIPTION

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
TOP_K = int(os.getenv("TOP_K", "5"))

ALLOWED_MODELS = {"llama3.2", "phi3", "gemma:2b"}

_META_IDENTITY = """Sou o **TriageAI**, um assistente de triagem hospitalar baseado em RAG (Retrieval-Augmented Generation), desenvolvido como projeto MLOps acadêmico.

**Arquitetura:**
- API REST: FastAPI (porta 8000)
- Embedding: Ollama `nomic-embed-text` (768 dimensões)
- Busca vetorial: Milvus 2.4.5 (HNSW COSINE, TOP_K=5)
- Inferência LLM: Ollama (llama3.2, phi3, gemma:2b)
- Orquestração de dados: Apache Airflow (pipeline semanal Bronze→Silver→Gold)
- Monitoramento: Prometheus + Grafana
- Experimentos ML: MLflow (artefatos no MinIO, metadados no PostgreSQL)

**Função:** Apoio à decisão clínica de triagem hospitalar usando o Protocolo de Manchester, auxiliando profissionais de saúde na classificação de prioridade e ações iniciais."""

_META_MODELS = """**Modelos treinados no TriageAI:**

**Modelo baseline (classificação supervisionada):**
- Experimento MLflow: `triageai-baseline-oficial`
- Algoritmo: TF-IDF (max_features=10.000, ngram_range=(1,2)) + Logistic Regression (C=1.0)
- Métricas obtidas:
  - `accuracy = 0.8570`
  - `f1_score (weighted) = 0.8563`
- Artefatos persistidos em: MinIO `s3://mlflow-artifacts/` | Metadados: PostgreSQL database `mlflow`
- Modelo registrado como: `triageai-baseline` versão 1

**Modelos de inferência RAG (Ollama local):**
- `llama3.2` — modelo padrão de geração de respostas
- `phi3` — modelo Microsoft Phi-3 (alternativa compacta)
- `gemma:2b` — modelo Google Gemma 2B

**Modelo de embedding:**
- `nomic-embed-text` — gera vetores de 768 dimensões para busca semântica no Milvus"""

_META_PREPROCESSING = """**Pipeline de pré-processamento dos dados (Medallion Architecture):**

**Camada Bronze** (`s3://bronze/`):
- Fonte: dataset Kaggle `dhivyeshrk/diseases-and-symptoms-dataset`
- Conteúdo: CSV bruto com ~5.000 registros de doenças × sintomas (colunas binárias)
- Operação: ingestão direta sem transformação

**Camada Silver** (`s3://silver/`):
- Normalização dos nomes de doenças (minúsculas, strip)
- Extração das colunas binárias de sintomas para lista: `['sintoma_1', 'sintoma_2', ...]`
- Remoção de sufixos numéricos duplicados (`.1`, `.2`)

**Camada Gold** (`s3://gold/`):
- Geração de texto RAG no template:
  `"<Disease> is a condition that may present symptoms such as <symptom_1>, <symptom_2>..."`
- Formato otimizado para embedding semântico

**Indexação Milvus:**
- Embeddings gerados com `nomic-embed-text` via Ollama
- Índice HNSW (M=8, efConstruction=64, métrica COSINE)
- Carga incremental por hash SHA-256 do documento (idempotente)

**Orquestração:** DAG `triageai_medallion_pipeline` no Apache Airflow (schedule semanal)"""

_META_KEYWORDS = {
    "quem": _META_IDENTITY,
    "who are you": _META_IDENTITY,
    "o que e voce": _META_IDENTITY,
    "what are you": _META_IDENTITY,
    "modelo": _META_MODELS,
    "models": _META_MODELS,
    "metrica": _META_MODELS,
    "metric": _META_MODELS,
    "treinado": _META_MODELS,
    "trained": _META_MODELS,
    "pre-processamento": _META_PREPROCESSING,
    "preprocessamento": _META_PREPROCESSING,
    "preprocessing": _META_PREPROCESSING,
    "pre processamento": _META_PREPROCESSING,
    "pipeline": _META_PREPROCESSING,
    "dados": _META_PREPROCESSING,
}


def _detect_meta(text: str) -> str | None:
    normalized = text.lower().strip()
    for keyword, response in _META_KEYWORDS.items():
        if keyword in normalized:
            return response
    return None


def _translate_to_english(symptoms: str, client) -> str:
    response = client.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a medical translator. Translate the given medical symptoms from Portuguese to English. Return only the translated text, no explanations.",
            },
            {"role": "user", "content": symptoms},
        ],
    )
    return response["message"]["content"].strip()


def run_rag(
    symptoms: str,
    model: str | None = None,
    client_id: str = "anonymous",
    request_id: str = "",
) -> dict:
    effective_model = model if model in ALLOWED_MODELS else LLM_MODEL

    t_start = time.perf_counter()

    meta_response = _detect_meta(symptoms)
    if meta_response:
        latency_ms = (time.perf_counter() - t_start) * 1000
        return {
            "response": meta_response,
            "request_id": request_id,
            "client_id": client_id,
            "timestamp": datetime.now(timezone.utc),
            "model_used": "system",
            "embedding_model_used": EMBED_MODEL,
            "latency_ms": round(latency_ms, 2),
            "embedding_tokens": 0,
            "generation_tokens": 0,
            "total_tokens": 0,
            "chunks": [],
            "num_chunks": 0,
            "preprocessing": PREPROCESSING_DESCRIPTION,
        }

    connect(host=MILVUS_HOST, port=MILVUS_PORT)
    client = get_client(host=OLLAMA_HOST)
    symptoms_en = _translate_to_english(symptoms, client)

    embed_raw = client.embed(model=EMBED_MODEL, input=[symptoms_en])
    embedding_tokens = embed_raw.get("prompt_eval_count", 0)
    embeddings = embed_raw.get("embeddings", [])
    if not embeddings:
        raise RuntimeError("Embedding gerado está vazio.")
    query_embedding = embeddings[0]

    results = search(query_embedding, top_k=TOP_K)
    messages = build_prompt(symptoms, results)
    llm_result = generate_response(messages, model=effective_model)

    latency_ms = (time.perf_counter() - t_start) * 1000

    generation_tokens = llm_result.get("eval_count", 0)
    prompt_tokens = llm_result.get("prompt_eval_count", 0)

    return {
        "response": llm_result["response"],
        "request_id": request_id,
        "client_id": client_id,
        "timestamp": datetime.now(timezone.utc),
        "model_used": effective_model,
        "embedding_model_used": EMBED_MODEL,
        "latency_ms": round(latency_ms, 2),
        "embedding_tokens": embedding_tokens,
        "generation_tokens": generation_tokens,
        "total_tokens": embedding_tokens + generation_tokens + prompt_tokens,
        "chunks": results,
        "num_chunks": len(results),
        "preprocessing": PREPROCESSING_DESCRIPTION,
    }


if __name__ == "__main__":
    symptoms = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Sintomas: ")
    print("\n=== ANÁLISE DE TRIAGEM ===\n")
    result = run_rag(symptoms)
    print(result["response"])
