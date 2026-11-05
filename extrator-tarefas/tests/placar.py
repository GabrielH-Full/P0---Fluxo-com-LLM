"""Roda todos os cenários e mostra o placar.

Uso (na raiz do projeto):  python -m tests.placar
Opções:  -v  mostra os detalhes dos erros
"""
import sys

from extrator import EntradaInvalida, extrair_tarefas
from tests.avaliador import avaliar, carregar_casos


def main():
    verboso = "-v" in sys.argv
    data_ref, casos = carregar_casos()
    passou = 0

    print(f"Data de referência: {data_ref}\n")
    for caso in casos:
        try:
            saida = extrair_tarefas(caso["entrada"], data_ref)
            erros = avaliar(caso, saida)
        except EntradaInvalida:
            erros = [] if caso.get("aceita_erro_controlado") else ["EntradaInvalida não esperada"]
        except Exception as e:  # qualquer outra falha = quebrou
            erros = [f"exceção: {type(e).__name__}: {e}"]

        ok = not erros
        passou += ok
        print(f"[{'PASSOU' if ok else 'FALHOU'}] {str(caso['id']):>3}  {caso['nome']}")
        if erros and verboso:
            for e in erros:
                print(f"           - {e}")

    total = len(casos)
    print(f"\nPlacar: {passou}/{total} ({passou / total:.0%})")
    sys.exit(0 if passou == total else 1)


if __name__ == "__main__":
    main()