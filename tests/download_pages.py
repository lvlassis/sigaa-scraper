"""
Baixa a página discente do SIGAA e salva como fixture HTML para os testes.

Uso:
    SIGAA_COOKIES="..." python tests/download_pages.py
    SIGAA_COOKIES="..." python tests/download_pages.py --output tests/pages/discente.html

Obtendo os cookies:
    1. Faça login no SIGAA pelo navegador.
    2. Abra DevTools (F12) > aba Network.
    3. Recarregue a página e clique em qualquer requisição ao sigaa.sistemas.ufg.br.
    4. Copie o valor completo do header "Cookie" e defina como SIGAA_COOKIES.
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from parsel import Selector

from dotenv import load_dotenv

from sigaa_scraper.pages import fetch_pagina_discente
from sigaa_scraper.scraper import SigaaScraper

_TS = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
_DEFAULT_OUTPUT = Path(__file__).parent / "pages" / f"discente-{_TS}.html"


def _filtrar_dados_pessoais(html: str):
    scraper = SigaaScraper
    discente = scraper._parse_discente(Selector(text=html))

    html = html.replace(discente.nome, "JOAO JOAQUIM JOSE")
    html = html.replace(discente.nome_titulo, "JOAO JOAQUIM JOSE")
    html = html.replace(discente.matricula, "040028922")
    html = html.replace(discente.email.split("@")[0], "aluno_anonimo")
    for m in re.finditer(r'idusuario=(\d+)', html):
        html = html.replace(m.group(1), "00000000")
    for topico in discente.topicos_forum:
        if topico.autor_nome:
            html = html.replace(topico.autor_nome, "AUTOR ANONIMO")
        if topico.autor:
            html = html.replace(topico.autor, "autor_anonimo")
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa a página discente do SIGAA como fixture.")
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help=f"Caminho de saída (padrão: {_DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    load_dotenv()
    cookies = os.environ.get("SIGAA_COOKIES", "")
    if not cookies or cookies.startswith("_ufg_br_sess=..."):
        print("Erro: defina a variável de ambiente SIGAA_COOKIES com os cookies da sessão.", file=sys.stderr)
        sys.exit(1)

    html = fetch_pagina_discente(cookies)
    html = _filtrar_dados_pessoais(html)

    output: Path = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")

    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{ts}] Página salva em: {output}  ({len(html)} bytes)")


if __name__ == "__main__":
    main()
