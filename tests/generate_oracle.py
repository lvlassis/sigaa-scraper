"""
Gera automaticamente os arquivos YAML de oracle para páginas em tests/pages/
que ainda não possuem um oracle correspondente.

Uso:
    python tests/generate_oracle.py            # apenas páginas sem yaml
    python tests/generate_oracle.py --force    # sobrescreve yamls existentes
"""

import argparse
import dataclasses
import sys
from pathlib import Path

import yaml
from parsel import Selector

from sigaa_scraper.scraper_discente import SigaaScraper

_PAGES_DIR = Path(__file__).parent / "pages"

_SCALAR_FIELDS = (
    "nome", "nome_titulo", "matricula", "curso", "nivel", "status",
    "email", "entrada", "ip", "ti", "ta", "qr", "mge", "mre", "pmf",
    "ch_exigida", "ch_cursada",
)
_LIST_FIELDS = ("turmas", "atividades", "atualizacoes_turma", "topicos_forum")


def _to_oracle(discente) -> dict:
    d = dataclasses.asdict(discente)
    result = {field: d[field] for field in _SCALAR_FIELDS}
    for field in _LIST_FIELDS:
        items = d[field]
        result[field] = {"count": len(items), "items": items}
    return result


def generate(force: bool) -> None:
    html_paths = sorted(_PAGES_DIR.glob("*.html"))
    if not html_paths:
        print("Nenhuma página encontrada em tests/pages/.")
        sys.exit(0)

    generated = skipped = 0
    for html_path in html_paths:
        yaml_path = html_path.with_suffix(".yaml")
        if yaml_path.exists() and not force:
            print(f"  skip  {yaml_path.name}  (já existe; use --force para sobrescrever)")
            skipped += 1
            continue

        discente = SigaaScraper._parse_discente(Selector(text=html_path.read_text(encoding="utf-8")))
        oracle = _to_oracle(discente)
        yaml_path.write_text(
            yaml.dump(oracle, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        print(f"  gerado  {yaml_path.name}")
        generated += 1

    print(f"\n{generated} gerado(s), {skipped} ignorado(s).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera oracles YAML para as páginas de teste.")
    parser.add_argument("--force", action="store_true", help="Sobrescreve YAMLs existentes.")
    args = parser.parse_args()
    generate(args.force)


if __name__ == "__main__":
    main()
