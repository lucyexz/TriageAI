from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility,
)

COLLECTION_NAME = "triageai_knowledge_base"
MILVUS_HOST = "milvus"
MILVUS_PORT = "19530"


def connect(host: str = MILVUS_HOST, port: str = MILVUS_PORT) -> None:
    connections.connect("default", host=host, port=port)
    print(f"[Milvus] Conectado em {host}:{port}")


def reset_collection() -> Collection:
    """Remove a coleção existente e cria uma nova com o schema correto."""
    if utility.has_collection(COLLECTION_NAME):
        utility.drop_collection(COLLECTION_NAME)
        print(f"[Milvus] Coleção '{COLLECTION_NAME}' removida.")

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="disease", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="texto_rag", dtype=DataType.VARCHAR, max_length=2500),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
    ]
    schema = CollectionSchema(fields, description="Base RAG TriageAI")
    collection = Collection(name=COLLECTION_NAME, schema=schema)
    print(f"[Milvus] Coleção '{COLLECTION_NAME}' criada.")
    return collection


def insert_batch(
    collection: Collection,
    diseases: list[str],
    texts: list[str],
    embeddings: list[list[float]],
) -> None:
    collection.insert([diseases, texts, embeddings])


def create_index_and_load(collection: Collection) -> None:
    index_params = {
        "metric_type": "COSINE",
        "index_type": "HNSW",
        "params": {"M": 8, "efConstruction": 64},
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    collection.load()
    print(f"[Milvus] Coleção '{COLLECTION_NAME}' indexada e carregada com sucesso.")


def search(
    query_embedding: list[float],
    top_k: int = 5,
    ef: int = 64,
) -> list[dict]:
    if not utility.has_collection(COLLECTION_NAME):
        raise RuntimeError(
            f"Coleção '{COLLECTION_NAME}' não encontrada. "
            "Execute a DAG 'pipeline_triageai' no Airflow para popular o Milvus."
        )
    collection = Collection(COLLECTION_NAME)
    collection.load()
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"ef": ef}},
        limit=top_k,
        output_fields=["disease", "texto_rag"],
    )
    return [
        {
            "disease": hit.entity.get("disease"),
            "texto_rag": hit.entity.get("texto_rag"),
            "score": hit.score,
        }
        for hit in results[0]
    ]
