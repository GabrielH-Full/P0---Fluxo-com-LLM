"""Mensagens de erro personalizadas, explicativas para o usuário.

Centraliza o texto mostrado quando algo dá errado, para que o usuário entenda
o que aconteceu e como resolver, em vez de ver um stack trace do Python.
"""
import os
import sys
import traceback
from typing import Optional

# Código de saída usado quando a aplicação quebra por um erro não previsto.
CODIGO_ERRO_INESPERADO = 2


def mensagem_pasta_no_lugar_de_arquivo(caminho: str) -> str:
    """IsADirectoryError: o usuário passou uma pasta em --arquivo."""
    linhas = [
        f'"{caminho}" é uma pasta, não um arquivo.',
        "Informe o caminho de um arquivo .txt com as anotações.",
    ]
    try:
        txts = sorted(n for n in os.listdir(caminho) if n.lower().endswith(".txt"))
    except OSError:
        txts = []
    if txts:
        exemplo = os.path.join(caminho, txts[0])
        linhas.append(f"Arquivos .txt encontrados nessa pasta: {', '.join(txts[:3])}"
                      + (" ..." if len(txts) > 3 else ""))
        linhas.append(f"Exemplo: python src/main.py --arquivo {exemplo}")
    return "\n".join(linhas)


def mensagem_codificacao_invalida(erro: UnicodeDecodeError, caminho: Optional[str]) -> str:
    """UnicodeDecodeError: o arquivo (ou texto colado) não está em UTF-8."""
    origem = f'O arquivo "{caminho}"' if caminho else "O texto recebido"
    return "\n".join([
        f"{origem} não está em UTF-8 (caractere inválido na posição {erro.start}).",
        "Isso costuma acontecer com arquivos salvos em outra codificação (ex.: Latin-1 /",
        "ANSI, comum no Bloco de Notas antigo do Windows) ou que não são de texto.",
        "Como resolver: abra o arquivo e salve novamente com a codificação UTF-8.",
        "  - VS Code: clique na codificação na barra inferior > 'Salvar com codificação' > UTF-8",
        "  - Bloco de Notas: Arquivo > Salvar como > Codificação: UTF-8",
    ])


def mensagem_erro_inesperado(erro: BaseException) -> str:
    """Qualquer erro não previsto: a aplicação quebrou."""
    return "\n".join([
        "Ocorreu um erro inesperado e a aplicação não conseguiu continuar.",
        f"Detalhe técnico: {type(erro).__name__}: {erro}",
        "Para ver o erro completo, rode novamente com a variável EXTRATOR_DEBUG=1, ex.:",
        "  EXTRATOR_DEBUG=1 python src/main.py ...",
    ])


def exibir_erro(mensagem: str) -> None:
    print(f"Erro: {mensagem}", file=sys.stderr)


def exibir_erro_inesperado(erro: BaseException) -> None:
    exibir_erro(mensagem_erro_inesperado(erro))
    if os.getenv("EXTRATOR_DEBUG") == "1":
        traceback.print_exception(type(erro), erro, erro.__traceback__, file=sys.stderr)
