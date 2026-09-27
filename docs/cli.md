# CLI wrapper

A biblioteca expõe um CLI que serializa para JSON o resultado de qualquer método `get_*` público das classes `*Scraper` exportadas pelo pacote.

## Uso

Cookies são lidos via **stdin** (mais seguro que argumento — não aparecem em `ps` e evitam problemas com caracteres especiais):

```bash
# subcomando explícito
echo "$SIGAA_COOKIES" | sigaa-scraper discente

# forma alternativa (módulo Python)
echo "$SIGAA_COOKIES" | python -m sigaa_scraper discente

# quando só existe um subcomando registrado, ele é chamado sem argumento
echo "$SIGAA_COOKIES" | sigaa-scraper
```

A saída é sempre JSON em `stdout`. Erros vão para `stderr` também como JSON.

## Códigos de saída

| Código | Significado |
|--------|-------------|
| `0` | Sucesso |
| `1` | `SessionExpiredError` — cookies expirados ou inválidos |
| `2` | `UnexpectedPageError` — o SIGAA retornou uma página fora do formato esperado |
| `3` | Subcomando desconhecido ou ausente quando há mais de um disponível |

## Convenção de descoberta automática (para contribuidores)

O CLI **não precisa ser atualizado** quando uma nova página é adicionada à biblioteca. Em runtime, ele inspeciona o pacote `sigaa_scraper` e registra um subcomando para cada método `get_*` encontrado em qualquer classe cujo nome termine em `Scraper`.

A regra é simples:

- Classe `FooScraper` com método `get_bar()` → subcomando `sigaa-scraper bar`
- Classe `SigaaScraper` com método `get_discente()` → subcomando `sigaa-scraper discente`

Para que um novo scraper seja exposto automaticamente:

1. A classe deve terminar com `Scraper` (ex.: `ProfessorScraper`).
2. A classe deve ser exportada no `__init__.py` do pacote.
3. O método de entrada deve começar com `get_` (ex.: `get_professor()`).
4. O método deve receber apenas `self` — o CLI instancia o scraper com os cookies e chama o método sem argumentos adicionais.
5. O retorno deve ser um `@dataclass` ou uma `list` de `@dataclass` definidos em `models.py`.

Se o retorno for um tipo não suportado (ex.: `str`, `dict`), `_serialize` o repassa diretamente para `json.dumps` — desde que seja serializável por padrão.

Veja [Adicionando uma nova página](nova-pagina.md) para o passo a passo completo de criação de um novo scraper.
