include .env
export

help: ## display this help screen
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## set up local environment for pipeline development
	@set -e && \
	git init && \
	uv sync --all-groups

clean: ## clean unneeded files
	@uv run pyclean . -d all -e *.xml -e local_outputs -y

lint: ## lint files with ruff
	uv run ruff check --fix
	uv run pyrefly check
