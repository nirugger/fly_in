export UV_CACHE_DIR=$(PWD)/.cache/uv

.PHONY: all install run debug clean lint lint-strict

UV := uv run

RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[38;2;253;253;100m
RESET := \033[0m

all: install run clean

install:
	@echo "$(YELLOW)→ Installing dependencies...$(RESET)"
	uv sync
	@echo "$(GREEN)✓ Dependencies installed.$(RESET)"

run:
	$(UV) python3 -m main maps/test/parsing_test.txt

debug:
	$(UV) python3 -m pdb main maps/test/parsing_test.txt

clean:
	@find . -type d -name "__pycache__" -not -path "./.venv/*" | xargs rm -rf
	@find . -type d -name ".mypy_cache" -not -path "./.venv/*" | xargs rm -rf
	@find . -type d -name "*.egg-info"  -not -path "./.venv/*" | xargs rm -rf

lint:
	@echo "$(YELLOW)→ Running flake8...$(RESET)"
	$(UV) flake8 src/
	@echo "$(YELLOW)→ Running mypy...$(RESET)"
	$(UV) mypy src/ \
				--warn-return-any \
				--warn-unused-ignores \
				--ignore-missing-imports \
				--disallow-untyped-defs \
				--check-untyped-defs
	@echo "$(GREEN)✓ Lint passed.$(RESET)"

lint-strict:
	@echo "$(YELLOW)→ Running flake8 (strict)...$(RESET)"
	$(UV) flake8 src/
	@echo "$(YELLOW)→ Running mypy --strict...$(RESET)"
	$(UV) mypy src/ --strict
	@echo "$(YELLOW)→ Running pydocstyle...$(RESET)"
	$(UV) pydocstyle src/
	@echo "$(GREEN)✓ Strict lint passed.$(RESET)"