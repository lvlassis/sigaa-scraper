class SessionExpiredError(Exception):
    """Lançada quando os cookies da sessão estão expirados ou são inválidos."""


class UnexpectedPageError(Exception):
    """Lançada quando o SIGAA retorna uma página fora do formato esperado."""


class NetworkError(Exception):
    """Lançada quando há falha de rede ao acessar o SIGAA."""
