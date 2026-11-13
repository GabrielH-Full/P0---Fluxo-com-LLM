import argparse
import sys
from datetime import date, datetime

try:
    import termios
except ImportError:  # Windows
    termios = None

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
        tty_in = open("/dev/tty", "r", encoding="utf-8", errors="ignore")
        tty_out = open("/dev/tty", "w", encoding="utf-8")
    except OSError:
        return
    with tty_in, tty_out:
        # Descarta entrada pendente no terminal (ex.: Ctrl+D extra usado para
        # finalizar a colagem das anotações), senão ela é lida como resposta vazia.
        if termios is not None:
            try:
                termios.tcflush(tty_in.fileno(), termios.TCIFLUSH)
            except (termios.error, OSError):
                pass
        resposta = ""
        try:
            for _ in range(3):
                tty_out.write("\nSalvar lista em arquivo? [Y/N]: ")
                tty_out.flush()
                resposta = tty_in.readline().strip().upper()
                if resposta in ("Y", "N"):
                    break
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
