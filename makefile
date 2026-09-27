.PHONY: setup docs pages oracle tests

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e . --group dev

docs:
	mkdocs serve

deploy-docs:
	mkdocs gh-deploy

pages:
	python tests/download_pages.py

oracle:
	python tests/generate_oracle.py

tests:
	pytest

