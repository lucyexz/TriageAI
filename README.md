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

## 🎲 Dataset

```bash
🔗 https://www.kaggle.com/datasets/karthikudyawar/disease-symptom-prediction
```

O dataset Disease Symptom Prediction reúne dados de sintomas associados a diferentes doenças, com o objetivo de treinar modelos de Machine Learning capazes de prever uma possível enfermidade a partir dos sintomas informados pelo usuário. Ele é adequado para projetos de triagem inicial, como o TriageAI, pois permite transformar sintomas em variáveis de entrada e gerar uma classificação provável da condição do paciente. Em bases semelhantes desse mesmo conjunto de dados, os sintomas aparecem como atributos binários ou categóricos, e a doença prevista é representada pela coluna-alvo, geralmente chamada de prognosis. Alguns conjuntos relacionados possuem cerca de 132 sintomas e 42 classes de doenças, divididos em arquivos de treino e teste.

---

## 🧠 Tecnologias Utilizadas

- **LLM Local:** Ollama
- **API:** FastAPI
- **Vector Database:** Milvus
- **Banco Relacional:** PostgreSQL
- **Data Lake:** MinIO
- **MLOps:** MLflow
- **Interface:** HTML/CSS/JS
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

## 👑 Product Owner

**Ana Lucia de Souza**

---

## 🚀 Como Executar

### ⚙️ Setup Inicial (primeira vez)
```bash
# pré-requisitos: Docker e Docker Compose instalados

cp .env.example .env

chmod +x init-scripts/postgres/01-create-databases.sh
chmod +x infra/minio/buckets.sh

make up       # sobe todos os 14 serviços (~2 min na primeira vez)
make health   # confirma que todos respondem
```

### 🎨 Front-end
```bash
# acessar interface
http://localhost:7860
```

### 💻 Backend
```bash
# acessar API
http://localhost:8000
```<img width="4763" height="2133" alt="mermaid-diagram (1)" src="https://github.com/user-attachments/assets/cdd34574-4f96-43c1-a7e7-555fcf181a7b" />


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
# derrubar o ambiente
make down

# rebuild das imagens sem cache
make build

# restart limpo (destrói volumes)
make reset

# ver logs de um serviço específico
make logs s=mlflow

# verificar se os serviços estão respondendo
make health

# shell em um container
make shell s=api
```
