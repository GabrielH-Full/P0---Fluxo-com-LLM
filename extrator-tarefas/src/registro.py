"""Configuração dos registros (logs) da aplicação.

Os logs vão para o stderr (e, opcionalmente, para um arquivo) e nunca devem
conter a chave de API, o texto das anotações ou a resposta integral do LLM —
apenas metadados como modelo, tamanhos e duração.
"""
import logging
import os

FORMATO = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configurar_logs() -> None:
    """Nível via LOG_LEVEL (padrão INFO); arquivo opcional via LOG_ARQUIVO."""
    nivel_nome = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    nivel = getattr(logging, nivel_nome, None)
    if not isinstance(nivel, int):
        nivel = logging.INFO

    handlers = [logging.StreamHandler()]
    arquivo = os.getenv("LOG_ARQUIVO", "").strip()
    if arquivo:
        handlers.append(logging.FileHandler(arquivo, encoding="utf-8"))

    logging.basicConfig(level=nivel, format=FORMATO, handlers=handlers, force=True)
    # Bibliotecas de rede podem registrar URLs e headers em DEBUG: manter caladas.
    for ruidosa in ("httpx", "httpcore", "google_genai", "urllib3"):
        logging.getLogger(ruidosa).setLevel(logging.WARNING)
