import pytest
from parsel import Selector

from sigaa_scraper.scraper import (
    SigaaScraper,
    SessionExpiredError,
    UnexpectedPageError,
    _PAGE_MARKERS,
    _SESSION_EXPIRED_MARKER,
    _SMALL_PAGE_THRESHOLD,
)


def _sel(html: str) -> Selector:
    return Selector(text=html)


# ── _to_float ────────────────────────────────────────────────────────────────

class TestToFloat:
    def test_virgula_decimal(self):
        assert SigaaScraper._to_float("8,5") == 8.5

    def test_ponto_decimal(self):
        assert SigaaScraper._to_float("8.5") == 8.5

    def test_numero_inteiro(self):
        assert SigaaScraper._to_float("10") == 10.0

    def test_string_invalida_retorna_none(self):
        assert SigaaScraper._to_float("N/A") is None

    def test_vazio_retorna_none(self):
        assert SigaaScraper._to_float("") is None


# ── _check_response ──────────────────────────────────────────────────────────

class TestCheckResponse:
    def test_sessao_expirada(self):
        html = f"<script>{_SESSION_EXPIRED_MARKER}\ndocument.location.href='/sigaa';</script>"
        assert len(html) < _SMALL_PAGE_THRESHOLD
        with pytest.raises(SessionExpiredError):
            SigaaScraper._check_response(html)

    def test_pagina_sem_marker_levanta_unexpected_page(self):
        with pytest.raises(UnexpectedPageError):
            SigaaScraper._check_response("<html><body>Página desconhecida</body></html>")

    def test_pagina_com_markers_parciais_levanta_unexpected_page(self):
        html = f"<html><body>{_PAGE_MARKERS[0]} {_PAGE_MARKERS[1]}</body></html>"
        with pytest.raises(UnexpectedPageError):
            SigaaScraper._check_response(html)

    def test_pagina_valida_nao_levanta(self):
        html = f"<html><body>{' '.join(_PAGE_MARKERS)}</body></html>"
        SigaaScraper._check_response(html)

    def test_pagina_grande_com_marker_sessao_nao_e_expirada(self):
        corpo_grande = "x" * _SMALL_PAGE_THRESHOLD + _SESSION_EXPIRED_MARKER
        with pytest.raises(UnexpectedPageError):
            SigaaScraper._check_response(corpo_grande)


# ── _field ───────────────────────────────────────────────────────────────────

class TestField:
    HTML = """
    <table>
      <tr><td>Matrícula:</td><td>  202300001  </td></tr>
      <tr><td>Curso:</td><td>Ciência da Computação</td></tr>
    </table>
    """

    def test_campo_existente(self):
        assert SigaaScraper._field(_sel(self.HTML), "Matrícula:") == "202300001"

    def test_whitespace_do_valor_removido(self):
        assert SigaaScraper._field(_sel(self.HTML), "Matrícula:") == "202300001"

    def test_campo_ausente_retorna_vazio(self):
        assert SigaaScraper._field(_sel(self.HTML), "Status:") == ""


# ── _indice ──────────────────────────────────────────────────────────────────

class TestIndice:
    HTML = """
    <table>
      <tr>
        <td><acronym title="Índice de Prioridade">IP</acronym></td>
        <td><div>8,5</div></td>
      </tr>
      <tr>
        <td><acronym title="Taxa de Integralização">TI</acronym></td>
        <td><div>25,0</div></td>
      </tr>
    </table>
    """

    def test_indice_existente(self):
        assert SigaaScraper._indice(_sel(self.HTML), "Índice de Prioridade") == "8,5"

    def test_segundo_indice(self):
        assert SigaaScraper._indice(_sel(self.HTML), "Taxa de Integralização") == "25,0"

    def test_indice_ausente_retorna_vazio(self):
        assert SigaaScraper._indice(_sel(self.HTML), "Índice Inexistente") == ""


# ── _materias ────────────────────────────────────────────────────────────────

class TestMaterias:
    HTML = """
    <table>
      <thead><tr><th>Componente Curricular</th><th>Local</th><th>Horário</th></tr></thead>
      <tbody>
        <tr>
          <td><form><a href="#">Algoritmos e Programação</a></form></td>
          <td>AT4</td>
          <td><center>2M12345</center></td>
        </tr>
        <tr>
          <td><form><a href="#">Cálculo I</a></form></td>
          <td>IME</td>
          <td><center>3T34</center></td>
        </tr>
      </tbody>
    </table>
    """

    def test_quantidade_de_materias(self):
        assert len(SigaaScraper._materias(_sel(self.HTML))) == 2

    def test_nomes_das_materias(self):
        nomes = [m["nome"] for m in SigaaScraper._materias(_sel(self.HTML))]
        assert "Algoritmos e Programação" in nomes
        assert "Cálculo I" in nomes

    def test_campos_de_cada_materia(self):
        result = SigaaScraper._materias(_sel(self.HTML))
        materia = next(m for m in result if m["nome"] == "Algoritmos e Programação")
        assert materia["local"] == "AT4"
        assert materia["horario"] == "2M12345"

    def test_tabela_sem_linhas_retorna_vazio(self):
        html = """
        <table>
          <thead><tr><th>Componente Curricular</th></tr></thead>
          <tbody></tbody>
        </table>
        """
        assert SigaaScraper._materias(_sel(html)) == []

    def test_linha_sem_nome_e_ignorada(self):
        html = """
        <table>
          <thead><tr><th>Componente Curricular</th></tr></thead>
          <tbody>
            <tr><td></td><td>AT4</td><td><center>2M12</center></td></tr>
          </tbody>
        </table>
        """
        assert SigaaScraper._materias(_sel(html)) == []


# ── _parse_due ───────────────────────────────────────────────────────────────

class TestParseDue:
    def test_formato_basico(self):
        assert SigaaScraper._parse_due("24/08/2026 21:35") == "2026-08-24T21:35:00-03:00"

    def test_formato_com_sufixo_dias(self):
        assert SigaaScraper._parse_due("31/08/2026 23:59 (2 dias)") == "2026-08-31T23:59:00-03:00"

    def test_minuto_um_digito(self):
        assert SigaaScraper._parse_due("24/08/2026 22:0") == "2026-08-24T22:00:00-03:00"

    def test_texto_sem_data_retorna_none(self):
        assert SigaaScraper._parse_due("Sem data") is None

    def test_texto_vazio_retorna_none(self):
        assert SigaaScraper._parse_due("") is None


# ── _atividades ──────────────────────────────────────────────────────────────

class TestAtividades:
    _HTML_ALERTA = """
    <div id="avaliacao-portal">
      <table><tbody>
        <tr>
          <td><img src="/sigaa/img/prova_semana.png" title="Atividade na Semana"></td>
          <td>31/08/2026 23:59 (2 dias)</td>
          <td><small>MATÉRIA A<br><strong>Tarefa:</strong><a href="#">Nome da Atividade</a></small></td>
        </tr>
      </tbody></table>
    </div>
    """

    _HTML_NORMAL = """
    <div id="avaliacao-portal">
      <table><tbody>
        <tr>
          <td></td>
          <td><font color="gray">24/08/2026 21:35</font></td>
          <td><small><font color="gray">MATÉRIA B<br><strong>Tarefa:</strong><a href="#">Outra Atividade</a></font></small></td>
        </tr>
      </tbody></table>
    </div>
    """

    def test_tipo_alerta_com_img(self):
        assert SigaaScraper._atividades(_sel(self._HTML_ALERTA))[0]["tipo"] == "alerta"

    def test_tipo_normal_sem_img(self):
        assert SigaaScraper._atividades(_sel(self._HTML_NORMAL))[0]["tipo"] == "normal"

    def test_due_com_sufixo_dias(self):
        assert SigaaScraper._atividades(_sel(self._HTML_ALERTA))[0]["due"] == "2026-08-31T23:59:00-03:00"

    def test_due_com_font_gray(self):
        assert SigaaScraper._atividades(_sel(self._HTML_NORMAL))[0]["due"] == "2026-08-24T21:35:00-03:00"

    def test_nome_extraido_do_link(self):
        assert SigaaScraper._atividades(_sel(self._HTML_ALERTA))[0]["nome"] == "Nome da Atividade"

    def test_materia_sem_font(self):
        assert SigaaScraper._atividades(_sel(self._HTML_ALERTA))[0]["materia"] == "MATÉRIA A"

    def test_materia_dentro_de_font(self):
        assert SigaaScraper._atividades(_sel(self._HTML_NORMAL))[0]["materia"] == "MATÉRIA B"

    def test_id_e_string_hexadecimal(self):
        int(SigaaScraper._atividades(_sel(self._HTML_ALERTA))[0]["id"], 16)

    def test_id_deterministico(self):
        assert (
            SigaaScraper._atividades(_sel(self._HTML_ALERTA))[0]["id"]
            == SigaaScraper._atividades(_sel(self._HTML_ALERTA))[0]["id"]
        )

    def test_ids_distintos_para_atividades_distintas(self):
        html = f"""
        <div id="avaliacao-portal"><table><tbody>
          {self._HTML_ALERTA.split('<tbody>')[1].split('</tbody>')[0]}
          {self._HTML_NORMAL.split('<tbody>')[1].split('</tbody>')[0]}
        </tbody></table></div>
        """
        ativ = SigaaScraper._atividades(_sel(html))
        assert ativ[0]["id"] != ativ[1]["id"]

    def test_sem_atividades_retorna_lista_vazia(self):
        html = '<div id="avaliacao-portal"><table><tbody></tbody></table></div>'
        assert SigaaScraper._atividades(_sel(html)) == []

    def test_multiplas_atividades(self):
        html = f"""
        <div id="avaliacao-portal"><table><tbody>
          {self._HTML_ALERTA.split('<tbody>')[1].split('</tbody>')[0]}
          {self._HTML_NORMAL.split('<tbody>')[1].split('</tbody>')[0]}
        </tbody></table></div>
        """
        assert len(SigaaScraper._atividades(_sel(html))) == 2


# ── _parse_date ──────────────────────────────────────────────────────────────

class TestParseDate:
    def test_formato_dd_mm_yyyy(self):
        assert SigaaScraper._parse_date("27/08/2026 - ") == "2026-08-27"

    def test_apenas_a_data(self):
        assert SigaaScraper._parse_date("24/08/2026") == "2026-08-24"

    def test_texto_sem_data_retorna_none(self):
        assert SigaaScraper._parse_date("sem data aqui") is None

    def test_texto_vazio_retorna_none(self):
        assert SigaaScraper._parse_date("") is None


# ── _atualizacoes_turma ──────────────────────────────────────────────────────

class TestAtualizacoesTurma:
    _HTML = """
    <div id="atualizacoes-turma">
      <div class="rotator">
        <table>
          <tr><td>27/08/2026 - <a href="#">INTELIGÊNCIA COMPUTACIONAL</a></td></tr>
          <tr><td>Nova Notícia: Aula do dia 27/08/2026, quinta-feira.</td></tr>
        </table>
        <table>
          <tr><td>24/08/2026 - <a href="#">ENGENHARIA DE SOFTWARE 1</a></td></tr>
          <tr><td>Tarefa alterada.</td></tr>
        </table>
      </div>
    </div>
    """

    _HTML_VAZIO = """
    <div id="atualizacoes-turma"><div class="rotator"></div></div>
    """

    def _get(self):
        return SigaaScraper._atualizacoes_turma(_sel(self._HTML))

    def test_quantidade_de_atualizacoes(self):
        assert len(self._get()) == 2

    def test_materia(self):
        assert self._get()[0]["materia"] == "INTELIGÊNCIA COMPUTACIONAL"

    def test_criacao_em_iso(self):
        assert self._get()[0]["criacao"] == "2026-08-27"

    def test_descricao(self):
        assert self._get()[0]["descricao"] == "Nova Notícia: Aula do dia 27/08/2026, quinta-feira."

    def test_id_e_string_hexadecimal(self):
        int(self._get()[0]["id"], 16)

    def test_id_deterministico(self):
        assert self._get()[0]["id"] == self._get()[0]["id"]

    def test_ids_distintos_para_atualizacoes_distintas(self):
        atualizacoes = self._get()
        assert atualizacoes[0]["id"] != atualizacoes[1]["id"]

    def test_sem_tabelas_retorna_lista_vazia(self):
        assert SigaaScraper._atualizacoes_turma(_sel(self._HTML_VAZIO)) == []


# ── _parse_discente (integração) ─────────────────────────────────────────────

_PAGINA_VALIDA = f"""
<html><body>
  {" ".join(_PAGE_MARKERS)}
  <span class="nome"><b>João da Silva</b></span>
  <table>
    <tr><td>Matrícula:</td><td>202300001</td></tr>
    <tr><td>Curso:</td><td>Ciência   da   Computação</td></tr>
    <tr><td>Nível:</td><td>Graduação</td></tr>
    <tr><td>Status:</td><td>Ativo</td></tr>
    <tr><td>E-Mail:</td><td>joao@ufg.br</td></tr>
    <tr><td>Entrada:</td><td>2023.1</td></tr>
    <tr><td>CH. Exigida</td><td>3200</td></tr>
    <tr><td>CH. Cursada</td><td>800</td></tr>
  </table>
  <table>
    <tr><td><acronym title="Índice de Prioridade">IP</acronym></td><td><div>8,5</div></td></tr>
    <tr><td><acronym title="Taxa de Integralização">TI</acronym></td><td><div>25,0</div></td></tr>
    <tr><td><acronym title="Taxa de Aprovação">TA</acronym></td><td><div>100,0</div></td></tr>
    <tr><td><acronym title="Quantidade de Reprovações por Falta">QRF</acronym></td><td><div>0</div></td></tr>
    <tr><td><acronym title="Média Global do Estudante">MGE</acronym></td><td><div>9,0</div></td></tr>
    <tr><td><acronym title="Média Relativa do Estudante">MRE</acronym></td><td><div>85,0</div></td></tr>
    <tr><td><acronym title="Porcentual Médio de Frequência">PMF</acronym></td><td><div>95,0</div></td></tr>
  </table>
  <table>
    <thead><tr><th>Componente Curricular</th><th>Local</th><th>Horário</th></tr></thead>
    <tbody>
      <tr>
        <td><form><a href="#">Algoritmos e Programação</a></form></td>
        <td>AT4</td>
        <td><center>2M12345</center></td>
      </tr>
    </tbody>
  </table>
</body></html>
"""


class TestParseDiscente:
    def _parse(self, html: str = _PAGINA_VALIDA) -> dict:
        return SigaaScraper._parse_discente(_sel(html))

    def test_retorna_dict(self):
        assert isinstance(self._parse(), dict)

    def test_campos_texto(self):
        item = self._parse()
        assert item["nome"] == "João da Silva"
        assert item["matricula"] == "202300001"
        assert item["nivel"] == "Graduação"
        assert item["status"] == "Ativo"
        assert item["entrada"] == "2023.1"

    def test_curso_com_espacos_extras_normalizado(self):
        assert self._parse()["curso"] == "Ciência da Computação"

    def test_email_com_arroba_recebe_dominio_discente_ufg(self):
        assert self._parse()["email"] == "joao@discente.ufg.br"

    def test_email_sem_arroba_fica_inalterado(self):
        html = _PAGINA_VALIDA.replace("joao@ufg.br", "joao.semdominio")
        assert self._parse(html)["email"] == "joao.semdominio"

    def test_indices_convertidos_para_float(self):
        item = self._parse()
        assert item["ip"] == 8.5
        assert item["ti"] == 25.0
        assert item["ta"] == 100.0
        assert item["qr"] == 0.0
        assert item["mge"] == 9.0
        assert item["mre"] == 85.0
        assert item["pmf"] == 95.0

    def test_ch_convertidas_para_int(self):
        item = self._parse()
        assert item["ch_exigida"] == 3200
        assert item["ch_cursada"] == 800

    def test_materias_e_lista(self):
        assert isinstance(self._parse()["materias"], list)

    def test_materias_extraidas(self):
        nomes = [m["nome"] for m in self._parse()["materias"]]
        assert "Algoritmos e Programação" in nomes

    def test_atividades_e_lista(self):
        assert isinstance(self._parse()["atividades"], list)

    def test_atualizacoes_turma_e_lista(self):
        assert isinstance(self._parse()["atualizacoes_turma"], list)
