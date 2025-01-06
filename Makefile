SHELL := /bin/bash
# =============================================================================
# Variables
# =============================================================================

.DEFAULT_GOAL:=help
.ONESHELL:
.EXPORT_ALL_VARIABLES:
MAKEFLAGS += --no-print-directory

# Define colors and formatting
BLUE := $(shell printf "\033[1;34m")
GREEN := $(shell printf "\033[1;32m")
RED := $(shell printf "\033[1;31m")
YELLOW := $(shell printf "\033[1;33m")
NC := $(shell printf "\033[0m")
INFO := $(shell printf "$(BLUE)ℹ$(NC)")
OK := $(shell printf "$(GREEN)✓$(NC)")
WARN := $(shell printf "$(YELLOW)⚠$(NC)")
ERROR := $(shell printf "$(RED)✖$(NC)")

.PHONY: help
help:                                               ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


# =============================================================================
# Developer Utils
# =============================================================================
.PHONY: install-uv
install-uv:                                         ## Install latest version of uv
	@echo "${INFO} Installing uv..."
	@curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
	@uv tool install nodeenv >/dev/null 2>&1
	@echo "${OK} UV installed successfully"

.PHONY: install
install: destroy clean                              ## Install the project, dependencies, and pre-commit for local development
	@echo "${INFO} Starting fresh installation..."
	@uv python pin 3.12 >/dev/null 2>&1
	@uv venv >/dev/null 2>&1
	@uv sync --all-extras --dev
	@if ! command -v npm >/dev/null 2>&1; then \
		echo "${INFO} Installing Node environment... 📦"; \
		uvx nodeenv .venv --force --quiet >/dev/null 2>&1; \
	fi
	@NODE_OPTIONS="--no-deprecation --disable-warning=ExperimentalWarning" npm install --no-fund >/dev/null 2>&1
	@echo "${OK} Installation complete! 🎉"

.PHONY: upgrade
upgrade:                                            ## Upgrade all dependencies to the latest stable versions
	@echo "${INFO} Updating all dependencies... 🔄"
	@uv lock --upgrade
	@NODE_OPTIONS="--no-deprecation --disable-warning=ExperimentalWarning" uv run npm upgrade --latest
	@echo "${OK} Dependencies updated 🔄"
	@NODE_OPTIONS="--no-deprecation --disable-warning=ExperimentalWarning" uv run pre-commit autoupdate
	@echo "${OK} Updated Pre-commit hooks 🔄"

.PHONY: clean
clean:                                              ## Cleanup temporary build artifacts
	@echo "${INFO} Cleaning working directory..."
	@rm -rf pytest_cache .ruff_cache .hypothesis build/ -rf dist/ .eggs/ .coverage coverage.xml coverage.json htmlcov/ .pytest_cache tests/.pytest_cache tests/**/.pytest_cache .mypy_cache .unasyncd_cache/ .auto_pytabs_cache node_modules >/dev/null 2>&1
	@find . -name '*.egg-info' -exec rm -rf {} + >/dev/null 2>&1
	@find . -type f -name '*.egg' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*.pyc' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*.pyo' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '*~' -exec rm -f {} + >/dev/null 2>&1
	@find . -name '__pycache__' -exec rm -rf {} + >/dev/null 2>&1
	@find . -name '.ipynb_checkpoints' -exec rm -rf {} + >/dev/null 2>&1
	@echo "${OK} Working directory cleaned"

.PHONY: destroy
destroy:                                            ## Destroy the virtual environment
	@echo "${INFO} Destroying virtual environment... 🗑️"
	@uv run pre-commit clean >/dev/null 2>&1
	@rm -rf .venv
	@echo "${OK} Virtual environment destroyed 🗑️"

.PHONY: lock
lock:                                              ## Rebuild lockfiles from scratch, updating all dependencies
	@echo "${INFO} Rebuilding lockfiles... 🔄"
	@uv lock --upgrade >/dev/null 2>&1
	@echo "${OK} Lockfiles updated"

.PHONY: release
release:                                           ## Bump version and create release tag
	@echo "${INFO} Preparing for release... 📦"
	@make clean
	@uv run bump-my-version bump $(bump)
	@make build
	@echo "${OK} Release complete 🎉"


# =============================================================================
# Tests, Linting, Coverage
# =============================================================================
.PHONY: mypy
mypy:                                              ## Run mypy
	@echo "${INFO} Running mypy... 🔍"
	@uv run dmypy run
	@echo "${OK} Mypy checks passed ✨"

.PHONY: mypy-nocache
mypy-nocache:                                      ## Run Mypy without cache
	@echo "${INFO} Running mypy without cache... 🔍"
	@uv run mypy
	@echo "${OK} Mypy checks passed ✨"

.PHONY: pyright
pyright:                                           ## Run pyright
	@echo "${INFO} Running pyright... 🔍"
	@uv run pyright
	@echo "${OK} Pyright checks passed ✨"

.PHONY: type-check
type-check: mypy pyright                           ## Run all type checking

.PHONY: pre-commit
pre-commit:                                        ## Runs pre-commit hooks; includes ruff formatting and linting, codespell
	@echo "${INFO} Running pre-commit checks... 🔎"
	@uv run pre-commit run --color=always --all-files
	@echo "${OK} Pre-commit checks passed ✨"

.PHONY: fix
fix:                                               ## Run formatting scripts
	@echo "${INFO} Running code formatters... 🔧"
	@uv run ruff check --fix --unsafe-fixes
	@echo "${OK} Code formatting complete ✨"

.PHONY: lint
lint: pre-commit type-check                        ## Run all linting

.PHONY: test
test:                                              ## Run the tests
	@echo "${INFO} Running test cases... 🧪"
	@uv run pytest tests -n 2 --quiet
	@echo "${OK} Tests passed ✨"
