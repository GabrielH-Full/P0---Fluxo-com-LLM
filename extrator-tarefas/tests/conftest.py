"""Configuração comum dos testes: nenhum teste usa a chave real nem chama a API."""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

VARIAVEIS = (
    "GEMINI_API_KEY", "GEMINI_MODEL", "LLM_TEMPERATURE", "LLM_TOP_P", "LLM_MAX_TOKENS",
    "LLM_TIMEOUT_SEGUNDOS", "LLM_SYSTEM_PROMPT_ARQUIVO", "LOG_LEVEL", "LOG_ARQUIVO",
)


@pytest.fixture(autouse=True)
def ambiente_isolado(monkeypatch):
    """Remove variáveis do ambiente e impede a leitura do .env real."""
    for nome in VARIAVEIS:
        monkeypatch.delenv(nome, raising=False)
    import config
    import main
    monkeypatch.setattr(config, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setattr(main, "load_dotenv", lambda *a, **k: None)


@pytest.fixture
def config_falsa():
    return {
        "api_key": "AQ.chave-secreta-de-teste", "modelo": "gemini-teste", "temperatura": 0.0,
        "top_p": 1.0, "max_tokens": 1024, "timeout_segundos": 30, "prompt_sistema": None,
    }
