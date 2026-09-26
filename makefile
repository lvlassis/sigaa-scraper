.PHONY: docs pages oracle tests

docs:
	mkdocs serve

pages:
	python tests/download_pages.py

oracle:
	python tests/generate_oracle.py

tests:
	pytest

