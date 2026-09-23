# Quick Start

## 1. Obtenha os cookies da sessão

O SIGAA exige dois cookies juntos para autenticar uma sessão:

| Cookie | Descrição |
|---|---|
| `_ufg_br_sess` | Sessão Rails |
| `JSESSIONID` | Sessão Java/JSF |

**Como obtê-los:**

1. Faça login no SIGAA pelo navegador.
2. Abra as ferramentas de desenvolvedor (`F12`) e vá até a aba **Network**.
3. Recarregue a página e clique em qualquer requisição para `sigaa.sistemas.ufg.br`.
4. Copie o valor completo do header `Cookie`.

## 2. Busque os dados do discente

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

## 3. Use os dados retornados

`get_discente()` retorna um dicionário com o perfil completo do discente:

```python
{
    "nome": "João da Silva",
    "matricula": "202300001",
    "curso": "Ciência da Computação",
    "nivel": "Graduação",
    "status": "Ativo",
    "email": "joao@discente.ufg.br",
    "entrada": "2023.1",

    # Índices acadêmicos (float ou None se não disponível)
    "ip": 8.5,      # Índice de Prioridade
    "ti": 25.0,     # Taxa de Integralização (%)
    "ta": 100.0,    # Taxa de Aprovação (%)
    "qr": 0.0,      # Reprovações por Falta
    "mge": 9.0,     # Média Global do Estudante
    "mre": 85.0,    # Média Relativa do Estudante
    "pmf": 95.0,    # Porcentual Médio de Frequência (%)

    "ch_exigida": 3200,
    "ch_cursada": 800,

    "materias": [
        {"nome": "Algoritmos e Programação", "local": "AT4", "horario": "2M12345"},
    ],
    "atividades": [
        {
            "id": "a1b2c3...",       # hash estável da atividade
            "tipo": "alerta",        # "alerta" = prova na semana, "normal" = demais
            "due": "2026-08-31T23:59:00-03:00",
            "nome": "Prova 1",
            "materia": "Cálculo I",
        },
    ],
    "atualizacoes_turma": [
        {
            "id": "d4e5f6...",
            "materia": "Engenharia de Software 1",
            "criacao": "2026-08-24",
            "descricao": "Material da aula 5 disponível no portal.",
        },
    ],
}
```

## Tratamento de erros

| Exceção | Quando ocorre |
|---|---|
| `SessionExpiredError` | Os cookies expiraram ou são inválidos |
| `UnexpectedPageError` | O SIGAA retornou uma página fora do esperado |

## Dica: use variável de ambiente

Evite deixar cookies no código-fonte:

```bash
export SIGAA_COOKIES="_ufg_br_sess=...; JSESSIONID=..."
```

```python
import os
from sigaa_scraper import SigaaScraper

data = SigaaScraper(os.environ["SIGAA_COOKIES"]).get_discente()
```
