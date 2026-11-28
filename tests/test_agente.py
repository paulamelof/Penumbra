import pytest

from src.agente import Agente, completar_resultado
from src.modelos import Acao, Resultado


def jogar(agente, percepcao, pistas):
    """Manda as pistas (uma por passo; None = névoa) e devolve a lista de ações."""
    acoes = []
    for passo, pista in enumerate(pistas, start=1):
        acao = agente.perceber(percepcao(passo, pista))
        acoes.append(acao)
        if acao != Acao.ESPERAR:
            break
    return acoes


E, M, P = Acao.ESPERAR, Acao.MATAR, Acao.PERMITIR


# ---------------------------------------------------------------- exemplo do PDF
def test_exemplo_nivel_1_mata_no_passo_5_por_garantia(base, percepcao):
    agente = Agente(base)
    pistas = ["cheiro_forte", "mochila", "roupa_suja", "olhos_vermelhos", "sorriso_fixo", "tossindo"]
    assert jogar(agente, percepcao, pistas) == [E, E, E, E, M]

    chances = [round(d.chance_monstro * 100) for d in agente.registro]
    assert chances == [64, 64, 23, 35, 89]
    assert agente.decisao.tipo == "garantia"
    assert agente.decisao.passo == 5


def test_exemplo_nivel_4_tambem_mata_no_passo_5(base, percepcao):
    agente = Agente(base)
    pistas = [None, None, None, "olhos_vermelhos", "sorriso_fixo", "tossindo"]
    assert jogar(agente, percepcao, pistas) == [E, E, E, E, M]

    chances = [round(d.chance_monstro * 100) for d in agente.registro]
    assert chances[3:] == [64, 96]
    assert agente.decisao.tipo == "garantia"
    # na névoa, nenhuma pista foi registrada
    assert all(d.caracteristica is None for d in agente.registro[:3])


# ---------------------------------------------------------------- decisão provada
def test_especifica_de_monstro_mata_na_hora(base, percepcao):
    agente = Agente(base)
    assert jogar(agente, percepcao, ["sem_sombra"]) == [M]
    assert agente.decisao.tipo == "provada"
    assert agente.decisao.chance_monstro == 1.0


def test_especifica_de_humano_deixa_entrar_na_hora(base, percepcao):
    agente = Agente(base)
    assert jogar(agente, percepcao, ["mochila", "pupila_reage"]) == [E, P]
    assert agente.decisao.tipo == "provada"
    assert agente.decisao.chance_monstro == 0.0


# ---------------------------------------------------------------- névoa
def test_na_nevoa_so_espera_mesmo_com_garantia_baixa(base, percepcao):
    agente = Agente(base, garantia_matar=0.4, garantia_entrar=0.4)
    for passo in (1, 2, 3):
        assert agente.perceber(percepcao(passo, None)) == Acao.ESPERAR
        assert agente.decisao.tipo is None


# ---------------------------------------------------------------- decisão forçada
def test_forcada_mata_quando_chance_passa_de_20_por_cento(base, percepcao):
    agente = Agente(base)
    # só uma atenuante (23%) e o resto neutro: 23% > 20% -> mata
    pistas = ["roupa_suja", "mochila", "idade_jovem", "idade_idosa", "genero_feminino", "genero_masculino"]
    assert jogar(agente, percepcao, pistas) == [E, E, E, E, E, M]
    assert agente.decisao.tipo == "forcada"
    assert agente.decisao.chance_monstro == pytest.approx(0.3 / 1.3)


def test_forcada_deixa_entrar_quando_chance_e_menor_que_20_por_cento(base, percepcao):
    agente = Agente(base)
    # duas atenuantes: razão 0,09 -> 8,3% de monstro (91,7% humano, abaixo dos 95%)
    pistas = ["roupa_suja", "olheiras", "mochila", "idade_jovem", "idade_idosa", "genero_feminino"]
    assert jogar(agente, percepcao, pistas) == [E, E, E, E, E, P]
    assert agente.decisao.tipo == "forcada"


def test_forcada_com_50_por_cento_mata(base, percepcao):
    agente = Agente(base)
    # só pistas neutras (×1): a chance continua 50% e o agente decide no escuro
    pistas = [None, "mochila", "idade_jovem", "idade_idosa", "genero_feminino", "genero_masculino"]
    assert jogar(agente, percepcao, pistas) == [E, E, E, E, E, M]  # na dúvida, não abre
    assert agente.decisao.tipo == "forcada"
    assert agente.decisao.chance_monstro == pytest.approx(0.5)


def test_entrada_por_garantia_exige_muitas_atenuantes(base, percepcao):
    agente = Agente(base)
    # três atenuantes: 0,3^3 = 0,027 -> 97,4% humano, passa dos 95%
    pistas = ["roupa_suja", "olheiras", "tossindo"]
    assert jogar(agente, percepcao, pistas) == [E, E, P]
    assert agente.decisao.tipo == "garantia"


# ---------------------------------------------------------------- configuração
def test_garantia_maior_faz_esperar_mais(base, percepcao):
    pistas = ["cheiro_forte", "mochila", "roupa_suja", "olhos_vermelhos", "sorriso_fixo", "sorriso_fixo"]
    # com 99% de garantia, os 89% do passo 5 não bastam
    agente = Agente(base, garantia_matar=0.99)
    acoes = jogar(agente, percepcao, pistas[:5])
    assert acoes == [E, E, E, E, E]


def test_garantia_invalida_da_erro(base):
    with pytest.raises(ValueError):
        Agente(base, garantia_matar=0)
    with pytest.raises(ValueError):
        Agente(base, garantia_entrar=1.5)


# ---------------------------------------------------------------- memória do encontro
def test_passo_1_zera_o_encontro_anterior(base, percepcao):
    agente = Agente(base)
    jogar(agente, percepcao, ["cheiro_forte", "mochila"])  # espera nos dois passos
    assert agente.fatos == ["cheiro_forte", "mochila"]

    agente.perceber(percepcao(1, "olhos_vermelhos"))  # criatura nova
    assert agente.fatos == ["olhos_vermelhos"]
    assert len(agente.registro) == 1


# ---------------------------------------------------------------- explicação e integração
def test_explicar_tem_uma_linha_por_passo_e_cita_a_anulacao(base, percepcao):
    agente = Agente(base)
    jogar(agente, percepcao, ["cheiro_forte", "mochila", "roupa_suja", "olhos_vermelhos", "sorriso_fixo"])
    linhas = agente.explicar()
    assert len(linhas) == 5
    assert "Passo 3" in linhas[2] and "roupa_suja explica cheiro_forte" in linhas[2]
    assert "MATAR (por garantia" in linhas[4]
    assert "89,0%" in linhas[4]


def test_completar_resultado_preenche_o_que_so_o_agente_sabe(base, percepcao):
    agente = Agente(base)
    jogar(agente, percepcao, ["sem_sombra"])
    do_ambiente = Resultado(acao=Acao.MATAR, tipo_real="monstro", correta=True,
                            tipo_decisao="", chance_monstro=0.0, passos=1, cadeia=[])
    completo = completar_resultado(do_ambiente, agente)
    assert completo.tipo_decisao == "provada"
    assert completo.chance_monstro == 1.0
    assert completo.cadeia == agente.explicar()
    assert completo.tipo_real == "monstro" and completo.passos == 1  # o resto continua igual
