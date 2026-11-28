"""Resumo das métricas"""

import pytest

from src.metricas import resultados_para_df, resumir
from src.modelos import Acao, Resultado


def _r(acao, real, tipo, passos):
    correta = (acao == Acao.MATAR) == (real == "monstro")
    return Resultado(acao, real, correta, tipo, 0.9, passos, [])


def test_resumo_conta_acertos_erros_e_tipos():
    resultados = [
        _r(Acao.MATAR, "monstro", "provada", 2),
        _r(Acao.PERMITIR, "humano", "garantia", 4),
        _r(Acao.MATAR, "humano", "forcada", 6),     # humano morto
        _r(Acao.PERMITIR, "monstro", "garantia", 5),  # monstro admitido
    ]
    resumo = resumir(resultados_para_df(resultados, nivel=1, dificuldade="medio")).iloc[0]
    assert resumo["criaturas"] == 4
    assert resumo["acuracia"] == pytest.approx(0.5)
    assert resumo["passos_medios"] == pytest.approx(4.25)
    assert resumo["forcadas"] == pytest.approx(0.25)
    assert resumo["monstros_admitidos"] == 1
    assert resumo["humanos_mortos"] == 1
    assert resumo["acuracia_provadas"] == pytest.approx(1.0)