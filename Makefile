# Makefile — Projeto Triagem com IA (MLOps/Infra)
# Uso: make <comando>

.PHONY: up down restart logs ps clean pull help

## Informacoes de todos os serviços
up:
	@echo "Subindo o ambiente MLOps..."
	docker compose up -d
	@echo ""
	@echo "Ambiente disponível em:"
	@echo "   MinIO Console  → http://localhost:9001  (minioadmin / minioadmin123)"
	@echo "   MLflow         → http://localhost:5000"
	@echo "   Airflow        → http://localhost:8080  (admin / admin123)"
	@echo "   Jupyter Lab    → http://localhost:8888  (token: mlops2025)"
	@echo "   Grafana        → http://localhost:3000  (admin / admin123)"
	@echo "   Prometheus     → http://localhost:9090"
	@echo "   Milvus gRPC    → localhost:19530"
	@echo "   Ollama API     → http://localhost:11434"
	@echo "   PostgreSQL     → localhost:5432 (admin / admin123)"

## Sobe somente a infra base (sem Airflow e Jupyter)
up-infra:
	docker compose up -d postgres minio minio-init mlflow etcd minio-milvus milvus redis

down:
	docker compose down

## Da um stop e remove volumes !apaga todos os dados!
clean:
	@echo "⚠️  Isso vai apagar TODOS os dados. Tem certeza? [y/N]"
	@read ans; [ $${ans:-N} = y ] && docker compose down -v || echo "Operação cancelada."

## Reinicia um serviço específico
restart:
	docker compose restart $(s)

## Mostra logs de todos os serviços
	docker compose logs -f $(s)

## listagem de status de todos os containers
ps:
	docker compose ps

## pull de todas as imagens sem subir
pull:
	docker compose pull

## abre shell no container especificado
shell:
	docker compose exec $(s) /bin/sh

## roda os health checks de todos os serviços
health:
	@echo "Verificando status dos serviços..."
	@docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

help:
	@grep -E '^## ' Makefile | sed 's/## //'