import hashlib

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


def _make_schema() -> CollectionSchema:
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="doc_hash", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="disease", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="texto_rag", dtype=DataType.VARCHAR, max_length=2500),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
    ]
    return CollectionSchema(fields, description="Base RAG TriageAI")


def ensure_collection_exists() -> Collection:
    """Creates the collection if it doesn't exist.
    If it exists but is missing the doc_hash field (old schema), recreates it with migration warning."""
    if utility.has_collection(COLLECTION_NAME):
        col = Collection(COLLECTION_NAME)
        field_names = {f.name for f in col.schema.fields}
        if "doc_hash" not in field_names:
            print(f"[Milvus] Schema antigo detectado (sem doc_hash) — recriando coleção para indexação incremental.")
            utility.drop_collection(COLLECTION_NAME)
            col = Collection(name=COLLECTION_NAME, schema=_make_schema())
            print(f"[Milvus] Coleção '{COLLECTION_NAME}' recriada com schema atualizado.")
        else:
            print(f"[Milvus] Coleção '{COLLECTION_NAME}' já existe — mantendo dados.")
        return col
    collection = Collection(name=COLLECTION_NAME, schema=_make_schema())
    print(f"[Milvus] Coleção '{COLLECTION_NAME}' criada.")
    return collection


def reset_collection() -> Collection:
    """Drops and recreates the collection. Use only for manual schema resets."""
    if utility.has_collection(COLLECTION_NAME):
        utility.drop_collection(COLLECTION_NAME)
        print(f"[Milvus] Coleção '{COLLECTION_NAME}' removida.")
    collection = Collection(name=COLLECTION_NAME, schema=_make_schema())
    print(f"[Milvus] Coleção '{COLLECTION_NAME}' criada.")
    return collection


def doc_hash(disease: str, texto_rag: str) -> str:
    return hashlib.sha256(f"{disease}|{texto_rag}".encode()).hexdigest()[:32]


def upsert_batch(
    collection: Collection,
    diseases: list[str],
    texts: list[str],
    embeddings: list[list[float]],
) -> int:
    """Inserts only documents not already in the collection (idempotent by doc_hash).
    Returns the number of new documents inserted."""
    hashes = [doc_hash(d, t) for d, t in zip(diseases, texts)]

    # Query existing hashes in this batch
    hash_filter = 'doc_hash in [' + ', '.join(f'"{h}"' for h in hashes) + ']'
    try:
        existing = collection.query(
            expr=hash_filter,
            output_fields=["doc_hash"],
            consistency_level="Strong",
        )
        existing_hashes = {r["doc_hash"] for r in existing}
    except Exception:
        existing_hashes = set()

    new_docs = [
        (h, d, t, e)
        for h, d, t, e in zip(hashes, diseases, texts, embeddings)
        if h not in existing_hashes
    ]

    if not new_docs:
        return 0

    new_hashes, new_diseases, new_texts, new_embeddings = zip(*new_docs)
    collection.insert([list(new_hashes), list(new_diseases), list(new_texts), list(new_embeddings)])
    return len(new_docs)


def insert_batch(
    collection: Collection,
    diseases: list[str],
    texts: list[str],
    embeddings: list[list[float]],
) -> None:
    """Legacy insert without deduplication. Kept for compatibility."""
    hashes = [doc_hash(d, t) for d, t in zip(diseases, texts)]
    collection.insert([hashes, diseases, texts, embeddings])


def create_index_and_load(collection: Collection) -> None:
    index_params = {
        "metric_type": "COSINE",
        "index_type": "HNSW",
        "params": {"M": 8, "efConstruction": 64},
    }
    existing_indexes = collection.indexes
    if not any(idx.field_name == "embedding" for idx in existing_indexes):
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
