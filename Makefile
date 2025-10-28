ifeq (,$(wildcard .env))
$(error .env file is missing. Please create one based on .env.example)
endif

include .env

CHECK_DIRS := .

# --- Ruff ---

format-fix:
	uv run ruff format $(CHECK_DIRS) 
	uv run ruff check --select I --fix

lint-fix:
	uv run ruff check --fix

format-check:
	uv run ruff format --check $(CHECK_DIRS) 
	uv run ruff check -e
	uv run ruff check --select I -e

lint-check:
	uv run ruff check $(CHECK_DIRS)

# --- RAG Indexing ---

index-qdrant:
	@echo 'Indexing documents to Qdrant...'
	uv run python -c "from telegram_agent_aws.application.rag_indexing_service.index_documents import index_documents; index_documents()"
	@echo 'Documents indexed successfully.'

# --- Fully Automated Local Development ---
.PHONY: dev
dev:
	@echo "Iniciando entorno de desarrollo local completo..."
	@echo "Lanzando servidor, ngrok y configurando webhook..."
	@uv run python scripts/start_local.py