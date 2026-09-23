"""
Exemplo mínimo: lista as matérias do semestre atual.

Como obter os cookies:
  1. Faça login no SIGAA pelo navegador.
  2. Abra as ferramentas de desenvolvedor (F12) > aba Network.
  3. Recarregue a página e clique em qualquer requisição ao sigaa.sistemas.ufg.br.
  4. Copie o valor completo do header "Cookie" e cole na variável COOKIES abaixo.
"""

import os

from sigaa_scraper import SigaaScraper

COOKIES = os.environ.get("SIGAA_COOKIES", "_ufg_br_sess=...; JSESSIONID=...")

discente = SigaaScraper(COOKIES).get_discente()

print(f"Olá, {discente.nome}!")
print(f"\nMatérias do semestre ({len(discente.turmas)}):")
for turma in discente.turmas:
    print(f"  • {turma.nome}")
