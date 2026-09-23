"""
Exemplo de uso de SigaaScraper.get_discente().

Como obter os cookies:
  1. Faça login no SIGAA pelo navegador.
  2. Abra as ferramentas de desenvolvedor (F12) > aba Network.
  3. Recarregue a página e clique em qualquer requisição ao sigaa.sistemas.ufg.br.
  4. Copie o valor completo do header "Cookie" e cole abaixo.
"""

import json
import os

from sigaa_scraper import SigaaScraper, SessionExpiredError, UnexpectedPageError

COOKIES = os.environ.get("SIGAA_COOKIES", "_ufg_br_sess=...; JSESSIONID=...")


def main() -> None:
    try:
        data = SigaaScraper(COOKIES).get_discente()
    except SessionExpiredError:
        print("Sessão expirada — atualize os cookies.")
        return
    except UnexpectedPageError:
        print("O SIGAA retornou uma página inesperada.")
        return

    print(f"Aluno  : {data['nome']} ({data['matricula']})")
    print(f"Curso  : {data['curso']} — {data['nivel']}")
    print(f"Status : {data['status']}")
    print(f"IP     : {data['ip']}  |  MGE: {data['mge']}  |  TI: {data['ti']}%")
    print()

    materias = data["materias"]
    print(f"Matérias matriculadas ({len(materias)}):")
    for m in materias:
        print(f"  • {m['nome']:50s}  {m['local']:6s}  {m['horario']}")

    print()
    atividades = data["atividades"]
    alertas = [a for a in atividades if a["tipo"] == "alerta"]
    print(f"Atividades ({len(atividades)})  —  alertas de prova na semana: {len(alertas)}")
    for a in atividades:
        tag = "[ALERTA]" if a["tipo"] == "alerta" else "        "
        due = a["due"] or "sem prazo"
        print(f"  {tag} {due}  {a['nome']} ({a['materia']})")

    print()
    atualizacoes = data["atualizacoes_turma"]
    print(f"Atualizações de turma ({len(atualizacoes)}):")
    for u in atualizacoes:
        print(f"  [{u['criacao']}] {u['materia']}: {u['descricao'][:80]}")

    print()
    print("Payload completo (JSON):")
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
