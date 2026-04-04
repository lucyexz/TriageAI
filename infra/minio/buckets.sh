#!/bin/bash

# Cria os buckets das camadas medallion e artefatos no MinIO

# sprint 3 (mlops infra)

set -e

echo "Aguardando MinIO ficar disponível..."
sleep 5

mc alias set local http://minio:9000 minioadmin minioadmin123

echo "Criando buckets..."

# Camadas medallion
mc mb --ignore-existing local/bronze
mc mb --ignore-existing local/silver
mc mb --ignore-existing local/gold

# Artefatos MLflow
mc mb --ignore-existing local/mlflow-artifacts

# Backup Milvus
mc mb --ignore-existing local/milvus-backup

echo ""
echo "   Buckets criados com sucesso:"
echo "   bronze            → dados brutos (ingestão)"
echo "   silver            → dados limpos (transformados)"
echo "   gold              → dados prontos (features)"
echo "   mlflow-artifacts  → modelos e artefatos do MLflow"
echo "   milvus-backup     → backup dos índices vetoriais"
echo ""

mc ls local 