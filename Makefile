.PHONY: help install dev test lint format clean run-bot run-api

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync

dev: ## Install all dependencies (including dev tools)
	uv sync --all-extras

test: ## Run tests
	uv run pytest -v

lint: ## Run linter (ruff check)
	uv run ruff check src/ tests/

format: ## Format code (ruff format)
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

typecheck: ## Run type checker (mypy)
	uv run mypy src/

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	rm -rf dist/ build/ *.egg-info/

# ── App commands (V1) ──
run-bot: ## Start the Telegram bot
	uv run python -m researchos.bot.main

run-api: ## Start the FastAPI server
	uv run uvicorn researchos.api.main:app --reload --port 8000
