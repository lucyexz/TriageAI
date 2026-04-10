# 🏥 TriageAI

Sistema inteligente de triagem hospitalar utilizando **RAG (Retrieval-Augmented Generation)** para auxiliar na classificação de sintomas e priorização de atendimento.

---

## 🎯 Objetivo

O projeto tem como objetivo desenvolver um assistente capaz de:

- Analisar sintomas informados pelo usuário
- Sugerir possíveis condições médicas
- Classificar o nível de prioridade (triagem)
- Recomendar ações iniciais
- Basear respostas em dados médicos confiáveis

---

## 🧠 Tecnologias Utilizadas

- **LLM Local:** Ollama
- **API:** FastAPI
- **Vector Database:** Milvus
- **Banco Relacional:** PostgreSQL
- **Data Lake:** MinIO
- **MLOps:** MLflow
- **Interface:** Gradio
- **Containerização:** Docker Compose

---

## 📊 Metodologia

O projeto segue metodologia ágil baseada em:

- **Scrum**
- Sprints incrementais
- Versionamento de experimentos com MLflow

---

## 👥 Equipe

| Nome | RA | Turma |
|------|----|-------|
| Ana Lucia de Souza | 223530 | TIN1 |
| André Siqueira | 222686 | TIN1 |
| Felipe Rusig de Paiva | 212031 | TIN1 |
| Guilherme Massayuki Yokoda de Moraes | 223618 | TIN1 |
| Leonardo Rossi de Oliveira | 222410 | TIN1 |
| Tiago Tavares de Lima Gonçalves | 222566 | TIN1 |
| Pedro Rovira | 222956 | TIN1 |
| Rafael Rocha Leite | 222469 | TIN2 |
| Erick Miranda Viana | 211857 | TIN1 |
| Leonardo Kuntz Oliveira | 222831 | TIN1 |
| Victor Santos Borba | 211932 | TIN1 |

---

## dataset: https://www.kaggle.com/datasets/dhivyeshrk/diseases-and-symptoms-dataset

---

## 👑 Product Owner

**Ana Lucia de Souza**

---

## 🚀 Como Executar

### 🎨 Front-end
```bash
# acessar interface
http://localhost:7860
```

### 💻 Backend
```bash
# acessar API
http://localhost:8000
```

### 🧠 AI / RAG
```bash
# MLflow — acompanhar experimentos
http://localhost:5000

# Ollama — API de embeddings
http://localhost:11434

# Milvus — banco de vetores
localhost:19530

# Jupyter — notebooks de treino
http://localhost:8888  # token: mlops2025
```

### 📊 Data Engineering
```bash
# Airflow — pipelines de dados
http://localhost:8080  # admin / admin123

# MinIO — camadas bronze, silver e gold
http://localhost:9001  # minioadmin / minioadmin123
```

### 🚀 MLOps / Infra
```bash
# configurar variáveis de ambiente
cp .env.example .env

# dar permissão aos scripts
chmod +x init-scripts/postgres/01-create-databases.sh
chmod +x infra/minio/buckets.sh

# subir todo o ambiente
make up

# derrubar o ambiente
make down

# ver logs de um serviço específico
make logs s=mlflow

# verificar se os serviços estão respondendo
make health
```
