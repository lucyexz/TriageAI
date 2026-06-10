from pydantic import BaseModel, Field


class MetadataResponse(BaseModel):
    collection: str = Field(description="Nome da coleção Milvus")
    num_entities: int = Field(description="Número de documentos indexados")
    embedding_model: str = Field(description="Modelo de embedding utilizado")
    llm_model: str = Field(description="Modelo LLM padrão de inferência")
    milvus_status: str = Field(description="Status da conexão com Milvus")
    available_models: list[str] = Field(description="Modelos de inferência disponíveis")
    preprocessing_pipeline: str = Field(description="Descrição do pipeline de pré-processamento dos dados")
    mlflow_experiment: str = Field(description="Nome do experimento MLflow com os modelos treinados")
    top_k: int = Field(description="Número de chunks recuperados por consulta")
    vector_dims: int = Field(description="Dimensão dos vetores de embedding")
