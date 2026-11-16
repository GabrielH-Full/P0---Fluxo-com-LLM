import pytest

from entrada import LIMITE_CARACTERES, EntradaInvalidaError, ler_entrada, validar_entrada


@pytest.mark.parametrize("texto", ["", "   ", "\n\t \n"])
def test_texto_vazio_ou_so_espacos_e_rejeitado(texto):
    with pytest.raises(EntradaInvalidaError, match="Nenhuma anotação"):
        validar_entrada(texto)


def test_texto_no_limite_e_aceito():
    assert len(validar_entrada("a" * LIMITE_CARACTERES)) == LIMITE_CARACTERES


def test_texto_acima_do_limite_e_rejeitado():
    with pytest.raises(EntradaInvalidaError, match="muito longo"):
        validar_entrada("a" * (LIMITE_CARACTERES + 1))


def test_validar_remove_espacos_das_pontas():
    assert validar_entrada("  joão faz x  \n") == "joão faz x"


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(EntradaInvalidaError, match="Arquivo não encontrado"):
        ler_entrada(str(tmp_path / "nao_existe.txt"))


def test_pasta_no_lugar_de_arquivo_sugere_txt(tmp_path):
    (tmp_path / "notas.txt").write_text("x", encoding="utf-8")
    with pytest.raises(EntradaInvalidaError) as erro:
        ler_entrada(str(tmp_path))
    assert "é uma pasta" in str(erro.value)
    assert "notas.txt" in str(erro.value)


def test_arquivo_latin1_orienta_salvar_em_utf8(tmp_path):
    arquivo = tmp_path / "latin1.txt"
    arquivo.write_bytes("reunião às 10h".encode("latin-1"))
    with pytest.raises(EntradaInvalidaError, match="não está em UTF-8"):
        ler_entrada(str(arquivo))


def test_arquivo_utf8_e_lido(tmp_path):
    arquivo = tmp_path / "ok.txt"
    arquivo.write_text("carla manda a ata", encoding="utf-8")
    assert ler_entrada(str(arquivo)) == "carla manda a ata"
