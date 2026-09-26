from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class TopicoForum:
    """Tópico exibido no painel do fórum do curso."""

    titulo: str
    """Título do tópico."""
    autor: str
    """Login do autor."""
    autor_nome: str
    """Nome completo do autor (atributo ``title`` do ``<acronym>``)."""
    respostas: int
    """Número de respostas."""
    data: str | None
    """Data da última atualização em ISO 8601 com fuso BRT."""


@dataclass
class Atividade:
    """Atividade avaliativa pendente."""

    tipo: Literal["alerta", "normal"]
    """``"alerta"`` se há prova na semana corrente, ``"normal"`` caso contrário."""
    due: str | None
    """Prazo em ISO 8601 com fuso BRT (ex.: ``"2026-08-31T23:59:00-03:00"``) ou ``None``."""
    nome: str
    """Nome da atividade."""
    materia: str
    """Nome da matéria associada."""


@dataclass
class AtualizacaoTurma:
    """Atualização publicada em uma turma."""

    materia: str
    """Nome da matéria."""
    criacao: str | None
    """Data de criação em ISO 8601 (ex.: ``"2026-08-24"``) ou ``None``."""
    descricao: str
    """Texto da atualização."""


@dataclass
class Turma:
    """Turma matriculada no semestre atual."""

    nome: str
    """Nome do componente curricular."""
    local: str
    """Sala ou local das aulas."""
    horario: str
    """Código de horário (ex.: ``"2M12345"``)."""


@dataclass
class Discente:
    """Perfil acadêmico completo do discente."""

    nome: str
    """Nome completo."""
    nome_titulo: str
    """Nome exibido no título da página (``<p class="usuario">``)."""
    matricula: str
    """Número de matrícula."""
    curso: str
    """Nome do curso."""
    nivel: str
    """Nível do curso (ex.: ``"Graduação"``)."""
    status: str
    """Situação acadêmica (ex.: ``"Ativo"``)."""
    email: str
    """E-mail institucional (``@discente.ufg.br``)."""
    entrada: str
    """Período de ingresso (ex.: ``"2023.1"``)."""
    ip: float | None
    """Índice de Prioridade."""
    ti: float | None
    """Taxa de Integralização em %."""
    ta: float | None
    """Taxa de Aprovação em %."""
    qr: float | None
    """Reprovações por Falta."""
    mge: float | None
    """Média Global do Estudante."""
    mre: float | None
    """Média Relativa do Estudante."""
    pmf: float | None
    """Porcentual Médio de Frequência em %."""
    ch_exigida: int | None
    """Carga horária exigida pelo curso."""
    ch_cursada: int | None
    """Carga horária já cursada."""
    turmas: list[Turma]
    """Turmas matriculadas no semestre atual."""
    atividades: list[Atividade]
    """Atividades avaliativas pendentes."""
    atualizacoes_turma: list[AtualizacaoTurma]
    """Atualizações recentes das turmas."""
    topicos_forum: list[TopicoForum]
    """Tópicos recentes do fórum do curso."""
