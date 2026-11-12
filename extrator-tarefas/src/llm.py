from google import genai
from google.genai import types
from google.api_core.exceptions import (
    Unauthenticated,
    ResourceExhausted,
    ServiceUnavailable,
    GoogleAPIError,
)


class LLMError(Exception):
    pass


def chamar_llm(system: str, user: str, config: dict) -> str:
    client = genai.Client(api_key=config["api_key"])
    try:
        resposta = client.models.generate_content(
            model=config["modelo"],
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0,
                max_output_tokens=1024,
            ),
        )
        return resposta.text
    except Unauthenticated:
        raise LLMError("Chave de API inválida. Verifique o GEMINI_API_KEY no .env.")
    except ResourceExhausted:
        raise LLMError("Limite de uso da API atingido. Aguarde e tente novamente.")
    except ServiceUnavailable:
        raise LLMError("Sem conexão com a API. Verifique sua internet.")
    except GoogleAPIError as e:
        raise LLMError(f"Erro da API: {e}")
