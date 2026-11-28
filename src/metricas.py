"""Simulações e resumo dos experimentos.

Contrato:
  simular(n, dificuldade, nivel, seed, garantias) -> DataFrame (um Resultado por linha)
      -> fica para quando ambiente.py e agente.py existirem.
  resumir(df) -> DataFrame com as métricas por nível e dificuldade.
"""

import pandas as pd

from src.modelos import Acao, Resultado


def resultados_para_df(resultados: list[Resultado], **extras) -> pd.DataFrame:
    """Transforma uma lista de Resultado em tabela. extras = colunas fixas (ex.: nivel=2)."""
    linhas = []
    for r in resultados:
        linhas.append({
            **extras,
            "acao": r.acao.value,
            "tipo_real": r.tipo_real,
            "correta": r.correta,
            "tipo_decisao": r.tipo_decisao,
            "chance_monstro": r.chance_monstro,
            "passos": r.passos,
            "monstro_admitido": r.acao == Acao.PERMITIR and r.tipo_real == "monstro",
            "humano_morto": r.acao == Acao.MATAR and r.tipo_real == "humano",
        })
    return pd.DataFrame(linhas)


def resumir(df: pd.DataFrame) -> pd.DataFrame:
    """Métricas por grupo (nivel e/ou dificuldade, se existirem as colunas)."""
    grupos = [c for c in ("nivel", "dificuldade") if c in df.columns]
    if not grupos:
        df = df.assign(geral="todos")
        grupos = ["geral"]

    def pct(serie, valor):
        return (serie == valor).mean()

    resumo = df.groupby(grupos).agg(
        criaturas=("correta", "size"),
        acuracia=("correta", "mean"),
        passos_medios=("passos", "mean"),
        provadas=("tipo_decisao", lambda s: pct(s, "provada")),
        por_garantia=("tipo_decisao", lambda s: pct(s, "garantia")),
        forcadas=("tipo_decisao", lambda s: pct(s, "forcada")),
        monstros_admitidos=("monstro_admitido", "sum"),
        humanos_mortos=("humano_morto", "sum"),
    )
    # acurácia só das decisões provadas: tem que ser 100% (se não for, é bug)
    provadas = df[df["tipo_decisao"] == "provada"]
    if len(provadas):
        resumo["acuracia_provadas"] = provadas.groupby(grupos)["correta"].mean()
    return resumo.reset_index()