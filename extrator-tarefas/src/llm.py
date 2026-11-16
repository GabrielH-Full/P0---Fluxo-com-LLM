"""Cliente do LLM (Google Gemini).

Isola a chamada à API e traduz qualquer falha em LLMError com mensagem
amigável — sem repassar ao usuário o texto cru da API nem a chave.
"""
import logging
import time

import httpx
from google import genai
from google.genai import errors, types

log = logging.getLogger(__name__)


class LLMError(Exception):
    pass


def _mensagem_client_error(codigo: int) -> str:
    if codigo in (401, 403):
        return "Chave de API inválida ou sem permissão. Verifique o GEMINI_API_KEY no .env."
    if codigo == 429:
        return "Limite de uso da API atingido. Aguarde e tente novamente."
    if codigo == 404:
        return "Modelo não encontrado. Verifique o GEMINI_MODEL no .env."
    return f"A API recusou a solicitação (código {codigo}). Verifique a configuração no .env."


def chamar_llm(system: str, user: str, config: dict) -> str:
    """Envia o prompt ao Gemini e devolve o texto da resposta."""
    client = genai.Client(
        api_key=config["api_key"],
        http_options=types.HttpOptions(timeout=config["timeout_segundos"] * 1000),
    )
    log.info("Enviando solicitação ao LLM (modelo=%s, entrada=%d caracteres)",
             config["modelo"], len(user))
    inicio = time.perf_counter()
    try:
        resposta = client.models.generate_content(
            model=config["modelo"],
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=config["temperatura"],
                top_p=config["top_p"],
                max_output_tokens=config["max_tokens"],
            ),
        )
    except errors.ClientError as e:
        log.error("Erro do cliente na API (código %s) após %.2fs", e.code, time.perf_counter() - inicio)
        raise LLMError(_mensagem_client_error(e.code)) from None
    except errors.ServerError as e:
        log.error("Erro do servidor da API (código %s) após %.2fs", e.code, time.perf_counter() - inicio)
        raise LLMError("Serviço do LLM indisponível no momento. Tente novamente em instantes.") from None
    except errors.APIError as e:
        log.error("Erro inesperado da API (código %s)", e.code)
        raise LLMError("A API retornou um erro inesperado. Tente novamente.") from None
    except httpx.TimeoutException:
        log.error("Tempo esgotado após %.2fs", time.perf_counter() - inicio)
        raise LLMError(
            f"Tempo esgotado: o LLM não respondeu em {config['timeout_segundos']}s. "
            "Tente novamente ou aumente LLM_TIMEOUT_SEGUNDOS no .env."
        ) from None
    except httpx.TransportError as e:
        log.error("Falha de conexão: %s", type(e).__name__)
        raise LLMError("Sem conexão com a API. Verifique sua internet.") from None

    duracao = time.perf_counter() - inicio
    texto = (resposta.text or "").strip()
    if not texto:
        log.warning("Resposta vazia do LLM após %.2fs", duracao)
        raise LLMError("O modelo não retornou conteúdo. Tente novamente.")
    log.info("Resposta recebida em %.2fs (%d caracteres)", duracao, len(texto))
    return texto
