"""Regras da partida (placar, vidas, níveis, vitória e derrota).

Funções puras: recebem e devolvem dicionários, sem Streamlit.
Assim dá para testar com pytest e a interface só desenha o resultado.
"""

CRIATURAS_POR_NIVEL = 3
TOTAL_NIVEIS = 4
VIDAS_INICIAIS = 3
PONTOS_ACERTO = 10            # menos 1 por passo usado
PONTOS_HUMANO_MORTO = -5
PONTOS_MONSTRO_ADMITIDO = -20


def nova_partida(nivel_inicial: int = 1) -> dict:
    return {
        "nivel": nivel_inicial,
        "criatura": 1,
        "vidas": VIDAS_INICIAIS,
        "sobreviventes": 0,
        "monstros_abatidos": 0,
        "pontos": 0,
        "historico": [],
        "status": "encontro", 
        "mensagem": None,
    }


def registrar_decisao(partida: dict, acao: str, tipo_real: str, passo: int) -> dict:
    """acao: "matar" ou "permitir"; tipo_real: "humano" ou "monstro"."""
    p = dict(partida, historico=list(partida["historico"]))
    acertou = (acao == "matar") == (tipo_real == "monstro")

    if acao == "matar" and tipo_real == "monstro":
        p["monstros_abatidos"] += 1
        p["pontos"] += PONTOS_ACERTO - passo
        p["mensagem"] = f"Monstro abatido no passo {passo}."
    elif acao == "permitir" and tipo_real == "humano":
        p["sobreviventes"] += 1
        p["pontos"] += PONTOS_ACERTO - passo
        p["mensagem"] = "Sobrevivente entrou no abrigo."
    elif acao == "matar" and tipo_real == "humano":
        p["vidas"] -= 1
        p["pontos"] += PONTOS_HUMANO_MORTO
        p["mensagem"] = f"Era um humano. Restam {p['vidas']} vidas."
    else:
        p["pontos"] += PONTOS_MONSTRO_ADMITIDO
        p["mensagem"] = "Era um monstro. O abrigo foi invadido."

    p["historico"].append({
        "nivel": p["nivel"], "criatura": p["criatura"], "acao": acao,
        "tipo_real": tipo_real, "passo": passo, "acertou": acertou,
    })

    if acao == "permitir" and tipo_real == "monstro":
        p["status"] = "derrota_invadido"
    elif p["vidas"] <= 0:
        p["status"] = "derrota_confianca"
    elif p["criatura"] >= CRIATURAS_POR_NIVEL:
        p["status"] = "vitoria" if p["nivel"] >= TOTAL_NIVEIS else "nivel_concluido"
    else:
        p["status"] = "decidido"
    return p


def proxima_criatura(partida: dict) -> dict:
    return dict(partida, criatura=partida["criatura"] + 1, status="encontro", mensagem=None)


def proximo_nivel(partida: dict) -> dict:
    return dict(partida, nivel=partida["nivel"] + 1, criatura=1, status="encontro", mensagem=None)