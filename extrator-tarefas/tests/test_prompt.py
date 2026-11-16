from datetime import date

from prompt import SYSTEM_PROMPT, montar_prompt


def test_data_de_referencia_no_formato_brasileiro():
    _, user = montar_prompt("ana faz x", date(2026, 11, 3))
    assert "Data de referência: 03/11/2026" in user


def test_anotacoes_ficam_delimitadas():
    _, user = montar_prompt("ana faz x\njoão faz y", date(2026, 11, 3))
    assert "<anotacoes>\nana faz x\njoão faz y\n</anotacoes>" in user


def test_usa_prompt_embutido_por_padrao():
    system, _ = montar_prompt("x", date(2026, 1, 1))
    assert system == SYSTEM_PROMPT


def test_usa_prompt_de_sistema_da_configuracao():
    system, _ = montar_prompt("x", date(2026, 1, 1), "Prompt alternativo")
    assert system == "Prompt alternativo"
