import pytest

from extrator import EntradaInvalida, extrair_tarefas
from tests.avaliador import avaliar, carregar_casos

DATA_REFERENCIA, CASOS = carregar_casos()


@pytest.mark.parametrize(
    "caso", CASOS, ids=[f"{c['id']}-{c['nome']}" for c in CASOS]
)
def test_cenario(caso):
    try:
        saida = extrair_tarefas(caso["entrada"], DATA_REFERENCIA)
    except EntradaInvalida:
        # erro controlado só é aceito nos cenários que permitem (entrada vazia/sem sentido)
        assert caso.get("aceita_erro_controlado"), "EntradaInvalida não esperada neste cenário"
        return

    erros = avaliar(caso, saida)
    assert not erros, "\n" + "\n".join(f"  - {e}" for e in erros)