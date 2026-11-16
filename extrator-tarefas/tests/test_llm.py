"""Testa o cliente do LLM com o SDK simulado — nenhuma requisição real é feita."""
import logging
from unittest.mock import MagicMock, patch

import httpx
import pytest
from google.genai import errors

from llm import LLMError, chamar_llm

CORPO_COM_SEGREDO = {"error": {"message": "API key AQ.chave-secreta-de-teste not valid"}}


def _cliente_que(resposta=None, erro=None):
    cliente = MagicMock()
    if erro is not None:
        cliente.models.generate_content.side_effect = erro
    else:
        cliente.models.generate_content.return_value = resposta
    return cliente


def test_resposta_simulada_devolve_o_texto(config_falsa):
    resposta = MagicMock(text="1. Responsável: Ana | Ação: X | Prazo: não informado\n")
    with patch("llm.genai.Client", return_value=_cliente_que(resposta)) as client:
        assert chamar_llm("sys", "user", config_falsa).startswith("1. Responsável: Ana")
    client.assert_called_once()


def test_parametros_vem_da_configuracao(config_falsa):
    config_falsa.update(temperatura=0.5, top_p=0.8, max_tokens=256, timeout_segundos=7)
    cliente = _cliente_que(MagicMock(text="ok"))
    with patch("llm.genai.Client", return_value=cliente) as client:
        chamar_llm("sys", "user", config_falsa)
    assert client.call_args.kwargs["http_options"].timeout == 7000
    chamada = cliente.models.generate_content.call_args.kwargs
    assert chamada["model"] == "gemini-teste"
    assert chamada["config"].temperature == 0.5
    assert chamada["config"].top_p == 0.8
    assert chamada["config"].max_output_tokens == 256
    assert chamada["config"].system_instruction == "sys"


@pytest.mark.parametrize("texto", [None, "", "   \n"])
def test_resposta_vazia_vira_llm_error(config_falsa, texto):
    with patch("llm.genai.Client", return_value=_cliente_que(MagicMock(text=texto))):
        with pytest.raises(LLMError, match="não retornou conteúdo"):
            chamar_llm("sys", "user", config_falsa)


@pytest.mark.parametrize("erro, trecho", [
    (errors.ClientError(401, CORPO_COM_SEGREDO), "Chave de API inválida"),
    (errors.ClientError(403, CORPO_COM_SEGREDO), "Chave de API inválida"),
    (errors.ClientError(429, CORPO_COM_SEGREDO), "Limite de uso"),
    (errors.ClientError(404, CORPO_COM_SEGREDO), "Modelo não encontrado"),
    (errors.ClientError(400, CORPO_COM_SEGREDO), "código 400"),
    (errors.ClientError(400, {"error": {"message": "API key AQ.chave-secreta-de-teste not valid",
                                        "details": [{"reason": "API_KEY_INVALID"}]}}),
     "Chave de API inválida"),
    (errors.ServerError(503, CORPO_COM_SEGREDO), "indisponível"),
    (httpx.ReadTimeout("timeout"), "Tempo esgotado"),
    (httpx.ConnectError("sem rede"), "Sem conexão"),
])
def test_erros_viram_mensagem_amigavel_sem_segredo(config_falsa, caplog, erro, trecho):
    caplog.set_level(logging.DEBUG)
    with patch("llm.genai.Client", return_value=_cliente_que(erro=erro)):
        with pytest.raises(LLMError) as capturado:
            chamar_llm("sys", "user", config_falsa)
    mensagem = str(capturado.value)
    assert trecho in mensagem
    assert "chave-secreta" not in mensagem
    assert "not valid" not in mensagem  # texto cru da API não chega ao usuário
    assert "chave-secreta" not in caplog.text
    assert capturado.value.__cause__ is None


def test_logs_nao_contem_entrada_nem_resposta(config_falsa, caplog):
    caplog.set_level(logging.DEBUG)
    resposta = MagicMock(text="RESPOSTA-SIGILOSA")
    with patch("llm.genai.Client", return_value=_cliente_que(resposta)):
        chamar_llm("sys", "ANOTACAO-SIGILOSA", config_falsa)
    assert "ANOTACAO-SIGILOSA" not in caplog.text
    assert "RESPOSTA-SIGILOSA" not in caplog.text
    assert "AQ.chave-secreta" not in caplog.text
    assert "Resposta recebida em" in caplog.text
