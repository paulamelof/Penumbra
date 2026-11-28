"""Regras da partida."""

from src.partida import nova_partida, proxima_criatura, registrar_decisao


def test_matar_monstro_soma_pontos():
    p = registrar_decisao(nova_partida(), "matar", "monstro", passo=3)
    assert p["monstros_abatidos"] == 1
    assert p["pontos"] == 7
    assert p["status"] == "decidido"


def test_monstro_admitido_acaba_o_jogo():
    p = registrar_decisao(nova_partida(), "permitir", "monstro", passo=6)
    assert p["status"] == "derrota_invadido"


def test_terceiro_humano_morto_acaba_o_jogo():
    p = nova_partida()
    p = proxima_criatura(registrar_decisao(p, "matar", "humano", 2))
    p = proxima_criatura(registrar_decisao(p, "matar", "humano", 2))
    p = registrar_decisao(p, "matar", "humano", 2)
    assert p["vidas"] == 0
    assert p["status"] == "derrota_confianca"


def test_terceira_criatura_conclui_o_nivel():
    p = nova_partida()
    p = registrar_decisao(p, "permitir", "humano", 4)
    p = proxima_criatura(p)
    p = registrar_decisao(p, "permitir", "humano", 4)
    p = proxima_criatura(p)
    p = registrar_decisao(p, "matar", "monstro", 4)
    assert p["status"] == "nivel_concluido"


def test_ultimo_nivel_da_vitoria():
    p = nova_partida(nivel_inicial=4)
    p = proxima_criatura(registrar_decisao(p, "matar", "monstro", 2))
    p = proxima_criatura(registrar_decisao(p, "matar", "monstro", 2))
    p = registrar_decisao(p, "matar", "monstro", 2)
    assert p["status"] == "vitoria"