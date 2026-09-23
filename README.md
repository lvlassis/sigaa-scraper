# Sigaa Scraper

Biblioteca Python para scraping do portal discente do SIGAA UFG. Extrai perfil acadêmico, matérias, atividades e atualizações de turma a partir de uma sessão autenticada.

**[Documentação completa](https://lvlassis.github.io/sigaa-scraper)**  &nbsp;·&nbsp;  [Quick Start](https://lvlassis.github.io/sigaa-scraper/quickstart/)  &nbsp;·&nbsp;  [Referência da API](https://lvlassis.github.io/sigaa-scraper/reference/)

## Instalação

```bash
pip install git+https://github.com/lvlassis/sigaa-scraper.git
```

## Quick Start

Você precisa dos cookies de uma sessão autenticada no SIGAA. Faça login pelo navegador, abra as ferramentas de desenvolvedor (`F12` > aba **Network**), recarregue a página e copie o valor do header `Cookie`.

```python
import os
from sigaa_scraper import SigaaScraper

cookies = os.environ.get("SIGAA_COOKIES", "_ufg_br_sess=...; JSESSIONID=...")

discente = SigaaScraper(cookies).get_discente()

print(f"Olá, {discente.nome}!")
print(f"\nMatérias do semestre ({len(discente.turmas)}):")
for turma in discente.turmas:
    print(f"  • {turma.nome}")
```

Saída esperada:

```
Olá, João da Silva!

Matérias do semestre (5):
  • Algoritmos e Programação
  • Cálculo I
  • ...
```

Consulte a [documentação](https://lvlassis.github.io/sigaa-scraper) para ver todos os campos disponíveis, tratamento de erros e exemplos avançados.

## Aviso de uso

> Esta biblioteca acessa apenas os dados do próprio usuário autenticado. Não a utilize para acessar dados de terceiros ou para realizar requisições em volume que possam sobrecarregar os servidores do SIGAA.

## Requisitos

- Python 3.12+
- Cookies de uma sessão ativa no SIGAA UFG
