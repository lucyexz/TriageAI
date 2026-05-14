# Governança de Dados — TriageAI

## 1. Catálogo de Dados

### 1.1 Camada Bronze — Dados Brutos

| Atributo | Valor |
|----------|-------|
| Origem | Kaggle: `dhivyeshrk/diseases-and-symptoms-dataset` |
| Arquivo | `Final_Augmented_dataset_Diseases_and_Symptoms.csv` |
| Caminho MinIO | `s3://bronze/dataset_doencas_sintomas.csv` |
| Formato | CSV, separador `,`, encoding UTF-8 |
| Volume aproximado | ~246.945 linhas, ~134 colunas |
| Idioma | Inglês |
| Atualização | Semanal (task `ingestao_bronze` na DAG `triageai_medallion_pipeline`) |

**Schema bruto (principais colunas):**

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `diseases` | string | Nome da doença |
| `Symptom_1` … `Symptom_N` | binário (0/1) | Presença de cada sintoma |

---

### 1.2 Camada Silver — Dados Normalizados

| Atributo | Valor |
|----------|-------|
| Caminho MinIO | `s3://silver/doencas_sintomas_limpo.csv` |
| Formato | CSV |
| Gerado por | Task `processamento_silver` (DAG Airflow) |

**Schema limpo:**

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `diseases` | string | Nome da doença (lowercase, strip) |
| `sintomas` | list[string] | Lista de sintomas presentes (colunas binárias desmontadas, `_` trocado por espaço, lowercase) |

**Regras de normalização aplicadas:**
- `diseases`: `str.lower().str.strip()`
- Sintomas: colunas com valor `1` são extraídas como lista; `_` → espaço; lowercase
- Colunas duplicadas com sufixo `.N` (ex: `Symptom_1.1`) são descartadas

---

### 1.3 Camada Gold — Dados para RAG

| Atributo | Valor |
|----------|-------|
| Caminho MinIO | `s3://gold/textos_rag.csv` |
| Formato | CSV |
| Gerado por | Task `processamento_gold` (DAG Airflow) |

**Schema:**

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `diseases` | string | Nome da doença (herdado do Silver) |
| `sintomas` | list[string] | Lista de sintomas (herdado do Silver) |
| `texto` | string | Texto RAG formatado (ver template abaixo) |

**Template de geração do campo `texto` (função `gerar_texto` em `airflow/dags/pipeline_triageai.py`):**

```
{doenca} is a condition that may present symptoms such as {sintomas}.
Individuals experiencing these symptoms may be associated with this condition.
This information is for educational purposes only and does not replace professional medical diagnosis.
```

> **Nota:** O texto está em inglês pois o dataset Kaggle é em inglês. A query do usuário é traduzida PT→EN antes de gerar o embedding (`rag/query.py`, função `_translate_to_english`), mantendo compatibilidade semântica.

---

### 1.4 Índice Vetorial — Milvus

| Atributo | Valor |
|----------|-------|
| Coleção | `triageai_knowledge_base` |
| Volume | ~493.390 entidades |
| Gerado por | Task `atualizacao_milvus` (DAG Airflow) |

**Schema da coleção:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INT64, PK auto-increment | Identificador único |
| `disease` | VARCHAR(200) | Nome da doença |
| `texto_rag` | VARCHAR(2500) | Texto RAG completo |
| `embedding` | FLOAT_VECTOR(768) | Vetor gerado por `nomic-embed-text` |

**Índice:** HNSW, métrica COSINE, `M=8`, `efConstruction=64`

---

## 2. Versionamento

O MinIO não possui versionamento nativo habilitado neste ambiente. A estratégia de versionamento adotada é baseada em **run_ids do Airflow**:

- Cada execução da DAG gera um `run_id` único com timestamp (ex: `scheduled__2026-05-14T00:00:00+00:00`)
- Os logs de cada run ficam em `airflow/logs/dag_id=triageai_medallion_pipeline/`
- Os arquivos no MinIO são sobrescritos a cada run (não há histórico de versões dos CSVs)

**Estratégia de retenção recomendada (a implementar):**
- Manter os 3 últimos runs de dados no MinIO com sufixo de data no path (ex: `s3://gold/textos_rag_20260514.csv`)
- Logs do Airflow: retenção de 30 dias (configurar em `airflow.cfg`)

---

## 3. Linhagem de Dados (Data Lineage)

```
[Kaggle Dataset]
      │
      ▼ task: ingestao_bronze
[MinIO: bronze/dataset_doencas_sintomas.csv]
      │
      ▼ task: processamento_silver
[MinIO: silver/doencas_sintomas_limpo.csv]
      │
      ▼ task: processamento_gold
[MinIO: gold/textos_rag.csv]
      │
      ▼ task: atualizacao_milvus
[Milvus: triageai_knowledge_base (~493k entidades)]
      │
      ▼ API: POST /query (runtime)
[Resposta de Triagem para o Usuário]
```

**Responsável por cada hop:**

| Origem | Destino | Task Airflow | Arquivo |
|--------|---------|-------------|---------|
| Kaggle | Bronze | `ingestao_bronze` | `pipeline_triageai.py:22` |
| Bronze | Silver | `processamento_silver` | `pipeline_triageai.py:33` |
| Silver | Gold | `processamento_gold` | `pipeline_triageai.py:56` |
| Gold | Milvus | `atualizacao_milvus` | `pipeline_triageai.py:78` |

---

## 4. Qualidade de Dados

### Checks existentes (implementados no pipeline)

| Check | Onde | Descrição |
|-------|------|-----------|
| Colunas duplicadas descartadas | Silver | Regex `\.\d+$` remove colunas como `Symptom_1.1` |
| Normalização de texto | Silver | lowercase + strip + substituição de `_` |
| Listas vazias permitidas | Silver | Não há validação explícita de `sintomas` não-vazia |

### Checks propostos (a implementar)

| Check | Camada | Critério |
|-------|--------|----------|
| Contagem mínima de linhas | Bronze/Silver/Gold | Alertar se `len(df) < 100.000` |
| Ausência de nulos em `diseases` | Silver/Gold | `df['diseases'].isna().sum() == 0` |
| Lista de sintomas não vazia | Silver/Gold | `df['sintomas'].apply(len).min() > 0` |
| Vetores indexados > 0 | Milvus | `collection.num_entities > 0` após indexação |

---

## 5. Privacidade e LGPD

### Dataset

- O dataset Kaggle (`dhivyeshrk/diseases-and-symptoms-dataset`) é **público e sintético** — não contém dados de pacientes reais, não há PII (Informação Pessoalmente Identificável).
- Não há nome, CPF, data de nascimento, endereço ou qualquer identificador pessoal no dataset.

### Dados em runtime

- O endpoint `POST /query` recebe sintomas em texto livre inseridos pelo usuário.
- **Verificado em `api/routes/triage.py`**: a rota chama `run_rag(request.symptoms)` e retorna a resposta — **não há persistência do conteúdo da query** em banco de dados, logs estruturados ou qualquer armazenamento externo.
- O processamento é inteiramente local (Ollama rodando on-premise).

### Classificação dos dados em runtime

| Dado | Categoria LGPD | Persistido? |
|------|---------------|------------|
| Sintomas enviados via `POST /query` | Dado de saúde (Art. 5, II) | **Não** |
| Resposta da triagem | Dado gerado pelo sistema | **Não** |
| Logs do Docker (stdout) | Operacional | Sim (efêmero, sem conteúdo clínico estruturado) |

> **Recomendação:** Em deploy de produção, configurar retenção máxima de 24h para logs de stdout do container `api` e garantir que nenhum middleware de logging capture o campo `symptoms` da requisição.

---

## 6. RACI

| Responsabilidade | Gestor Hospitalar | Médico Triador | Desenvolvedor |
|-----------------|:-----------------:|:--------------:|:-------------:|
| Acionar pipeline de ingestão | A | — | R |
| Validar qualidade dos dados (Silver/Gold) | A | C | R |
| Monitorar índice Milvus | C | — | R |
| Manter modelos MLflow atualizados | A | — | R |
| Aprovar promoção de modelo para produção | A | C | R |
| Garantir conformidade LGPD | R | C | C |
| Atualizar documentação de governança | A | — | R |

**Legenda:** R = Responsável | A = Aprovador | C = Consultado

---

## 7. Política de Modelos (MLflow)

### Rastreamento

- Todos os experimentos de treino são registrados no experimento `triageai-baseline-oficial` (MLflow tracking URI: `http://mlflow:5000`)
- Parâmetros obrigatórios a logar: `model_type`, `vectorizer`, `dataset_version`, `dataset_path`
- Métricas obrigatórias: `accuracy`, `f1_score` (weighted)
- Métricas recomendadas: `precision_weighted`, `recall_weighted`

### Artefatos

- Modelos salvos via `mlflow.sklearn.log_model(pipeline, "modelo_classificacao")`
- Artefatos persistidos no MinIO (`s3://mlflow-artifacts/`)

### Promoção

- O modelo com maior `f1_score` (weighted) no conjunto de teste é considerado o "campeão"
- A promoção para produção deve ser feita via MLflow Model Registry (`mlflow.register_model(...)`)
- Mínimo de 2 runs comparativos antes de promover um novo campeão

### Retenção

- Manter todos os runs no MLflow (não deletar — serve como histórico de experimentos)
- Artefatos no MinIO: retenção indefinida (storage é local, sem custo de cloud)
