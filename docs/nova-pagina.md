# Adicionando uma nova página

Este guia descreve as convenções obrigatórias para adicionar o scraping de uma nova página do SIGAA.

## Estrutura de módulos

Cada página do SIGAA segue uma separação em três camadas:

| Camada | Arquivo | Responsabilidade |
|---|---|---|
| HTTP | `sigaa_scraper/pages.py` | Fazer a requisição e retornar o HTML bruto |
| Modelos | `sigaa_scraper/models.py` | Dataclasses tipadas com docstrings para cada campo |
| Scraping | `sigaa_scraper/scraper_<pagina>.py` | Parsear o HTML e retornar instâncias dos modelos |

Nunca misture lógica de requisição com lógica de parsing. Nunca defina modelos fora de `models.py`.

## Passo a passo

### 1. Defina os modelos em `models.py`

Adicione um `@dataclass` para cada estrutura de dados que a página retorna. Documente cada campo:

```python
@dataclass
class MinhaEntidade:
    """Descrição da entidade.

    Attributes:
        campo_a: Descrição do campo A.
        campo_b: Descrição do campo B.
    """
    campo_a: str
    campo_b: str | None
```

Datas e horários devem ser `str` em ISO 8601 (ex: `"2026-09-01"`, `"2026-09-01T14:00:00-03:00"`). Nunca use objetos `datetime`.

### 2. Adicione a função de download em `pages.py`

Implemente uma função `fetch_<pagina>(cookies: str) -> str` que faz o GET autenticado e retorna o HTML:

```python
def fetch_minha_pagina(cookies: str) -> str:
    response = requests.get(
        "https://sigaa.sistemas.ufg.br/sigaa/...",
        headers={"Cookie": cookies},
        timeout=30,
    )
    response.raise_for_status()
    return response.text
```

### 3. Crie `scraper_<pagina>.py`

Crie um arquivo dedicado para o scraper da nova página. Siga o padrão de `scraper_discente.py`: uma classe com métodos estáticos de parsing e um método público de entrada:

```python
# sigaa_scraper/scraper_minha_pagina.py
from parsel import Selector
from .models import MinhaEntidade
from .pages import fetch_minha_pagina


class MinhaPaginaScraper:
    def __init__(self, cookies: str) -> None:
        self._cookies = cookies

    def get_dados(self) -> list[MinhaEntidade]:
        html = fetch_minha_pagina(self._cookies)
        # validação de resposta...
        return self._parse(Selector(text=html))

    @staticmethod
    def _parse(sel: Selector) -> list[MinhaEntidade]:
        ...
```

Exponha a nova classe no `__init__.py`:

```python
from .scraper_minha_pagina import MinhaPaginaScraper
__all__ = [..., "MinhaPaginaScraper"]
```

### 4. Gere e sanitize a fixture de teste

Todo scraper novo precisa de ao menos uma página real sanitizada em `tests/pages/`. PRs sem fixture não serão aceitos.

**4a.** Implemente um script `tests/download_<pagina>.py` análogo a `tests/download_pages.py`, com uma função `_sanitizar_dados_comprometedores(html)` que cobre:

- Dados pessoais do usuário (nome, matrícula, e-mail, foto)
- PKs e tokens expostos no HTML (ver [critérios de sanitização](fixtures.md#oclusão-de-dados-pessoais-e-ids-de-banco-de-dados))
- Hostname do servidor no rodapé

**4b.** Baixe a página e gere a fixture:

```bash
SIGAA_COOKIES="..." python tests/download_<pagina>.py
```

**4c.** Inspecione o HTML gerado e confirme que nenhum dado real ficou exposto. Consulte a [lista de padrões sensíveis já conhecidos](fixtures.md#ids-e-tokens-de-banco-de-dados) como referência — mas não a trate como exaustiva; cada página pode expor novos campos. Quando encontrar um padrão novo, documente-o em `fixtures.md`.

**4d.** Gere o oracle YAML:

```bash
# adapte generate_oracle.py ou crie um equivalente para a nova página
make oracle
```

### 5. Implemente os testes

Crie `tests/scraper/test_<pagina>.py` com dois níveis:

- **Testes unitários**: snippets HTML inline, testam cada método estático isoladamente.
- **Testes de página**: parametrizados sobre os pares `.html` + `.yaml` em `tests/pages/`.

```bash
make tests  # todos devem passar antes de abrir o PR
```

---

## Checklist de PR

Antes de abrir o pull request, confirme cada item:

- [ ] Modelos definidos e documentados em `models.py`
- [ ] Função de download em `pages.py`
- [ ] Scraper em arquivo dedicado `scraper_<pagina>.py`
- [ ] Classe exportada no `__init__.py`
- [ ] Ao menos uma fixture HTML em `tests/pages/` **100% sanitizada**
- [ ] Oracle YAML correspondente em `tests/pages/`
- [ ] Novos padrões sensíveis encontrados documentados em `fixtures.md`
- [ ] `make tests` passando sem erros
