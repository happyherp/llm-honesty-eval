.PHONY: install install-dev test test-unit test-integration lint format clean build help

# Default target
help:
	@echo "Available commands:"
	@echo "  install       Install package in development mode"
	@echo "  install-dev   Install package with development dependencies"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  lint          Run linting (flake8, mypy)"
	@echo "  format        Format code (black, isort)"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-unit:
	pytest -m "not integration"

test-integration:
	pytest -m integration

lint:
	flake8 src tests
	mypy src

format:
	black src tests
	isort src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build