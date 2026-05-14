from pydantic import BaseModel


class MetadataResponse(BaseModel):
    collection: str
    num_entities: int
    embedding_model: str
    llm_model: str
    milvus_status: str
