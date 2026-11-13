"""Roda os casos de tests/casos sem chamar o LLM (não gasta chamadas de API).

Executa o fluxo completo do main.py (argumentos, leitura, validação e montagem
do prompt), mas troca a chamada ao LLM por uma resposta falsa e pula a
pergunta de salvar.

Uso (a partir da pasta extrator-tarefas):
    python tests/rodar_casos_local.py                # todos os casos
    python tests/rodar_casos_local.py 11 17          # só os casos que começam com 11 ou 17
    python tests/rodar_casos_local.py -v             # mostra também o prompt enviado
"""
import contextlib
import glob
import io
import os
import sys
import types

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

# Substitui o módulo llm antes de importar o main: assim nem o SDK do Google
# precisa estar instalado e nenhuma requisição é feita.
class LLMError(Exception):
    pass

prompts_enviados = []

def chamar_llm_falso(system, user, config):
    prompts_enviados.append(user)
    return "1. Responsável: (falso) | Ação: (resposta simulada) | Prazo: não informado"

sys.modules["llm"] = types.SimpleNamespace(chamar_llm=chamar_llm_falso, LLMError=LLMError)

import main  # noqa: E402

main.obter_config = lambda: None                 # não exige .env / chave
main._perguntar_salvar = lambda resultado, data: None  # não trava esperando Y/N

DATA = "13/11/2026"


def rodar(argv):
    """Roda main.main() com os argumentos dados e devolve (status, saída)."""
    sys.argv = ["main.py", *argv]
    out, err = io.StringIO(), io.StringIO()
    codigo = 0
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            main.main()
    except SystemExit as e:
        codigo = e.code or 0
    except Exception as e:  # qualquer exceção não tratada = a aplicação quebrou
        return "QUEBRA", f"{type(e).__name__}: {str(e)[:90]}"
    if codigo == 0:
        return "OK", out.getvalue().strip().splitlines()[-1][:90]
    primeira_linha = err.getvalue().strip().splitlines()[0][:90]
    if codigo == main.CODIGO_ERRO_INESPERADO:  # main capturou um erro não previsto
        detalhe = next((l for l in err.getvalue().splitlines() if "Detalhe técnico" in l), primeira_linha)
        return "QUEBRA", detalhe.strip()[:90]
    return "ERRO", primeira_linha  # erro tratado, com mensagem


def main_testes():
    args = [a for a in sys.argv[1:] if a != "-v"]
    verboso = "-v" in sys.argv[1:]

    arquivos = sorted(glob.glob(os.path.join(RAIZ, "tests", "casos", "*.txt")))
    if args:
        arquivos = [a for a in arquivos if os.path.basename(a).startswith(tuple(args))]

    cenarios = [(os.path.basename(a), ["--arquivo", a, "--data", DATA]) for a in arquivos]
    if not args:
        cenarios += [
            ("[arquivo inexistente]", ["--arquivo", "tests/casos/nao_existe.txt", "--data", DATA]),
            ("[pasta no lugar de arquivo]", ["--arquivo", os.path.join(RAIZ, "tests", "casos"), "--data", DATA]),
            ("[--texto]", ["--texto", "pedro revisa o dashboard até quarta", "--data", DATA]),
            ("[--texto vazio]", ["--texto", "   ", "--data", DATA]),
        ]

    contagem = {"OK": 0, "ERRO": 0, "QUEBRA": 0}
    for nome, argv in cenarios:
        prompts_enviados.clear()
        status, detalhe = rodar(argv)
        contagem[status] += 1
        print(f"{status:7} {nome:42} {detalhe}")
        if verboso and prompts_enviados:
            print("        prompt enviado:\n        " + prompts_enviados[0][:400].replace("\n", "\n        "))

    print(f"\nOK: {contagem['OK']}  |  ERRO tratado: {contagem['ERRO']}  |  QUEBRA: {contagem['QUEBRA']}")
    sys.exit(1 if contagem["QUEBRA"] else 0)


if __name__ == "__main__":
    main_testes()
