# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
make tests
# or directly:
pytest

# Run a single test file
pytest tests/scraper/test_scraper.py

# Run a single test class or method
pytest tests/scraper/test_scraper.py::TestAtividades
pytest tests/scraper/test_scraper.py::TestAtividades::test_tipo_alerta_com_img

# Serve documentation locally
make docs

# Download a live fixture (requires SIGAA_COOKIES env var)
make pages
# Accepts --output to specify the path:
SIGAA_COOKIES="..." python tests/download_pages.py --output tests/pages/minha-pagina.html

# Generate YAML oracle files for HTML fixtures without one
make oracle
# Force-overwrite existing oracles:
python tests/generate_oracle.py --force
```

Dependencies are managed with `uv` (see `pyproject.toml`). Dev extras: `pytest`, `python-dotenv`, `pyyaml`, `mkdocs-material`, `mkdocstrings`.

## Architecture

The library scrapes the authenticated student portal of SIGAA UFG (`sigaa.sistemas.ufg.br`). Authentication is cookie-based — the caller passes the raw `Cookie` header string (containing `_ufg_br_sess` and `JSESSIONID`) to `SigaaScraper`.

### Module layout

- **`sigaa_scraper/pages.py`** — thin HTTP layer. `fetch_pagina_discente(cookies)` does the single GET request and returns raw HTML.
- **`sigaa_scraper/scraper.py`** — all parsing logic lives here as static methods on `SigaaScraper`. `get_discente()` calls `fetch_pagina_discente`, validates the response, then runs `_parse_discente` which delegates to per-section helpers (`_turmas`, `_atividades`, `_atualizacoes_turma`, `_topicos_forum`). Parsing uses `parsel.Selector` (XPath).
- **`sigaa_scraper/models.py`** — plain `@dataclass` types: `Discente`, `Turma`, `Atividade`, `AtualizacaoTurma`, `TopicoForum`. `Discente` is the root object returned by `get_discente()`.
- **`sigaa_scraper/__init__.py`** — public API surface (`SigaaScraper`, `SessionExpiredError`, `UnexpectedPageError`, and the four model types).

### Testing strategy

Tests are divided into two layers:

1. **Unit tests** (`tests/scraper/test_scraper.py`) — inline HTML snippets, test each static method in isolation. No fixtures needed, no network.
2. **Page vector tests** (`tests/scraper/test_pages.py`) — parametrized over `tests/pages/*.html` + corresponding `tests/pages/*.yaml` oracle files. Each pair is a sanitized real page + expected parse result. `conftest.py` provides the `page_vectors()` loader.

To add a new real-page test case:
1. `make pages` (needs `SIGAA_COOKIES`) → saves an anonymized HTML to `tests/pages/`.
2. `make oracle` → generates the matching YAML.
3. Run `pytest` — the new pair is picked up automatically.

### Key implementation details

- `Atividade.tipo` is `"alerta"` when the row contains `prova_semana.png` (exam this week), `"normal"` otherwise. This is the distinction being fixed on the current branch (`fix/atividades-x-provas`).
- All dates/datetimes are returned as ISO 8601 strings (not `datetime` objects). Timestamps include BRT offset (`-03:00`); date-only fields are `YYYY-MM-DD`.
- The email normalization in `_parse_discente` replaces whatever domain SIGAA returns with `@discente.ufg.br`.
- Session expiry detection: if the response is shorter than 500 chars AND contains the JS alert string, `SessionExpiredError` is raised. Any page missing all three `_PAGE_MARKERS` raises `UnexpectedPageError`.
