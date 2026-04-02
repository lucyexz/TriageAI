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

## 👑 Product Owner

**Ana Lucia de Souza**

---

## 🚀 Como Executar

```bash
# subir ambiente
docker-compose up -d

# acessar API
http://localhost:8000

# acessar interface
http://localhost:7860

## 🛠️ Infra — Como Subir o Ambiente

> Essa seção é mantida pelo time de MLOps/Infra.
> Os outros times não precisam mexer nesses arquivos.

### Pré-requisitos
- [Docker](https://www.docker.com/) instalado
- [Git](https://git-scm.com/) instalado

### 1. Configure as variáveis de ambiente
```bash
cp .env.example .env
```

### 2. Dê permissão aos scripts
```bash
chmod +x init-scripts/postgres/01-create-databases.sh
chmod +x infra/minio/buckets.sh
```

### 3. Suba o ambiente
```bash
make up
```

### 4. Serviços disponíveis

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin123 |
| MLflow | http://localhost:5000 | — |
| Airflow | http://localhost:8080 | admin / admin123 |
| Jupyter Lab | http://localhost:8888 | token: mlops2025 |
| Grafana | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | — |
| Milvus gRPC | localhost:19530 | — |
| Ollama | http://localhost:11434 | — |
| PostgreSQL | localhost:5432 | admin / admin123 |

### 5. Outros comandos úteis
```bash
# derrubar o ambiente
make down

# ver logs de um serviço específico
make logs s=mlflow

# verificar se os serviços estão respondendo
make health
```
---
