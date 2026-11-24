"""Testes da Pessoa 1: catálogo e base de conhecimento."""

import math

import pytest

from src.base_conhecimento import HUMANO, MONSTRO, montar_base
from src.catalogo import CatalogoInvalido, carregar_catalogo, validar_catalogo
from src.modelos import Caracteristica


@pytest.fixture(scope="module")
def catalogo():
  return carregar_catalogo()


@pytest.fixture(scope="module")
def base(catalogo):
  return montar_base(catalogo)


# --- catálogo -------------------------------------------------------------

def test_catalogo_tem_23_caracteristicas_com_a_composicao_do_documento(catalogo):
  assert len(catalogo) == 23
  neutras = [c for c in catalogo if c.tipo == "generica" and c.anula is None]
  atenuantes = [c for c in catalogo if c.tipo == "generica" and c.anula]
  ambiguas = [c for c in catalogo if c.tipo == "ambigua"]
  esp_monstro = [c for c in catalogo if c.tipo == "especifica" and c.lado == MONSTRO]
  esp_humano = [c for c in catalogo if c.tipo == "especifica" and c.lado == HUMANO]
  assert (len(neutras), len(atenuantes), len(ambiguas)) == (5, 5, 6)
  assert (len(esp_monstro), len(esp_humano)) == (4, 3)


@pytest.mark.parametrize("coluna", ["p_humano", "p_monstro"])
def test_colunas_p_somam_100_entre_nao_especificas(catalogo, coluna):
  assert sum(getattr(c, coluna) for c in catalogo if c.tipo != "especifica") == pytest.approx(100)


@pytest.mark.parametrize("lado,coluna", [(MONSTRO, "p_monstro"), (HUMANO, "p_humano")])
def test_colunas_p_somam_100_dentro_das_especificas_do_lado(catalogo, lado, coluna):
  soma = sum(getattr(c, coluna) for c in catalogo if c.tipo == "especifica" and c.lado == lado)
  assert soma == pytest.approx(100)


def test_anula_vazio_vira_none(catalogo):
  por_id = {c.id: c for c in catalogo}
  assert por_id["mochila"].anula is None
  assert por_id["roupa_suja"].anula == "cheiro_forte"


def _copia(catalogo, **mudancas_por_id):
  novo = []
  for c in catalogo:
    dados = dict(vars(c))
    dados.update(mudancas_por_id.get(c.id, {}))
    novo.append(Caracteristica(**dados))
  return novo


@pytest.mark.parametrize(
  "mudancas",
  [
    {"mochila": {"p_humano": 6}},  # soma deixa de dar 100
    {"sem_sombra": {"p_humano": 1}},  # específica de monstro aparecendo em humano
    {"roupa_suja": {"anula": "nao_existe"}},  # atenuante aponta para o nada
    {"roupa_suja": {"anula": "mochila"}},  # atenuante aponta para não ambígua
    {"olheiras": {"anula": "cheiro_forte"}},  # duas atenuantes para a mesma ambígua
    {"mochila": {"tipo": "neutra"}},  # tipo inválido
  ],
)
def test_validacao_recusa_catalogo_quebrado(catalogo, mudancas):
  with pytest.raises(CatalogoInvalido):
      validar_catalogo(_copia(catalogo, **mudancas))


# --- regras de certeza ----------------------------------------------------

def test_cada_especifica_prova_o_lado_certo(catalogo, base):
  especificas = [c for c in catalogo if c.tipo == "especifica"]
  assert len(base.regras_certeza) == len(especificas)
  for c in especificas:
    regra = base.certeza_por_id[c.id]
    assert regra.conclusao == c.lado
  assert {r.premissa for r in base.regras_certeza if r.conclusao == MONSTRO} == {
    "sem_sombra", "dentes_afiados", "sangue_escuro", "dedos_extras"
  }
  assert {r.premissa for r in base.regras_certeza if r.conclusao == HUMANO} == {
    "sangue_vermelho", "reflexo_visivel", "pupila_reage"
  }


def test_so_especificas_geram_certeza(base):
  for regra in base.regras_certeza:
    assert base.caracteristicas[regra.premissa].tipo == "especifica"


# --- regras de anulação ---------------------------------------------------

def test_cada_atenuante_anula_so_a_sua_ambigua(catalogo, base):
  esperado = {
    "cheiro_forte": "roupa_suja",
    "olhos_vermelhos": "olheiras",
    "anda_mancando": "perna_enfaixada",
    "pele_palida": "roupa_molhada",
    "voz_rouca": "tossindo",
  }
  assert {r.ambigua: r.atenuante for r in base.regras_anulacao} == esperado
  for c in catalogo:
    if c.anula:
      regras_da_atenuante = [r for r in base.regras_anulacao if r.atenuante == c.id]
      assert [r.ambigua for r in regras_da_atenuante] == [c.anula]


def test_sorriso_fixo_nunca_e_explicado(base):
  assert "sorriso_fixo" not in base.anulacoes_por_ambigua


# --- fatores --------------------------------------------------------------

@pytest.mark.parametrize(
  "id_,fator",
  [
    ("mochila", 1.0),
    ("roupa_suja", 0.3),
    ("cheiro_forte", 1.8),
    ("voz_rouca", 2.25),
    ("sorriso_fixo", 15.0),
  ],
)
def test_fatores_da_tabela(base, id_, fator):
  assert base.fator(id_) == pytest.approx(fator)


def test_fatores_das_especificas(base):
  assert base.fator("sem_sombra") == math.inf
  assert base.fator("pupila_reage") == 0
  assert base.log_fator("sem_sombra") == math.inf
  assert base.log_fator("pupila_reage") == -math.inf


def test_exemplo_do_documento_com_os_fatores_da_base(base):
  """Nível 1: cheiro_forte, mochila, roupa_suja (anula), olhos_vermelhos, sorriso_fixo."""
  razao = 1.0
  chances = []
  vistos = []
  for pista in ["cheiro_forte", "mochila", "roupa_suja", "olhos_vermelhos", "sorriso_fixo"]:
    vistos.append(pista)
    explicadas = {
      r.ambigua for r in base.regras_anulacao
      if r.ambigua in vistos and r.atenuante in vistos
    }
    razao = math.prod(base.fator(p) for p in vistos if p not in explicadas)
    chances.append(round(100 * razao / (1 + razao)))
  assert chances == [64, 64, 23, 35, 89]