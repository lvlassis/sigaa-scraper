import pytest
from parsel import Selector

from sigaa_scraper.scraper import SigaaScraper
from tests.conftest import page_vectors


@pytest.mark.parametrize("html,expected", page_vectors())
class TestParseDiscentePages:
    def _discente(self, html):
        return SigaaScraper._parse_discente(Selector(text=html))

    def test_campos_escalares(self, html, expected):
        d = self._discente(html)
        campos = (
            "nome", "nome_titulo", "matricula", "curso", "nivel", "status",
            "email", "entrada", "ip", "ti", "ta", "qr", "mge", "mre", "pmf",
            "ch_exigida", "ch_cursada",
        )
        for campo in campos:
            if campo in expected:
                assert getattr(d, campo) == expected[campo], f"campo {campo!r} diverge"

    def test_turmas(self, html, expected):
        if "turmas" not in expected:
            pytest.skip("turmas não definidas no oracle")
        d = self._discente(html)
        spec = expected["turmas"]
        assert len(d.turmas) == spec["count"]
        for i, item in enumerate(spec.get("items", [])):
            t = d.turmas[i]
            for campo, valor in item.items():
                assert getattr(t, campo) == valor, f"turmas[{i}].{campo} diverge"

    def test_atividades(self, html, expected):
        if "atividades" not in expected:
            pytest.skip("atividades não definidas no oracle")
        d = self._discente(html)
        spec = expected["atividades"]
        assert len(d.atividades) == spec["count"]
        for i, item in enumerate(spec.get("items", [])):
            a = d.atividades[i]
            for campo, valor in item.items():
                assert getattr(a, campo) == valor, f"atividades[{i}].{campo} diverge"

    def test_atualizacoes_turma(self, html, expected):
        if "atualizacoes_turma" not in expected:
            pytest.skip("atualizacoes_turma não definidas no oracle")
        d = self._discente(html)
        spec = expected["atualizacoes_turma"]
        assert len(d.atualizacoes_turma) == spec["count"]
        for i, item in enumerate(spec.get("items", [])):
            a = d.atualizacoes_turma[i]
            for campo, valor in item.items():
                assert getattr(a, campo) == valor, f"atualizacoes_turma[{i}].{campo} diverge"

    def test_topicos_forum(self, html, expected):
        if "topicos_forum" not in expected:
            pytest.skip("topicos_forum não definidos no oracle")
        d = self._discente(html)
        spec = expected["topicos_forum"]
        assert len(d.topicos_forum) == spec["count"]
        for i, item in enumerate(spec.get("items", [])):
            t = d.topicos_forum[i]
            for campo, valor in item.items():
                assert getattr(t, campo) == valor, f"topicos_forum[{i}].{campo} diverge"
