# sigaa-scraper

Biblioteca Python para scraping do portal discente do SIGAA UFG. Extrai perfil acadêmico, matérias, atividades e atualizações de turma a partir de uma sessão autenticada.

## Instalação

```bash
pip install git+https://github.com/lvlassis/sigaa-scraper.git
```

## Quick Start

Você precisa dos cookies de uma sessão autenticada no SIGAA. O SIGAA exige dois cookies juntos: `_ufg_br_sess` (sessão Rails) e `JSESSIONID` (sessão Java/JSF).

Para obtê-los, faça login no SIGAA pelo navegador e copie o valor do header `Cookie` nas ferramentas de desenvolvedor (aba Network).

```python
from sigaa_scraper import SigaaScraper, SessionExpiredError, UnexpectedPageError

cookies = "_ufg_br_sess=...; JSESSIONID=..."

try:
    data = SigaaScraper(cookies).get_discente()
except SessionExpiredError:
    print("Sessão expirada — atualize os cookies.")
except UnexpectedPageError:
    print("O SIGAA retornou uma página inesperada.")
```

`get_discente()` retorna um dicionário com os dados do portal discente:

```python
{
    "nome": "João da Silva",
    "matricula": "202300001",
    "curso": "Ciência da Computação",
    "nivel": "Graduação",
    "status": "Ativo",
    "email": "joao@discente.ufg.br",
    "entrada": "2023.1",
    "ip": 8.5,      # Índice de Prioridade
    "ti": 25.0,     # Taxa de Integralização (%)
    "ta": 100.0,    # Taxa de Aprovação (%)
    "qr": 0.0,      # Quantidade de Reprovações por Falta
    "mge": 9.0,     # Média Global do Estudante
    "mre": 85.0,    # Média Relativa do Estudante
    "pmf": 95.0,    # Porcentual Médio de Frequência (%)
    "ch_exigida": 3200,
    "ch_cursada": 800,
    "materias": [
        {"nome": "Algoritmos e Programação", "local": "AT4", "horario": "2M12345"},
    ],
    "atividades": [
        {"id": "...", "tipo": "alerta", "due": "2026-08-31T23:59:00-03:00", "nome": "Prova 1", "materia": "Cálculo I"},
    ],
    "atualizacoes_turma": [
        {"id": "...", "materia": "Engenharia de Software 1", "criacao": "2026-08-24", "descricao": "..."},
    ],
}
```

## Exceções

| Exceção | Quando ocorre |
|---|---|
| `SessionExpiredError` | Os cookies expiraram ou são inválidos |
| `UnexpectedPageError` | O SIGAA retornou uma página fora do esperado |

## Aviso de uso

> Esta biblioteca acessa apenas os dados do próprio usuário autenticado. Não a utilize para acessar dados de terceiros ou para realizar requisições em volume que possam sobrecarregar os servidores do SIGAA.

## Requisitos

- Python 3.12+
- Cookies de uma sessão ativa no SIGAA UFG
