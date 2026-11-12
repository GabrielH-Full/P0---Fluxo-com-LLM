import argparse
import os
import sys
from datetime import date, datetime

from config import obter_config, ConfigError
from entrada import ler_entrada, validar_entrada, EntradaInvalidaError
from prompt import montar_prompt
from llm import chamar_llm, LLMError


def parse_data(valor: str) -> date:
    try:
        return datetime.strptime(valor, "%d/%m/%Y").date()
    except ValueError:
        raise argparse.ArgumentTypeError("Use o formato DD/MM/AAAA.")


def _perguntar_salvar(resultado: str, data: date) -> None:
    try:
        fd = os.open("/dev/tty", os.O_RDWR)
        os.write(fd, b"\nSalvar lista em arquivo? [Y/N]: ")
        chars = b""
        while True:
            ch = os.read(fd, 1)
            if ch in (b"\n", b"\r") or not ch:
                break
            chars += ch
        os.close(fd)
        resposta = chars.decode("utf-8", errors="ignore").strip().upper()
    except (OSError, KeyboardInterrupt):
        return
    if resposta != "Y":
        return
    nome = f"tarefas_{data.strftime('%d-%m-%Y')}.txt"
    with open(nome, "w", encoding="utf-8") as f:
        f.write(resultado + "\n")
    print(f"\nSalvo em: {nome}")


def main():
    parser = argparse.ArgumentParser(
        description="Transforma anotações de reunião em lista de tarefas."
    )
    parser.add_argument(
        "--arquivo", "-a",
        metavar="ARQUIVO",
        help="Caminho para um .txt com as anotações.",
    )
    parser.add_argument(
        "--texto", "-t",
        metavar="TEXTO",
        help="Anotações passadas diretamente como texto.",
    )
    parser.add_argument(
        "--data", "-d",
        metavar="DD/MM/AAAA",
        type=parse_data,
        default=date.today(),
        help="Data de referência da reunião (padrão: hoje).",
    )
    args = parser.parse_args()

    try:
        config = obter_config()
        texto_bruto = args.texto if args.texto else ler_entrada(args.arquivo)
        anotacoes = validar_entrada(texto_bruto)
        system, user = montar_prompt(anotacoes, args.data)
        resultado = chamar_llm(system, user, config)
        print(resultado)
        _perguntar_salvar(resultado, args.data)
    except (ConfigError, EntradaInvalidaError, LLMError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
