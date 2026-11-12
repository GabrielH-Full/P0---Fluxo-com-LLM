import os
from dotenv import load_dotenv


class ConfigError(Exception):
    pass


def obter_config():
    load_dotenv()
    chave = os.getenv("GEMINI_API_KEY")
    if not chave:
        raise ConfigError(
            "Defina GEMINI_API_KEY no arquivo .env (veja o .env.example)."
        )
    modelo = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    return {"api_key": chave, "modelo": modelo}
