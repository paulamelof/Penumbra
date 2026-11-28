import itertools
import math

import pytest

from src.inferencia import chance_monstro, provar

ESPECIFICAS_MONSTRO = ["sem_sombra", "dentes_afiados", "sangue_escuro", "dedos_extras"]
ESPECIFICAS_HUMANO = ["sangue_vermelho", "reflexo_visivel", "pupila_reage"]
# (atenuante, ambígua que ela explica)
ANULACOES = [
    ("roupa_suja", "cheiro_forte"),
    ("olheiras", "olhos_vermelhos"),
    ("perna_enfaixada", "anda_mancando"),
    ("roupa_molhada", "pele_palida"),
    ("tossindo", "voz_rouca"),
]


# ---------------------------------------------------------------- fatores
def test_fatores_vem_do_csv(base):
    assert base.fatores["mochila"] == pytest.approx(1.0)  # neutra
    assert base.fatores["roupa_suja"] == pytest.approx(0.3)  # atenuante
    assert base.fatores["cheiro_forte"] == pytest.approx(1.8)  # ambígua comum
    assert base.fatores["voz_rouca"] == pytest.approx(2.25)
    assert base.fatores["sorriso_fixo"] == pytest.approx(15.0)
    assert base.fatores["sem_sombra"] == math.inf
    assert base.fatores["pupila_reage"] == 0.0


# ---------------------------------------------------------------- certeza
@pytest.mark.parametrize("carac", ESPECIFICAS_MONSTRO)
def test_especifica_de_monstro_prova_monstro(carac, base):
    prova, regras = provar(["mochila", carac], base)
    assert prova == "monstro"
    assert regras
    assert chance_monstro(["mochila", carac], base).chance_monstro == 1.0


@pytest.mark.parametrize("carac", ESPECIFICAS_HUMANO)
def test_especifica_de_humano_prova_humano(carac, base):
    prova, _ = provar(["cheiro_forte", carac], base)
    assert prova == "humano"
    assert chance_monstro(["cheiro_forte", carac], base).chance_monstro == 0.0


def test_sem_especifica_nao_prova_nada(base):
    assert provar(["sorriso_fixo", "cheiro_forte", "mochila"], base) == (None, [])
    assert provar([], base) == (None, [])


def test_especificas_contraditorias_dao_erro(base):
    with pytest.raises(ValueError):
        provar(["sem_sombra", "pupila_reage"], base)


# ---------------------------------------------------------------- anulação
@pytest.mark.parametrize("atenuante,ambigua", ANULACOES)
def test_atenuante_anula_a_sua_ambigua(atenuante, ambigua, base):
    sozinha = chance_monstro([ambigua], base)
    assert sozinha.explicadas == []

    com_atenuante = chance_monstro([ambigua, atenuante], base)
    assert com_atenuante.explicadas == [ambigua]
    # a ambígua deixa de contar (×1); só a atenuante (×0,3) pesa
    assert com_atenuante.razao == pytest.approx(base.fatores[atenuante])


@pytest.mark.parametrize("atenuante,ambigua", ANULACOES)
def test_atenuante_sem_a_ambigua_so_puxa_para_humano(atenuante, ambigua, base):
    calc = chance_monstro([atenuante], base)
    assert calc.explicadas == []
    assert calc.razao == pytest.approx(0.3)


def test_atenuante_anula_so_a_ambigua_indicada(base):
    # roupa_suja explica cheiro_forte, e NÃO olhos_vermelhos
    calc = chance_monstro(["olhos_vermelhos", "roupa_suja"], base)
    assert calc.explicadas == []
    assert calc.razao == pytest.approx(1.8 * 0.3)


def test_so_anula_se_as_duas_ja_foram_vistas(base):
    # a atenuante veio ANTES da ambígua: quando a ambígua chega, a anulação passa a valer
    antes = chance_monstro(["roupa_suja"], base)
    depois = chance_monstro(["roupa_suja", "cheiro_forte"], base)
    assert antes.explicadas == []
    assert depois.explicadas == ["cheiro_forte"]


# ---------------------------------------------------------------- Bayes (exemplo do PDF)
def test_comeca_em_50_por_cento(base):
    assert chance_monstro([], base).chance_monstro == pytest.approx(0.5)


def test_exemplo_do_encontro_nivel_1(base):
    """Tabela do PDF: cheiro_forte, mochila, roupa_suja, olhos_vermelhos, sorriso_fixo."""
    esperado = [
        (["cheiro_forte"], 1.8, 0.64),
        (["cheiro_forte", "mochila"], 1.8, 0.64),
        (["cheiro_forte", "mochila", "roupa_suja"], 0.3, 0.23),
        (["cheiro_forte", "mochila", "roupa_suja", "olhos_vermelhos"], 0.54, 0.35),
        (["cheiro_forte", "mochila", "roupa_suja", "olhos_vermelhos", "sorriso_fixo"], 8.1, 0.89),
    ]
    for fatos, razao, chance in esperado:
        calc = chance_monstro(fatos, base)
        assert calc.razao == pytest.approx(razao)
        assert calc.chance_monstro == pytest.approx(chance, abs=0.005)


def test_exemplo_do_encontro_nivel_4(base):
    """Na névoa densa o agente só vê os passos 4 a 6 e nunca vê a roupa_suja."""
    c4 = chance_monstro(["olhos_vermelhos"], base)
    assert c4.razao == pytest.approx(1.8)
    assert c4.chance_monstro == pytest.approx(0.64, abs=0.005)
    c5 = chance_monstro(["olhos_vermelhos", "sorriso_fixo"], base)
    assert c5.razao == pytest.approx(27.0)
    assert c5.chance_monstro == pytest.approx(0.96, abs=0.005)


def test_raciocinio_nao_monotonico(base):
    """Uma pista nova pode DERRUBAR a chance (roupa_suja depois do cheiro_forte)."""
    antes = chance_monstro(["cheiro_forte"], base).chance_monstro
    depois = chance_monstro(["cheiro_forte", "roupa_suja"], base).chance_monstro
    assert depois < antes


# ---------------------------------------------------------------- RB05
def test_ordem_das_pistas_nao_muda_a_chance_final(base):
    pistas = ["cheiro_forte", "roupa_suja", "olhos_vermelhos", "sorriso_fixo", "mochila"]
    chances = {round(chance_monstro(list(ordem), base).chance_monstro, 12)
               for ordem in itertools.permutations(pistas)}
    assert len(chances) == 1


def test_pista_repetida_conta_uma_vez(base):
    assert chance_monstro(["cheiro_forte", "cheiro_forte"], base).razao == pytest.approx(1.8)
