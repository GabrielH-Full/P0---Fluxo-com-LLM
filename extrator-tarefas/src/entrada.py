import sys
from typing import Optional

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
    if sys.stdin.isatty():
        print("Cole as anotações da reunião e finalize com Ctrl+D (ou Ctrl+Z no Windows):")
    return sys.stdin.read()


def validar_entrada(texto: str) -> str:
    texto = texto.strip()
    if not texto:
        raise EntradaInvalidaError("Nenhuma anotação informada.")
    if len(texto) > LIMITE_CARACTERES:
        raise EntradaInvalidaError(
            f"Texto muito longo (máx. {LIMITE_CARACTERES} caracteres)."
        )
    return texto
