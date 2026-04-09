from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import os
import re
import ast

# ==========================================
# Configurações Globais
# ==========================================
MINIO_OPTIONS = {
    "key": "minioadmin",
    "secret": "minioadmin123",
    "client_kwargs": {"endpoint_url": "http://minio:9000"}
}

# ==========================================
# Funções de Processamento (Tasks)
# ==========================================

def ingestao_bronze():
    import kagglehub
    print("Iniciando extração do Kaggle para a Camada Bronze...")
    dataset_dir = kagglehub.dataset_download("dhivyeshrk/diseases-and-symptoms-dataset")
    csv_path = os.path.join(dataset_dir, "Final_Augmented_dataset_Diseases_and_Symptoms.csv")
    
    df = pd.read_csv(csv_path)
    path_bronze = "s3://bronze/dataset_doencas_sintomas.csv"
    df.to_csv(path_bronze, index=False, storage_options=MINIO_OPTIONS)
    print(f"Camada Bronze atualizada: {path_bronze}")

def processamento_silver():
    print("Iniciando tratamento de dados para a Camada Silver...")
    df = pd.read_csv("s3://bronze/dataset_doencas_sintomas.csv", storage_options=MINIO_OPTIONS)
    
    col_doenca = 'diseases'
    sintomas_cols = df.columns.drop(col_doenca)
    sintomas_cols_limpos = [col for col in sintomas_cols if not re.search(r'\.\d+$', col)]
    
    def extrair_sintomas(row):
        return [col for col in sintomas_cols_limpos if row[col] == 1]
    
    df['sintomas'] = df.apply(extrair_sintomas, axis=1)
    df_silver = df[[col_doenca, 'sintomas']].copy()
    
    df_silver[col_doenca] = df_silver[col_doenca].str.lower().str.strip()
    df_silver['sintomas'] = df_silver['sintomas'].apply(
        lambda lista: [s.replace('_', ' ').lower() for s in lista]
    )
    
    path_silver = "s3://silver/doencas_sintomas_limpo.csv"
    df_silver.to_csv(path_silver, index=False, storage_options=MINIO_OPTIONS)
    print(f"Camada Silver atualizada: {path_silver}")

def processamento_gold():
    print("Iniciando formatação RAG para a Camada Gold...")
    df_silver = pd.read_csv("s3://silver/doencas_sintomas_limpo.csv", storage_options=MINIO_OPTIONS)
    
    # O Pandas lê listas no CSV como strings. Precisamos convertê-las de volta para listas reais.
    df_silver['sintomas'] = df_silver['sintomas'].apply(ast.literal_eval)
    
    def gerar_texto(row):
        sintomas = ', '.join(row['sintomas'])
        return (
            f"{row['diseases'].capitalize()} is a condition that may present symptoms such as {sintomas}. "
            f"Individuals experiencing these symptoms may be associated with this condition. "
            f"This information is for educational purposes only and does not replace professional medical diagnosis."
        )
    
    df_gold = df_silver.copy()
    df_gold['texto'] = df_gold.apply(gerar_texto, axis=1)
    
    path_gold = "s3://gold/textos_rag.csv"
    df_gold.to_csv(path_gold, index=False, storage_options=MINIO_OPTIONS)
    print(f"Camada Gold atualizada: {path_gold}")

def atualizacao_milvus():
    from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
    from ollama import Client
    
    print("Iniciando geração de embeddings e indexação no Milvus...")
    df_gold = pd.read_csv("s3://gold/textos_rag.csv", storage_options=MINIO_OPTIONS)
    
    connections.connect("default", host="milvus", port="19530")
    ollama_client = Client(host='http://ollama:11434')
    
    collection_name = "triageai_knowledge_base"
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="disease", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="texto_rag", dtype=DataType.VARCHAR, max_length=2500),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
    ]
    schema = CollectionSchema(fields, description="Base RAG TriageAI")
    collection = Collection(name=collection_name, schema=schema)
    
    doencas = df_gold['diseases'].tolist()
    textos = df_gold['texto'].tolist()
    embeddings = []
    
    for texto in textos:
        response = ollama_client.embeddings(model='nomic-embed-text', prompt=texto)
        embeddings.append(response['embedding'])
        
    collection.insert([doencas, textos, embeddings])
    
    index_params = {"metric_type": "COSINE", "index_type": "HNSW", "params": {"M": 8, "efConstruction": 64}}
    collection.create_index(field_name="embedding", index_params=index_params)
    collection.load()
    print("Indexação vetorial concluída com sucesso!")

# ==========================================
# Definição da DAG
# ==========================================
default_args = {
    'owner': 'time_de_dados',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'triageai_medallion_pipeline',
    default_args=default_args,
    description='Pipeline completo: Ingestão Kaggle -> MinIO (Medalhão) -> Embeddings Milvus',
    schedule_interval='@weekly', # Roda toda semana. Pode mudar para '@daily' ou None (apenas manual)
    start_date=datetime(2026, 4, 1),
    catchup=False,
    tags=['triageai', 'rag', 'minio', 'milvus'],
) as dag:

    task_bronze = PythonOperator(
        task_id='extracao_kaggle_bronze',
        python_callable=ingestao_bronze,
    )

    task_silver = PythonOperator(
        task_id='tratamento_silver',
        python_callable=processamento_silver,
    )

    task_gold = PythonOperator(
        task_id='preparacao_rag_gold',
        python_callable=processamento_gold,
    )

    task_milvus = PythonOperator(
        task_id='atualizacao_vetorial_milvus',
        python_callable=atualizacao_milvus,
    )

    # Ordem exata de execução:
    task_bronze >> task_silver >> task_gold >> task_milvus