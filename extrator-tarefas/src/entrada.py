import sys
from typing import Optional

from erros import mensagem_codificacao_invalida, mensagem_pasta_no_lugar_de_arquivo

LIMITE_CARACTERES = 20_000


class EntradaInvalidaError(Exception):
    pass


def ler_entrada(arquivo: Optional[str]) -> str:
    if arquivo:
        try:
            with open(arquivo, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise EntradaInvalidaError(f"Arquivo não encontrado: {arquivo}.")
        except IsADirectoryError:
            raise EntradaInvalidaError(mensagem_pasta_no_lugar_de_arquivo(arquivo)) from None
        except UnicodeDecodeError as e:
            raise EntradaInvalidaError(mensagem_codificacao_invalida(e, arquivo)) from None
    if sys.stdin.isatty():
        print("Cole as anotações da reunião e finalize com Ctrl+D (ou Ctrl+Z no Windows):")
    try:
        return sys.stdin.read()
    except UnicodeDecodeError as e:
        raise EntradaInvalidaError(mensagem_codificacao_invalida(e, None)) from None


def validar_entrada(texto: str) -> str:
    texto = texto.strip()
    if not texto:
        raise EntradaInvalidaError("Nenhuma anotação informada.")
    if len(texto) > LIMITE_CARACTERES:
        raise EntradaInvalidaError(
            f"Texto muito longo (máx. {LIMITE_CARACTERES} caracteres)."
        )
    return texto
