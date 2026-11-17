"""Ponto de entrada: lê as anotações, monta o prompt, chama o LLM e exibe as tarefas."""
import argparse
import logging
import sys
import time
from datetime import date, datetime

try:
    import termios
except ImportError:  # Windows
    termios = None

from dotenv import load_dotenv

from config import obter_config, resumo_seguro, ConfigError
from entrada import ler_entrada, validar_entrada, EntradaInvalidaError
from erros import CODIGO_ERRO_INESPERADO, exibir_erro, exibir_erro_inesperado
from prompt import montar_prompt
from llm import chamar_llm, LLMError
from registro import configurar_logs

log = logging.getLogger("extrator")


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

    load_dotenv()
    configurar_logs()
    inicio = time.perf_counter()
    log.info("Início da execução")
    codigo = 0
    try:
        config = obter_config()
        log.info("Configuração carregada: %s", resumo_seguro(config))
        texto_bruto = args.texto if args.texto else ler_entrada(args.arquivo)
        anotacoes = validar_entrada(texto_bruto)
        log.info("Entrada válida: %d caracteres", len(anotacoes))
        system, user = montar_prompt(anotacoes, args.data, config["prompt_sistema"])
        resultado = chamar_llm(system, user, config)
        print(resultado)
        _perguntar_salvar(resultado, args.data)
    except (ConfigError, EntradaInvalidaError, LLMError) as e:
        log.error("Execução interrompida: %s", type(e).__name__)
        exibir_erro(str(e))
        codigo = 1
    except KeyboardInterrupt:
        log.warning("Execução cancelada pelo usuário")
        exibir_erro("Operação cancelada pelo usuário.")
        codigo = 130
    except Exception as e:
        log.error("Erro inesperado: %s", type(e).__name__)
        exibir_erro_inesperado(e)
        codigo = CODIGO_ERRO_INESPERADO
    log.info("Fim da execução (código %d, %.2fs)", codigo, time.perf_counter() - inicio)
    if codigo:
        sys.exit(codigo)


if __name__ == "__main__":
    main()
