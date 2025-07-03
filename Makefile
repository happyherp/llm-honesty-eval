.PHONY: help install install-dev test lint format clean run-basic run-compare run-prompts run-batch

help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  install-dev  - Install with development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean artifacts"
	@echo ""
	@echo "Experiment scripts:"
	@echo "  run-basic    - Run basic evaluation example"
	@echo "  run-compare  - Compare different model combinations"
	@echo "  run-prompts  - Experiment with evaluation prompts"
	@echo "  run-batch    - Run batch evaluation on test dataset"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	flake8 common/ scripts/ tests/

format:
	black common/ scripts/ tests/
	isort common/ scripts/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f *.json *.csv

# Experiment runners
run-basic:
	python scripts/basic_evaluation.py

run-compare:
	python scripts/compare_models.py

run-prompts:
	python scripts/experiment_prompts.py

run-batch:
	python scripts/batch_evaluation.py