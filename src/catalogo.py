"""
Leitura e validação do catálogo de características (data/caracteristicas.csv).
Contrato: carregar_catalogo(caminho) -> list[Caracteristica]
"""

from pathlib import Path

import pandas as pd

from src.modelos import Caracteristica

CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "data" / "caracteristicas.csv"

COLUNAS = ["id", "descricao", "tipo", "lado", "p_humano", "p_monstro", "anula"]
TIPOS = {"generica", "ambigua", "especifica"}
LADOS = {"monstro", "humano", "ambos"}


class CatalogoInvalido(ValueError):
  """O CSV não segue as regras do catálogo."""


def carregar_catalogo(caminho: str | Path = CAMINHO_PADRAO) -> list[Caracteristica]:
  """Lê o CSV com pandas, valida e devolve as características na ordem do arquivo."""
  df = pd.read_csv(caminho, dtype={"id": str, "descricao": str, "anula": str})

  faltando = [c for c in COLUNAS if c not in df.columns]
  if faltando:
    raise CatalogoInvalido(f"colunas faltando no CSV: {faltando}")

  df = df[COLUNAS].copy()
  for coluna in ("id", "descricao", "tipo", "lado"):
    df[coluna] = df[coluna].str.strip()
  df["anula"] = df["anula"].str.strip()

  catalogo = [
    Caracteristica(
      id=linha.id,
      descricao=linha.descricao,
      tipo=linha.tipo,
      lado=linha.lado,
      p_humano=float(linha.p_humano),
      p_monstro=float(linha.p_monstro),
      anula=linha.anula if isinstance(linha.anula, str) and linha.anula else None,
    )
    for linha in df.itertuples(index=False)
  ]
  validar_catalogo(catalogo)
  return catalogo


def validar_catalogo(catalogo: list[Caracteristica]) -> None:
    """Confere as regras do catálogo; levanta CatalogoInvalido com todos os problemas."""
    erros: list[str] = []
    ids = [c.id for c in catalogo]
    por_id = {c.id: c for c in catalogo}

    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    if repetidos:
      erros.append(f"ids repetidos: {repetidos}")

    for c in catalogo:
      if c.tipo not in TIPOS:
        erros.append(f"{c.id}: tipo inválido '{c.tipo}'")
      if c.lado not in LADOS:
        erros.append(f"{c.id}: lado inválido '{c.lado}'")
      if c.p_humano < 0 or c.p_monstro < 0:
        erros.append(f"{c.id}: probabilidade negativa")

      if c.tipo == "especifica":
        if c.lado == "monstro" and not (c.p_humano == 0 and c.p_monstro > 0):
          erros.append(f"{c.id}: específica de monstro precisa de p_humano=0 e p_monstro>0")
        elif c.lado == "humano" and not (c.p_monstro == 0 and c.p_humano > 0):
          erros.append(f"{c.id}: específica de humano precisa de p_monstro=0 e p_humano>0")
        elif c.lado == "ambos":
          erros.append(f"{c.id}: específica precisa de um lado único")
      else:
        if c.lado != "ambos":
          erros.append(f"{c.id}: só específicas têm lado único")
        if c.p_humano <= 0 or c.p_monstro <= 0:
          erros.append(f"{c.id}: não específica precisa de p_humano>0 e p_monstro>0")

      if c.anula is not None:
        alvo = por_id.get(c.anula)
        if c.tipo != "generica":
          erros.append(f"{c.id}: só genéricas (atenuantes) podem anular")
        if alvo is None:
          erros.append(f"{c.id}: anula '{c.anula}', que não existe")
        elif alvo.tipo != "ambigua":
          erros.append(f"{c.id}: anula '{c.anula}', que não é ambígua")

    alvos = [c.anula for c in catalogo if c.anula]
    alvos_repetidos = sorted({a for a in alvos if alvos.count(a) > 1})
    if alvos_repetidos:
      erros.append(f"ambíguas anuladas por mais de uma atenuante: {alvos_repetidos}")

    # Cada coluna p_ soma 100 entre as não específicas e dentro das específicas de cada lado.
    nao_especificas = [c for c in catalogo if c.tipo != "especifica"]
    for coluna in ("p_humano", "p_monstro"):
      soma = sum(getattr(c, coluna) for c in nao_especificas)
      if abs(soma - 100) > 1e-9:
        erros.append(f"{coluna} das não específicas soma {soma:g}, deveria ser 100")

    for lado, coluna in (("monstro", "p_monstro"), ("humano", "p_humano")):
      soma = sum(getattr(c, coluna) for c in catalogo if c.tipo == "especifica" and c.lado == lado)
      if abs(soma - 100) > 1e-9:
        erros.append(f"{coluna} das específicas de {lado} soma {soma:g}, deveria ser 100")

    if erros:
      raise CatalogoInvalido("catálogo inválido:\n- " + "\n- ".join(erros))
