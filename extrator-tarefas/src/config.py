"""Carrega a configuração da aplicação a partir de variáveis de ambiente / .env.

Todos os parâmetros do LLM ficam aqui, fora do núcleo: para mudar modelo,
temperatura, limite de tokens, timeout ou prompt de sistema basta editar o
.env (veja o .env.example), sem tocar no código.
"""
import os
from typing import Callable, Optional

from dotenv import load_dotenv

PADROES = {
    "GEMINI_MODEL": "gemini-2.0-flash",
    "LLM_TEMPERATURE": "0",
    "LLM_TOP_P": "1.0",
    "LLM_MAX_TOKENS": "1024",
    "LLM_TIMEOUT_SEGUNDOS": "30",
}


class ConfigError(Exception):
    pass


def _ler(nome: str) -> str:
    """Valor da variável, ou o padrão se ausente/vazia."""
    valor = os.getenv(nome, "").strip()
    return valor if valor else PADROES[nome]


def _numero(nome: str, conversor: Callable, minimo: float, maximo: Optional[float],
            descricao: str):
    bruto = _ler(nome)
    try:
        valor = conversor(bruto)
    except ValueError:
        raise ConfigError(f"{nome} deve ser {descricao} (recebido: {bruto!r}).") from None
    if valor < minimo or (maximo is not None and valor > maximo):
        raise ConfigError(f"{nome} deve ser {descricao} (recebido: {bruto!r}).")
    return valor


def _ler_prompt_sistema() -> Optional[str]:
    """Conteúdo do arquivo em LLM_SYSTEM_PROMPT_ARQUIVO, ou None para usar o embutido."""
    caminho = os.getenv("LLM_SYSTEM_PROMPT_ARQUIVO", "").strip()
    if not caminho:
        return None
    try:
        with open(caminho, encoding="utf-8") as f:
            conteudo = f.read().strip()
    except (OSError, UnicodeDecodeError):
        raise ConfigError(
            f"Não foi possível ler LLM_SYSTEM_PROMPT_ARQUIVO ({caminho}). "
            "Verifique o caminho e se o arquivo está em UTF-8."
        ) from None
    if not conteudo:
        raise ConfigError(f"O arquivo de prompt de sistema está vazio: {caminho}.")
    return conteudo


def obter_config() -> dict:
    """Lê e valida a configuração. Levanta ConfigError com mensagem clara se algo estiver errado."""
    load_dotenv()
    chave = os.getenv("GEMINI_API_KEY", "").strip()
    if not chave:
        raise ConfigError("Defina GEMINI_API_KEY no arquivo .env (veja o .env.example).")
    return {
        "api_key": chave,
        "modelo": _ler("GEMINI_MODEL"),
        "temperatura": _numero("LLM_TEMPERATURE", float, 0, 2, "um número entre 0 e 2"),
        "top_p": _numero("LLM_TOP_P", float, 0, 1, "um número entre 0 e 1"),
        "max_tokens": _numero("LLM_MAX_TOKENS", int, 1, None, "um inteiro maior que 0"),
        "timeout_segundos": _numero("LLM_TIMEOUT_SEGUNDOS", int, 1, None, "um inteiro maior que 0"),
        "prompt_sistema": _ler_prompt_sistema(),
    }


def resumo_seguro(config: dict) -> str:
    """Descrição da configuração para log — nunca inclui a chave de API."""
    return (
        f"modelo={config['modelo']} temperatura={config['temperatura']} "
        f"top_p={config['top_p']} max_tokens={config['max_tokens']} "
        f"timeout={config['timeout_segundos']}s "
        f"prompt_sistema={'arquivo' if config.get('prompt_sistema') else 'embutido'}"
    )
