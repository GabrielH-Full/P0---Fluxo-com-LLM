"""Regras de avaliação dos cenários de teste.

avaliar(caso, saida) devolve uma lista de erros. Lista vazia = cenário passou.
"""
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

ARQUIVO_CASOS = Path(__file__).parent / "casos_de_teste.json"
CAMPOS = {"responsavel", "acao", "prazo"}


def carregar_casos():
    dados = json.loads(ARQUIVO_CASOS.read_text(encoding="utf-8"))
    return dados["data_referencia"], dados["casos"]


def normalizar(texto):
    """minúsculas, sem acento, sem espaços nas pontas."""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().strip()


def validar_schema(saida):
    """Contrato: {"tarefas": [{"responsavel": str|None, "acao": str, "prazo": 'AAAA-MM-DD'|None}]}"""
    erros = []
    if not isinstance(saida, dict) or set(saida.keys()) != {"tarefas"}:
        return ["saída deve ser um dict com exatamente a chave 'tarefas'"]
    if not isinstance(saida["tarefas"], list):
        return ["'tarefas' deve ser uma lista"]

    for i, t in enumerate(saida["tarefas"]):
        if not isinstance(t, dict) or set(t.keys()) != CAMPOS:
            erros.append(f"tarefa {i}: campos devem ser exatamente {sorted(CAMPOS)}")
            continue
        resp, acao, prazo = t["responsavel"], t["acao"], t["prazo"]
        if resp is not None and (not isinstance(resp, str) or not resp.strip()):
            erros.append(f"tarefa {i}: responsavel deve ser string não vazia ou null")
        if not isinstance(acao, str) or not acao.strip():
            erros.append(f"tarefa {i}: acao deve ser string não vazia")
        if prazo is not None:
            if not isinstance(prazo, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", prazo):
                erros.append(f"tarefa {i}: prazo deve ser AAAA-MM-DD ou null (veio {prazo!r})")
            else:
                try:
                    date.fromisoformat(prazo)
                except ValueError:
                    erros.append(f"tarefa {i}: prazo é uma data inexistente ({prazo})")
    return erros


def _responsavel_ok(esperado, obtido):
    if esperado is None:
        return obtido is None
    if obtido is None:
        return False
    aceitos = esperado if isinstance(esperado, list) else [esperado]
    return normalizar(obtido) in {normalizar(a) for a in aceitos}


def _tarefa_confere(exp, obt):
    acao = normalizar(obt["acao"])
    return (
        _responsavel_ok(exp["responsavel"], obt["responsavel"])
        and exp["prazo"] == obt["prazo"]
        and all(normalizar(p) in acao for p in exp["acao_palavras"])
    )


def avaliar(caso, saida):
    erros = validar_schema(saida)
    if erros:
        return erros

    obtidas = saida["tarefas"]
    esperadas = caso["esperado"]

    if len(obtidas) != len(esperadas):
        erros.append(f"número de tarefas: esperado {len(esperadas)}, obtido {len(obtidas)}")

    # casamento sem ordem: cada esperada precisa achar uma obtida ainda livre
    livres = list(range(len(obtidas)))
    for exp in esperadas:
        achou = next((i for i in livres if _tarefa_confere(exp, obtidas[i])), None)
        if achou is None:
            erros.append(
                f"não encontrada: responsavel={exp['responsavel']!r}, "
                f"acao contém {exp['acao_palavras']}, prazo={exp['prazo']!r}"
            )
        else:
            livres.remove(achou)

    for i in livres:
        erros.append(f"tarefa extra/inesperada: {obtidas[i]}")
    return erros