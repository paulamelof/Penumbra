import math
from dataclasses import dataclass, field

from src.base_conhecimento import BaseConhecimento


@dataclass
class Calculo:
    chance_monstro: float  # de 0 a 1
    razao: float  # razão de chances r (monstro : humano)
    prova: str | None  # "monstro", "humano" ou None (nada provado)
    explicadas: list[str] = field(default_factory=list)  # ambíguas anuladas
    regras: list[str] = field(default_factory=list)  # regras que dispararam


def provar(fatos, base: BaseConhecimento) -> tuple[str | None, list[str]]:
    """Camada lógica de certeza: alguma específica apareceu?

    Devolve ("monstro" | "humano" | None, regras usadas).
    """
    fatos = list(dict.fromkeys(fatos))  # tira repetidos, mantém a ordem
    # regras de certeza que dispararam (uma por específica vista)
    disparadas = [base.certeza_por_id[f] for f in fatos if f in base.certeza_por_id]
    provas_monstro = [r for r in disparadas if r.conclusao == "monstro"]
    provas_humano = [r for r in disparadas if r.conclusao == "humano"]

    # RB04: nunca se prova os dois ao mesmo tempo. Se acontecer, o ambiente tem bug.
    if provas_monstro and provas_humano:
        raise ValueError(
            f"Contradição: {[r.premissa for r in provas_monstro]} provam monstro "
            f"e {[r.premissa for r in provas_humano]} provam humano"
        )

    if provas_monstro:
        return "monstro", [f"certeza: {r}" for r in provas_monstro]
    if provas_humano:
        return "humano", [f"certeza: {r}" for r in provas_humano]
    return None, []


def anulacoes(fatos, base: BaseConhecimento) -> list[tuple[str, str]]:
    """Camada lógica de anulação: pares (atenuante, ambígua) em que AS DUAS já foram vistas (RB02)."""
    vistos = set(fatos)
    return [(r.atenuante, r.ambigua) for r in base.regras_anulacao
            if r.atenuante in vistos and r.ambigua in vistos]


def chance_monstro(fatos, base: BaseConhecimento) -> Calculo:
    """Chance de ser monstro dadas todas as pistas vistas. Sempre recalcula do zero."""
    fatos = list(dict.fromkeys(fatos))

    # 1) Certeza vence tudo (RB01): 100% ou 0%.
    prova, regras = provar(fatos, base)
    if prova == "monstro":
        return Calculo(1.0, math.inf, prova, [], regras)
    if prova == "humano":
        return Calculo(0.0, 0.0, prova, [], regras)

    # 2) Anulação: ambígua explicada deixa de contar (fator volta a ×1).
    pares = anulacoes(fatos, base)
    explicadas = [amb for _, amb in pares]
    regras = [f"anulação: {aten} explica {amb}" for aten, amb in pares]

    # 3) Naive Bayes: começa em 1:1 e multiplica o fator de cada pista não explicada.
    #    Somamos logaritmos em vez de multiplicar (evita números gigantes/zerados).
    soma_log = 0.0  # log(1) = 0, ou seja, razão inicial 1:1
    for f in fatos:
        if f in explicadas:
            continue
        soma_log += math.log(base.fatores[f])

    razao = math.exp(soma_log)
    chance = 1.0 / (1.0 + math.exp(-soma_log))  # igual a r / (1 + r)
    return Calculo(chance, razao, None, explicadas, regras)
