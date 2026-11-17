"""Roda o fluxo completo do main.py para cada caso de tests/casos, com o LLM simulado."""
import glob
import os
import sys

import pytest

import main

CASOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "casos")
ESPERADO_ERRO = {
    "03_vazio.txt": "Nenhuma anotação",
    "04_so_espacos.txt": "Nenhuma anotação",
    "17_encoding_latin1.txt": "não está em UTF-8",
    "19_acima_do_limite.txt": "muito longo",
}
RESPOSTA_FALSA = "1. Responsável: Ana | Ação: Teste | Prazo: não informado"


@pytest.fixture
def fluxo_simulado(monkeypatch, config_falsa):
    prompts = []

    def llm_falso(system, user, config):
        prompts.append(user)
        return RESPOSTA_FALSA

    monkeypatch.setattr(main, "obter_config", lambda: config_falsa)
    monkeypatch.setattr(main, "chamar_llm", llm_falso)
    monkeypatch.setattr(main, "configurar_logs", lambda: None)
    monkeypatch.setattr(main, "_perguntar_salvar", lambda resultado, data: None)
    return prompts


def _rodar(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", ["main.py", *argv])
    try:
        main.main()
    except SystemExit as e:
        return e.code
    return 0


@pytest.mark.parametrize("caminho", sorted(glob.glob(os.path.join(CASOS, "*.txt"))),
                         ids=os.path.basename)
def test_caso(caminho, fluxo_simulado, monkeypatch, capsys):
    nome = os.path.basename(caminho)
    codigo = _rodar(monkeypatch, ["--arquivo", caminho, "--data", "13/11/2026"])
    saida = capsys.readouterr()
    if nome in ESPERADO_ERRO:
        assert codigo == 1
        assert ESPERADO_ERRO[nome] in saida.err
        assert fluxo_simulado == []  # o LLM nem foi chamado
    else:
        assert codigo == 0, saida.err
        assert RESPOSTA_FALSA in saida.out
        assert "Data de referência: 13/11/2026" in fluxo_simulado[0]


def test_texto_direto(fluxo_simulado, monkeypatch, capsys):
    assert _rodar(monkeypatch, ["--texto", "pedro revisa o dashboard", "--data", "10/11/2026"]) == 0
    assert RESPOSTA_FALSA in capsys.readouterr().out


def test_data_invalida_e_rejeitada(fluxo_simulado, monkeypatch, capsys):
    assert _rodar(monkeypatch, ["--texto", "x", "--data", "2026-11-10"]) == 2
    assert "DD/MM/AAAA" in capsys.readouterr().err


def test_sem_chave_mostra_mensagem_de_configuracao(monkeypatch, capsys):
    monkeypatch.setattr(main, "configurar_logs", lambda: None)
    assert _rodar(monkeypatch, ["--texto", "x"]) == 1
    assert "Defina GEMINI_API_KEY" in capsys.readouterr().err


def test_erro_inesperado_nao_expoe_detalhe(fluxo_simulado, monkeypatch, capsys):
    def explode(*a):
        raise RuntimeError("detalhe interno AQ.segredo")
    monkeypatch.setattr(main, "chamar_llm", explode)
    assert _rodar(monkeypatch, ["--texto", "x"]) == main.CODIGO_ERRO_INESPERADO
    err = capsys.readouterr().err
    assert "RuntimeError" in err
    assert "AQ.segredo" not in err
