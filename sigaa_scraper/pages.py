import requests

from .exceptions import NetworkError

_SIGAA_URL = "https://sigaa.sistemas.ufg.br/sigaa/portais/discente/discente.jsf"
_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_TIMEOUT = 30


def fetch_pagina_discente(cookies: str) -> str:
    """Realiza a requisição autenticada e retorna o HTML da página discente."""
    try:
        response = requests.get(
            _SIGAA_URL,
            headers={"Cookie": cookies, "User-Agent": _USER_AGENT},
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        raise NetworkError("Timeout ao conectar ao SIGAA (limite: 30s)")
    except requests.exceptions.ConnectionError as e:
        raise NetworkError(f"Erro de conexão ao SIGAA: {e}")
    except requests.exceptions.HTTPError as e:
        raise NetworkError(f"SIGAA retornou HTTP {e.response.status_code}")
