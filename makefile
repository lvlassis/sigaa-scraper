.PHONY: setup docs pages oracle tests build clean

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

build:
	uv pip install --system pyinstaller 2>/dev/null || pip install pyinstaller
	pyinstaller --onefile --name sigaa-scraper --distpath out --workpath .pyinstaller-work sigaa_scraper/__main__.py
	rm -rf .pyinstaller-work sigaa-scraper.spec

clean:
	rm -rf out .pyinstaller-work sigaa-scraper.spec

