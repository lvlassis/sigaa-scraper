import re
from datetime import date, datetime, timedelta, timezone

import requests
import xxhash
from parsel import Selector

_SIGAA_URL = "https://sigaa.sistemas.ufg.br/sigaa/portais/discente/discente.jsf"
_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_TZ_BRT = timezone(timedelta(hours=-3))
_ALERTA_IMG = "prova_semana.png"
_SESSION_EXPIRED_MARKER = "alert('Sua sessão foi expirada. É necessário autenticar-se novamente!');"
_PAGE_MARKERS = ["Componente Curricular", "Dados Institucionais", "Minhas atividades"]
_SMALL_PAGE_THRESHOLD = 500


class SessionExpiredError(Exception):
    pass


class UnexpectedPageError(Exception):
    pass


class SigaaScraper:
    def __init__(self, cookies: str):
        self._cookies = cookies

    def get_discente(self) -> dict:
        response = requests.get(
            _SIGAA_URL,
            headers={"Cookie": self._cookies, "User-Agent": _USER_AGENT},
        )
        body = response.text
        self._check_response(body)
        return self._parse_discente(Selector(text=body))

    @staticmethod
    def _check_response(body: str) -> None:
        if len(body) < _SMALL_PAGE_THRESHOLD and _SESSION_EXPIRED_MARKER in body:
            raise SessionExpiredError("Sessão SIGAA expirada")
        if not all(marker in body for marker in _PAGE_MARKERS):
            raise UnexpectedPageError("Página inesperada retornada pelo SIGAA")

    @staticmethod
    def _parse_discente(sel: Selector) -> dict:
        raw_email = SigaaScraper._field(sel, "E-Mail:")
        return {
            "nome": sel.xpath('//span[@class="nome"]//b/text()').get("").strip(),
            "matricula": SigaaScraper._field(sel, "Matrícula:"),
            "curso": " ".join(SigaaScraper._field(sel, "Curso:").split()),
            "nivel": SigaaScraper._field(sel, "Nível:"),
            "status": SigaaScraper._field(sel, "Status:"),
            "email": raw_email.split("@")[0] + "@discente.ufg.br" if "@" in raw_email else raw_email,
            "entrada": SigaaScraper._field(sel, "Entrada:"),
            "ip": SigaaScraper._to_float(SigaaScraper._indice(sel, "Índice de Prioridade")),
            "ti": SigaaScraper._to_float(SigaaScraper._indice(sel, "Taxa de Integralização")),
            "ta": SigaaScraper._to_float(SigaaScraper._indice(sel, "Taxa de Aprovação")),
            "qr": SigaaScraper._to_float(SigaaScraper._indice(sel, "Quantidade de Reprovações por Falta")),
            "mge": SigaaScraper._to_float(SigaaScraper._indice(sel, "Média Global do Estudante")),
            "mre": SigaaScraper._to_float(SigaaScraper._indice(sel, "Média Relativa do Estudante")),
            "pmf": SigaaScraper._to_float(SigaaScraper._indice(sel, "Porcentual Médio de Frequência")),
            "ch_exigida": SigaaScraper._parse_int(
                sel.xpath('//td[normalize-space()="CH. Exigida"]/following-sibling::td[1]/text()').get("").strip()
            ),
            "ch_cursada": SigaaScraper._parse_int(
                sel.xpath('//td[normalize-space()="CH. Cursada"]/following-sibling::td[1]/text()').get("").strip()
            ),
            "materias": SigaaScraper._materias(sel),
            "atividades": SigaaScraper._atividades(sel),
            "atualizacoes_turma": SigaaScraper._atualizacoes_turma(sel),
        }

    @staticmethod
    def _field(sel: Selector, label: str) -> str:
        return sel.xpath(
            f'//td[normalize-space()="{label}"]/following-sibling::td[1]/text()'
        ).get("").strip()

    @staticmethod
    def _indice(sel: Selector, title: str) -> str:
        return sel.xpath(
            f'//acronym[@title="{title}"]/parent::td/following-sibling::td[1]//div/text()'
        ).get("").strip()

    @staticmethod
    def _to_float(value: str) -> float | None:
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None

    @staticmethod
    def _parse_int(value: str) -> int | None:
        return int(value) if value.isdigit() else None

    @staticmethod
    def _parse_due(text: str) -> str | None:
        m = re.search(r'(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{1,2})', text)
        if not m:
            return None
        day, month, year = m.group(1).split("/")
        h, mi = m.group(2).split(":")
        dt = datetime(int(year), int(month), int(day), int(h), int(mi), tzinfo=_TZ_BRT)
        return dt.isoformat()

    @staticmethod
    def _parse_date(text: str) -> str | None:
        m = re.search(r'(\d{2})/(\d{2})/(\d{4})', text)
        if not m:
            return None
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()

    @staticmethod
    def _atividades(sel: Selector) -> list:
        rows = sel.xpath('//div[@id="avaliacao-portal"]//tbody/tr')
        result = []
        for row in rows:
            tipo = "alerta" if row.xpath(f'td[1]//img[contains(@src, "{_ALERTA_IMG}")]') else "normal"
            due_raw = " ".join(row.xpath('td[2]//text()').getall())
            due = SigaaScraper._parse_due(due_raw)
            nome = row.xpath('td[3]/small//a/text()').get("").strip()
            materia = row.xpath('(td[3]/small//text()[normalize-space()!=""])[1]').get("").strip()
            hasher = xxhash.xxh3_128()
            for part in (due or "", nome, materia):
                hasher.update(part.encode())
            result.append({"id": hasher.hexdigest(), "tipo": tipo, "due": due, "nome": nome, "materia": materia})
        return result

    @staticmethod
    def _atualizacoes_turma(sel: Selector) -> list:
        tables = sel.xpath('//div[@id="atualizacoes-turma"]//div[@class="rotator"]/table')
        result = []
        for table in tables:
            materia = table.xpath('normalize-space(.//tr[1]/td/a)').get("").strip()
            criacao = SigaaScraper._parse_date(table.xpath('.//tr[1]/td/text()').get(""))
            descricao = table.xpath('normalize-space(.//tr[2]/td)').get("").strip()
            hasher = xxhash.xxh3_128()
            for part in (materia, criacao or "", descricao):
                hasher.update(part.encode())
            result.append({"id": hasher.hexdigest(), "materia": materia, "criacao": criacao, "descricao": descricao})
        return result

    @staticmethod
    def _materias(sel: Selector) -> list:
        rows = sel.xpath(
            '//th[normalize-space()="Componente Curricular"]'
            '/ancestor::table[1]//tbody/tr'
        )
        result = []
        for row in rows:
            nome = row.xpath('normalize-space(td[1]/form//a)').get("").strip()
            local = row.xpath('normalize-space(td[2])').get("").strip()
            horario = row.xpath('normalize-space(td[3]//center)').get("").strip()
            if nome:
                result.append({"nome": nome, "local": local, "horario": horario})
        return result
