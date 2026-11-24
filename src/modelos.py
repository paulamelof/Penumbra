"""Tipos compartilhados entre os módulos (contrato do grupo).

Dono: Pessoa 2 (Fase 1). Esta versão segue exatamente o documento
"Regras de negócio e plano do grupo"; qualquer mudança deve ser combinada
com todos antes.
"""

from dataclasses import dataclass
from enum import Enum


class Acao(Enum):
  MATAR = "matar"
  PERMITIR = "permitir"
  ESPERAR = "esperar"


@dataclass
class Caracteristica:
  id: str
  descricao: str
  tipo: str  # generica | ambigua | especifica
  lado: str  # monstro | humano | ambos
  p_humano: float
  p_monstro: float
  anula: str | None


@dataclass
class Percepcao:
  passo: int  # 1 a 6
  distancia: int  # 6 a 1
  caracteristica: Caracteristica | None  # None = passo na névoa


@dataclass
class Resultado:
  acao: Acao
  tipo_real: str  # humano | monstro
  correta: bool
  tipo_decisao: str  # provada | garantia | forcada
  chance_monstro: float
  passos: int
  cadeia: list[str]
