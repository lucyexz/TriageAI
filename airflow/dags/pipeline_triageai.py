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
    from embeddings.generate import get_client, generate_embeddings
    from embeddings.indexing import connect, ensure_collection_exists, upsert_batch, create_index_and_load

    print("Iniciando geração de embeddings e indexação incremental no Milvus...")
    df_gold = pd.read_csv("s3://gold/textos_rag.csv", storage_options=MINIO_OPTIONS)

    connect()
    collection = ensure_collection_exists()
    ollama_client = get_client()

    BATCH_SIZE = 500
    total = len(df_gold)
    total_inserted = 0
    for i in range(0, total, BATCH_SIZE):
        batch = df_gold.iloc[i : i + BATCH_SIZE]
        embeddings = generate_embeddings(batch["texto"].tolist(), ollama_client)
        inserted = upsert_batch(
            collection,
            batch["diseases"].tolist(),
            batch["texto"].tolist(),
            embeddings,
        )
        total_inserted += inserted
        print(f"[Milvus] Batch {i // BATCH_SIZE + 1}: {min(i + BATCH_SIZE, total)}/{total} processados, {inserted} novos inseridos")

    if total_inserted > 0:
        create_index_and_load(collection)
        print(f"Indexação incremental concluída: {total_inserted} novos documentos adicionados.")
    else:
        print("Nenhum documento novo — base Milvus já está atualizada.")

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