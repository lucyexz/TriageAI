# Product Backlog — TriageAI

## Visão do Produto

O TriageAI é um assistente inteligente de triagem hospitalar que utiliza Recuperação Aumentada por Geração (RAG) para apoiar médicos e enfermeiros na classificação de prioridade de pacientes. A partir dos sintomas relatados, o sistema sugere condições prováveis, atribui o nível de prioridade Manchester e recomenda ações iniciais — tudo processado localmente, sem dependência de APIs externas, garantindo privacidade dos dados clínicos.

---

## Personas

| Persona | Perfil | Objetivo principal |
|---------|--------|-------------------|
| **Médico Triador** | Médico responsável pela avaliação inicial na recepção de urgência | Obter sugestão rápida de condições e prioridade para agilizar o atendimento |
| **Enfermeiro de Triagem** | Enfermeiro que realiza a entrevista inicial com o paciente | Inserir sintomas e receber orientação de encaminhamento sem necessidade de conhecimento técnico do sistema |
| **Gestor Hospitalar** | Responsável pela governança, qualidade dos dados e conformidade | Auditar o pipeline de dados, monitorar experimentos de ML e garantir rastreabilidade |

---

## Épicos

| ID | Épico | Sprints relacionadas |
|----|-------|---------------------|
| E1 | Ingestão de dados (pipeline Medallion) | Sprint 3, Sprint 5 |
| E2 | Vetorização & RAG | Sprint 5, Sprint 6 |
| E3 | API & Integração | Sprint 7 |
| E4 | Interface clínica | Sprint 8 |
| E5 | Observabilidade & ML Tracking | Sprint 4 |
| E6 | Governança & Documentação | Sprint 1, Sprint 2, Sprint 3 |

---

## User Stories

| ID | Como | Quero | Para | MoSCoW | Sprint | Status |
|----|------|-------|------|--------|--------|--------|
| **E1 — Ingestão de dados** |
| US-01 | gestor hospitalar | ter um pipeline automatizado que baixa o dataset Kaggle e carrega na camada Bronze do MinIO | garantir reprodutibilidade e atualização periódica dos dados | Must | Sprint 3 | Done |
| US-02 | gestor hospitalar | ter a camada Bronze com os dados brutos preservados | possibilitar auditoria e reprocessamento sem perda da fonte original | Must | Sprint 3 | Done |
| US-03 | gestor hospitalar | ter a camada Silver com dados normalizados (lowercase, sem duplicatas, sintomas como lista) | garantir consistência na entrada do modelo e no pipeline de embeddings | Must | Sprint 3 | Done |
| US-04 | gestor hospitalar | ter a camada Gold com textos RAG formatados e prontos para vetorização | alimentar o índice vetorial com contexto clínico adequado | Must | Sprint 3 | Done |
| US-05 | gestor hospitalar | ter o pipeline orquestrado pelo Airflow com agendamento semanal | manter os dados atualizados automaticamente sem intervenção manual | Must | Sprint 3 | Done |
| **E2 — Vetorização & RAG** |
| US-06 | médico triador | ter embeddings gerados localmente via Ollama (nomic-embed-text, 768d) | evitar envio de dados clínicos sensíveis a serviços externos | Must | Sprint 5 | Done |
| US-07 | médico triador | ter os vetores indexados em Milvus com busca HNSW por similaridade cosseno | recuperar as condições clínicas mais relevantes para os sintomas informados | Must | Sprint 5 | Done |
| US-08 | médico triador | ter um pipeline RAG que combina busca vetorial com geração de linguagem | obter respostas fundamentadas no contexto clínico indexado, não em conhecimento genérico do LLM | Must | Sprint 6 | Done |
| US-09 | enfermeiro de triagem | que o sistema nunca mencione medicamentos ou tratamentos farmacológicos | garantir que o assistente não seja interpretado como prescrição médica ou automedicação | Must | Sprint 6 | Done |
| US-10 | médico triador | que o sistema traduza automaticamente as queries em português para inglês antes da busca | garantir que o mismatch de idioma entre queries PT e documentos EN não prejudique o retrieval | Must | Sprint 6 | Done |
| **E3 — API & Integração** |
| US-11 | desenvolvedor | ter o endpoint `POST /query` que recebe sintomas e retorna análise de triagem em JSON | integrar qualquer frontend ou sistema externo ao motor RAG | Must | Sprint 7 | Done |
| US-12 | desenvolvedor | ter o endpoint `GET /health` que retorna o status da API | monitorar a disponibilidade do serviço em produção | Must | Sprint 7 | Done |
| US-13 | desenvolvedor | ter o endpoint `GET /metadata` com informações sobre o estado do Milvus e modelos ativos | inspecionar o sistema sem precisar acessar os serviços internos | Should | Sprint 7 | Done |
| US-14 | desenvolvedor | ter validação de entrada e saída via Pydantic (schemas tipados) | garantir contratos de API e detectar erros de integração antecipadamente | Must | Sprint 7 | Done |
| US-15 | desenvolvedor | ter documentação Swagger gerada automaticamente em `/docs` | facilitar integrações futuras e reduzir tempo de onboarding | Should | Sprint 7 | Done |
| **E4 — Interface clínica** |
| US-16 | enfermeiro de triagem | ter uma interface web com campo de texto para inserir sintomas | usar o sistema sem conhecimento técnico, diretamente no navegador | Must | Sprint 8 | Done |
| US-17 | enfermeiro de triagem | ter casos clínicos pré-configurados (Meníngea, Cardíaca, Gripal, Abdômen, AVC) | agilizar testes e demonstrações sem digitar sintomas manualmente | Should | Sprint 8 | Done |
| US-18 | médico triador | receber a análise formatada com condições prováveis, nível de prioridade Manchester e ações iniciais | tomar decisões de encaminhamento de forma rápida e padronizada | Must | Sprint 8 | Done |
| **E5 — Observabilidade & ML Tracking** |
| US-19 | gestor hospitalar | ter experimentos de machine learning rastreados no MLflow com parâmetros e métricas | comparar modelos ao longo do tempo e justificar a escolha do modelo em produção | Must | Sprint 4 | Done |
| US-20 | gestor hospitalar | ter artefatos de modelo versionados no MinIO via MLflow | realizar rollback para versões anteriores do modelo em caso de regressão | Must | Sprint 4 | Done |
| US-21 | gestor hospitalar | ter o stack de monitoramento (Prometheus + Grafana) disponível | observar métricas de performance do sistema em produção | Should | Sprint 2 | Done |
| **E6 — Governança & Documentação** |
| US-22 | gestor hospitalar | ter documentação formal da arquitetura do sistema | facilitar onboarding da equipe e tomadas de decisão técnica | Must | Sprint 2 | Done |
| US-23 | gestor hospitalar | ter um catálogo de dados documentando o schema e linhagem de cada camada | atender requisitos de auditoria e garantir rastreabilidade dos dados | Must | Sprint 3 | Done |
| US-24 | gestor hospitalar | ter documentação de privacidade e conformidade com a LGPD | garantir que o tratamento de dados de sintomas esteja em conformidade legal | Must | Sprint 3 | Done |

---

## Critérios de Aceite (AC)

### AC1 — Pipeline de Treino + MLflow (Sprint 4)
Satisfeito quando:
- US-19 e US-20 estão implementadas
- Notebook `notebooks/training/treinamento_baseline.ipynb` roda ponta a ponta dentro do container Jupyter
- Experimento `triageai-baseline-oficial` aparece no painel MLflow (`http://localhost:5000`) com ao menos um run registrado
- Métricas `accuracy` e `f1_score` são logadas e o modelo é salvo como artefato no MinIO

### AC2 — API Funcional Documentada (Sprint 7)
Satisfeito quando:
- US-11, US-12, US-13, US-14 e US-15 estão implementadas
- `GET /health` retorna `{"status":"ok"}`
- `POST /query` com sintomas válidos retorna resposta de triagem com condição, prioridade e ações
- `GET /metadata` retorna `num_entities > 0`
- Swagger disponível em `http://localhost:8000/docs`

---

## Definição de Pronto (DoD)

Um item é considerado **Pronto** quando:

1. O código está commitado na branch correta e passou no CI (`.github/workflows/healthcheck.yml`)
2. Os arquivos de infraestrutura obrigatórios estão presentes (`docker-compose.yml`, `Makefile`, `monitoring/prometheus.yml`, etc.)
3. O serviço correspondente sobe com `make up` sem erros
4. O comportamento esperado foi verificado manualmente (ou via testes automatizados, quando existentes)
5. A documentação relevante foi atualizada (`CLAUDE.md`, `README.md` ou `docs/`)
6. Não há credenciais ou dados sensíveis expostos no commit
