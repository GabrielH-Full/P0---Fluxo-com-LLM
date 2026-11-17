import pytest

from config import ConfigError, obter_config, resumo_seguro


def test_sem_chave_levanta_config_error():
    with pytest.raises(ConfigError, match="GEMINI_API_KEY"):
        obter_config()


def test_valores_padrao_quando_variaveis_ausentes(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AQ.teste")
    config = obter_config()
    assert config["modelo"] == "gemini-2.0-flash"
    assert config["temperatura"] == 0.0
    assert config["top_p"] == 1.0
    assert config["max_tokens"] == 1024
    assert config["timeout_segundos"] == 30
    assert config["prompt_sistema"] is None


def test_valores_lidos_do_ambiente(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AQ.teste")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-outro")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.7")
    monkeypatch.setenv("LLM_TOP_P", "0.9")
    monkeypatch.setenv("LLM_MAX_TOKENS", "2048")
    monkeypatch.setenv("LLM_TIMEOUT_SEGUNDOS", "10")
    config = obter_config()
    assert (config["modelo"], config["temperatura"], config["top_p"],
            config["max_tokens"], config["timeout_segundos"]) == ("gemini-outro", 0.7, 0.9, 2048, 10)


@pytest.mark.parametrize("nome, valor", [
    ("LLM_TEMPERATURE", "abc"),
    ("LLM_TEMPERATURE", "3"),
    ("LLM_TOP_P", "1.5"),
    ("LLM_MAX_TOKENS", "0"),
    ("LLM_MAX_TOKENS", "1.5"),
    ("LLM_TIMEOUT_SEGUNDOS", "-1"),
])
def test_valor_invalido_levanta_config_error(monkeypatch, nome, valor):
    monkeypatch.setenv("GEMINI_API_KEY", "AQ.teste")
    monkeypatch.setenv(nome, valor)
    with pytest.raises(ConfigError, match=nome):
        obter_config()


def test_prompt_de_sistema_lido_de_arquivo(monkeypatch, tmp_path):
    arquivo = tmp_path / "prompt.txt"
    arquivo.write_text("Responda só com a lista.", encoding="utf-8")
    monkeypatch.setenv("GEMINI_API_KEY", "AQ.teste")
    monkeypatch.setenv("LLM_SYSTEM_PROMPT_ARQUIVO", str(arquivo))
    assert obter_config()["prompt_sistema"] == "Responda só com a lista."


def test_prompt_de_sistema_inexistente(monkeypatch, tmp_path):
    monkeypatch.setenv("GEMINI_API_KEY", "AQ.teste")
    monkeypatch.setenv("LLM_SYSTEM_PROMPT_ARQUIVO", str(tmp_path / "nao_existe.txt"))
    with pytest.raises(ConfigError, match="LLM_SYSTEM_PROMPT_ARQUIVO"):
        obter_config()


def test_resumo_seguro_nao_contem_a_chave(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AQ.segredo123")
    resumo = resumo_seguro(obter_config())
    assert "segredo123" not in resumo
    assert "modelo=gemini-2.0-flash" in resumo
