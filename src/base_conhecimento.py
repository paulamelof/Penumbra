"""Base de conhecimento montada a partir do catálogo (RB03: nada escrito à mão).

Contrato: montar_base(catalogo) -> BaseConhecimento, com
  - regras de certeza (R): uma específica prova o lado dela;
  - regras de anulação (A): ambígua ∧ atenuante -> Explicada(ambígua);
  - fator de cada característica: p_monstro ÷ p_humano
    (0 para específica de humano, infinito para específica de monstro).
"""

import math
from dataclasses import dataclass, field

from src.modelos import Caracteristica

MONSTRO = "monstro"
HUMANO = "humano"


@dataclass(frozen=True)
class RegraCerteza:
  """R: premissa -> conclusao (MONSTRO ou HUMANO)."""

  id: str
  premissa: str
  conclusao: str

  def __str__(self) -> str:
    return f"{self.id}: {self.premissa} → {self.conclusao.capitalize()}"


@dataclass(frozen=True)
class RegraAnulacao:
  """A: ambigua ∧ atenuante -> Explicada(ambigua)."""

  id: str
  ambigua: str
  atenuante: str

  def __str__(self) -> str:
      return f"{self.id}: {self.ambigua} ∧ {self.atenuante} → Explicada({self.ambigua})"


@dataclass
class BaseConhecimento:
  caracteristicas: dict[str, Caracteristica]
  regras_certeza: list[RegraCerteza]
  regras_anulacao: list[RegraAnulacao]
  fatores: dict[str, float]
  # Índices para consulta rápida pela inferência.
  certeza_por_id: dict[str, RegraCerteza] = field(default_factory=dict)
  anulacoes_por_ambigua: dict[str, RegraAnulacao] = field(default_factory=dict)

  def fator(self, id_caracteristica: str) -> float:
    return self.fatores[id_caracteristica]

  def log_fator(self, id_caracteristica: str) -> float:
    """log do fator: Devolve -inf para específica de humano e +inf para específica de monstro."""
    f = self.fatores[id_caracteristica]
    if f == 0:
        return -math.inf
    return math.log(f)


def fator_de(c: Caracteristica) -> float:
    """p_monstro ÷ p_humano, com ×∞ e ×0 para as específicas."""
    if c.p_humano == 0:
        return math.inf
    return c.p_monstro / c.p_humano


def montar_base(catalogo: list[Caracteristica]) -> BaseConhecimento:
    """Gera regras R, regras A e fatores a partir do catálogo, na ordem do CSV."""
    por_id = {c.id: c for c in catalogo}

    regras_certeza = [
        RegraCerteza(id=f"R{i}", premissa=c.id, conclusao=c.lado)
        for i, c in enumerate((c for c in catalogo if c.tipo == "especifica"), start=1)
    ]

    atenuante_de = {c.anula: c.id for c in catalogo if c.anula}
    regras_anulacao = [
        RegraAnulacao(id=f"A{i}", ambigua=amb.id, atenuante=atenuante_de[amb.id])
        for i, amb in enumerate(
            (c for c in catalogo if c.tipo == "ambigua" and c.id in atenuante_de), start=1
        )
    ]

    return BaseConhecimento(
        caracteristicas=por_id,
        regras_certeza=regras_certeza,
        regras_anulacao=regras_anulacao,
        fatores={c.id: fator_de(c) for c in catalogo},
        certeza_por_id={r.premissa: r for r in regras_certeza},
        anulacoes_por_ambigua={r.ambigua: r for r in regras_anulacao},
    )
