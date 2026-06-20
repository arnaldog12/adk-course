# Atalhos opcionais para macOS/Linux. No Windows, use os comandos `uv run ...`
# diretamente (veja o README).
-include .env
export

help: ## display this help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## set up local environment for pipeline development
	uv sync --all-groups

dev: ## start the ADK web interface (http://localhost:8000)
	uv run adk web

test: ## run the test suite
	uv run pytest

clean: ## clean unneeded files
	@uv run pyclean . -d all -e *.xml -e local_outputs -y

lint: ## lint files with ruff
	uv run ruff check --fix
	uv run pyrefly check
