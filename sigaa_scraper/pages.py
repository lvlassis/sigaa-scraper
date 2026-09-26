import requests

_SIGAA_URL = "https://sigaa.sistemas.ufg.br/sigaa/portais/discente/discente.jsf"
_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def fetch_pagina_discente(cookies: str) -> str:
    """Realiza a requisição autenticada e retorna o HTML da página discente."""
    response = requests.get(
        _SIGAA_URL,
        headers={"Cookie": cookies, "User-Agent": _USER_AGENT},
    )
    response.raise_for_status()
    return response.text
