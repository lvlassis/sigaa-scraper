"""
Exemplo de uso de SigaaScraper.get_discente().

Como obter os cookies:
  1. Faça login no SIGAA pelo navegador.
  2. Abra as ferramentas de desenvolvedor (F12) > aba Network.
  3. Recarregue a página e clique em qualquer requisição ao sigaa.sistemas.ufg.br.
  4. Copie o valor completo do header "Cookie" e cole abaixo.
"""

import dataclasses
import json
import os

from sigaa_scraper import SigaaScraper, SessionExpiredError, UnexpectedPageError

COOKIES = os.environ.get("SIGAA_COOKIES", "_ufg_br_sess=...; JSESSIONID=...")


def main() -> None:
    try:
        discente = SigaaScraper(COOKIES).get_discente()
    except SessionExpiredError:
        print("Sessão expirada — atualize os cookies.")
        return
    except UnexpectedPageError:
        print("O SIGAA retornou uma página inesperada.")
        return

    print(f"Aluno  : {discente.nome} ({discente.matricula})")
    print(f"Curso  : {discente.curso} — {discente.nivel}")
    print(f"Status : {discente.status}")
    print(f"IP     : {discente.ip}  |  MGE: {discente.mge}  |  TI: {discente.ti}%")
    print()

    print(f"Turmas matriculadas ({len(discente.turmas)}):")
    for t in discente.turmas:
        print(f"  • {t.nome:50s}  {t.local:6s}  {t.horario}")

    print()
    alertas = [a for a in discente.atividades if a.tipo == "alerta"]
    print(f"Atividades ({len(discente.atividades)})  —  alertas de prova na semana: {len(alertas)}")
    for a in discente.atividades:
        tag = "[ALERTA]" if a.tipo == "alerta" else "        "
        due = a.due or "sem prazo"
        print(f"  {tag} {due}  {a.nome} ({a.materia})")

    print()
    print(f"Atualizações de turma ({len(discente.atualizacoes_turma)}):")
    for u in discente.atualizacoes_turma:
        print(f"  [{u.criacao}] {u.materia}: {u.descricao[:80]}")

    print()
    print("Payload completo (JSON):")
    print(json.dumps(dataclasses.asdict(discente), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
