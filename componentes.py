"""Tela de jogo do Penumbra: cenário, silhueta, cards das pistas e pensamento da IA.

desenhar_tela(...) monta tudo num bloco só, com cara de jogo.
"""

import html
import math

import streamlit as st

import arte

NOME_TIPO = {"generica": "genérica", "ambigua": "ambígua", "especifica": "específica"}
TOTAL_PASSOS = 6


def _num(x: float) -> str:
    return f"{x:.2f}".replace(".", ",")


def texto_fator(fator: float) -> str:
    if fator == math.inf:
        return "certeza de monstro"
    if fator == 0:
        return "certeza de humano"
    return f"×{_num(fator)}"


def _categoria(c) -> tuple[str, str]:
    """(rótulo, classe CSS) do selo do card."""
    if c.tipo == "especifica":
        return (f"prova: {c.lado}", f"pz-esp-{c.lado}")
    if c.tipo == "generica" and c.anula:
        return ("atenuante", "pz-atenuante")
    return (NOME_TIPO[c.tipo], f"pz-{c.tipo}")


# ----------------------------------------------------------------------
# Pensamento da IA
# PRÉVIA: refaz a conta do documento para a tela ter o que mostrar.
# Quando o agente existir, troque por agente.explicar() / agente.chance_monstro.
# ----------------------------------------------------------------------
def calcular_pensamento(pistas: list, base, garantia_matar: float, garantia_entrar: float) -> dict:
    linhas, vistas, chance, prova = [], [], 0.5, None
    for passo, c in enumerate(pistas, start=1):
        if c is None:
            linhas.append(dict(passo=passo, nome="névoa", conta="nada visto", chance=chance, nota=""))
            continue
        vistas.append(c.id)
        regra = next((base.certeza_por_id[i] for i in vistas if i in base.certeza_por_id), None)
        if regra:
            prova = regra.conclusao
            chance = 1.0 if prova == "monstro" else 0.0
            linhas.append(dict(passo=passo, nome=c.descricao, conta=f"regra {regra.id}: certeza", chance=chance, nota=""))
            break
        explicadas = {r.ambigua for r in base.regras_anulacao if r.ambigua in vistas and r.atenuante in vistas}
        razao = math.prod(base.fator(i) for i in vistas if i not in explicadas)
        chance = razao / (1 + razao)
        nota = ""
        if c.anula and c.anula in explicadas:
            nota = f"anula {base.caracteristicas[c.anula].descricao.lower()} (÷ {_num(base.fator(c.anula))})"
        linhas.append(dict(passo=passo, nome=c.descricao, conta=f"× {_num(base.fator(c.id))}", chance=chance, nota=nota))

    passo = len(pistas)
    if prova:
        decisao, tipo = ("matar" if prova == "monstro" else "deixar entrar"), "provada"
    elif not pistas:
        decisao, tipo = "esperar", ""
    elif chance >= garantia_matar:
        decisao, tipo = "matar", "por garantia"
    elif 1 - chance >= garantia_entrar:
        decisao, tipo = "deixar entrar", "por garantia"
    elif passo < TOTAL_PASSOS:
        decisao, tipo = "esperar", ""
    else:
        decisao, tipo = ("matar" if chance > 0.20 else "deixar entrar"), "forçada"
    return dict(linhas=linhas, chance=chance, decisao=decisao, tipo=tipo)


# ----------------------------------------------------------------------
# HTML da tela
# ----------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;700;800&family=Space+Mono:wght@400;700&display=swap');
.pz { --roxo:#2b2560; --roxo2:#3a3380; font-family:'Poppins',system-ui,sans-serif; color:#f4f2ff;
  background:#0f1016; border-radius:18px; padding:18px 18px 22px; }
.pz-topo { display:flex; justify-content:space-between; align-items:center; margin:0 4px 12px; }
.pz-nivel { font-weight:800; font-size:24px; letter-spacing:.01em; }
.pz-nivel small { font-weight:500; font-size:14px; color:#9d97c9; margin-left:10px; }
.pz-hud { display:flex; align-items:center; gap:16px; }
.pz-pontos { font:700 14px 'Space Mono',monospace; color:#f0b65a; background:#1c1a2e; padding:6px 10px; border-radius:8px; }
.pz-vidas { display:flex; gap:6px; }
.pz-coracao { width:30px; height:26px; background-size:contain; background-repeat:no-repeat; image-rendering:pixelated; }

.pz-cena { position:relative; height:270px; border-radius:26px 26px 0 0; overflow:hidden;
  background:linear-gradient(180deg,#2c2668 0%,#1a1640 45%,#07061a 100%); }
.pz-lua { position:absolute; top:22px; left:3.5%; width:62px; height:62px; border-radius:50%;
  background:radial-gradient(circle at 35% 35%,#e9e7df 0%,#bdbab0 45%,#7d7a74 100%);
  box-shadow:0 0 50px 14px rgba(200,196,230,.18); }
.pz-lua::before { content:""; position:absolute; inset:0; border-radius:50%;
  background:radial-gradient(circle at 30% 60%,#8e8b84 0 6px,transparent 7px),
             radial-gradient(circle at 62% 30%,#9a968e 0 4px,transparent 5px),
             radial-gradient(circle at 60% 70%,#8e8b84 0 5px,transparent 6px),
             radial-gradient(circle at 80% 42%,#2c2668 0 27px,transparent 28px); opacity:.9; }
.pz-paisagem { position:absolute; inset:0; background-position:center bottom; background-size:cover; background-repeat:no-repeat; }
.pz-porta { position:absolute; bottom:0; width:78px; height:150px; transform:translateX(-50%);
  background-size:contain; background-repeat:no-repeat; background-position:bottom;
  filter:drop-shadow(0 0 18px rgba(240,182,90,.25)); }
.pz-silhueta { position:absolute; bottom:0; transform:translateX(-50%); aspect-ratio:60/140;
  background-size:contain; background-repeat:no-repeat; background-position:bottom; z-index:2;
  filter:drop-shadow(0 4px 10px rgba(0,0,0,.7)); }
@keyframes pz-balanco { 0%,100% { margin-bottom:0 } 50% { margin-bottom:5px } }
.pz-nevoa { position:absolute; top:0; bottom:0; left:0; z-index:3; backdrop-filter:blur(4px);
  background:linear-gradient(90deg,rgba(170,166,205,.62) 0%,rgba(170,166,205,.45) 82%,rgba(170,166,205,0) 100%); }
.pz-nevoa span { position:absolute; bottom:14px; left:14px; font-weight:700; font-size:12px; color:#2b2560;
  background:#ffffffaa; padding:3px 8px; border-radius:99px; }
.pz-chao { height:5px; background:#f4f2ff; border-radius:3px; margin:0 -6px; }

.pz-grade { display:grid; grid-template-columns:repeat(7,1fr); gap:12px; }
.pz-num { text-align:center; font-weight:800; font-size:20px; margin:8px 0 6px; color:#f4f2ff; }
.pz-num.pz-apagado { color:#4a466b; }
.pz-card { position:relative; margin-top:12px; background:var(--roxo); border-radius:20px; padding:12px 8px 12px;
  text-align:center; min-height:132px; box-sizing:border-box; box-shadow:0 8px 20px rgba(0,0,0,.35); }
.pz-card::before { content:""; position:absolute; top:-15px; left:50%; transform:translateX(-50%);
  border:9px solid transparent; border-bottom:16px solid var(--roxo); border-top:none; }
.pz-card.pz-novo { animation:pz-surgir .55s cubic-bezier(.2,1.4,.4,1); }
@keyframes pz-surgir { from { opacity:0; transform:translateY(-18px) scale(.85) } to { opacity:1; transform:none } }
.pz-icone { width:64px; height:64px; margin:0 auto 6px; background-size:contain; background-repeat:no-repeat; background-position:center;
  filter:drop-shadow(0 3px 3px rgba(0,0,0,.35)); }
.pz-nome { font-weight:700; font-size:13px; line-height:1.2; }
.pz-selo { display:inline-block; margin-top:7px; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.05em;
  padding:2px 8px; border-radius:99px; background:#ffffff1a; color:#d7d3f5; }
.pz-ambigua { background:#e0a52633; color:#ffcf6b; }
.pz-atenuante { background:#5b8def33; color:#9fbcff; }
.pz-esp-monstro { background:#e5393540; color:#ff8a85; }
.pz-esp-humano { background:#3fae6a40; color:#86e3a8; }
.pz-card.pz-prova-monstro { box-shadow:0 0 0 3px #e53935, 0 0 24px rgba(229,57,53,.55); }
.pz-card.pz-prova-humano { box-shadow:0 0 0 3px #3fae6a, 0 0 24px rgba(63,174,106,.5); }
.pz-card.pz-explicada .pz-icone, .pz-card.pz-explicada .pz-nome { opacity:.35; }
.pz-carimbo { position:absolute; top:40px; left:50%; transform:translateX(-50%) rotate(-12deg); white-space:nowrap;
  font-weight:800; font-size:11px; letter-spacing:.06em; color:#9fbcff; border:2px solid #9fbcff; padding:2px 7px; border-radius:6px;
  background:#1b1840cc; }
.pz-card.pz-card-nevoa { background:#3a3760; }
.pz-card.pz-card-nevoa::before { border-bottom-color:#3a3760; }

.pz-mente { position:relative; margin-top:26px; background:#16142c; border:2px solid #3a3380; border-radius:22px; padding:16px 18px; }
.pz-mente::before, .pz-mente::after { content:""; position:absolute; border-radius:50%; background:#16142c; border:2px solid #3a3380; }
.pz-mente::before { width:14px; height:14px; top:-20px; left:46px; }
.pz-mente::after { width:8px; height:8px; top:-34px; left:38px; }
.pz-mente h4 { margin:0 0 10px; font-size:14px; font-weight:800; letter-spacing:.04em; text-transform:uppercase; color:#b7b0ff; }
.pz-conta { width:100%; border-collapse:collapse; font:13px/1.5 'Space Mono',monospace; }
.pz-conta td { padding:3px 8px 3px 0; border-bottom:1px dashed #2c2a4d; color:#d9d6f3; }
.pz-conta td.pz-direita { text-align:right; font-weight:700; color:#fff; }
.pz-conta .pz-nota { color:#9fbcff; font-size:12px; }
.pz-barra { position:relative; height:16px; margin:18px 0 8px; border-radius:99px;
  background:linear-gradient(90deg,#3fae6a 0%,#3fae6a var(--entra),#4a466b var(--entra),#4a466b var(--mata),#e53935 var(--mata),#e53935 100%); }
.pz-agulha { position:absolute; top:-6px; width:6px; height:28px; border-radius:3px; background:#fff; transform:translateX(-50%);
  box-shadow:0 0 10px rgba(255,255,255,.7); transition:left .6s ease; }
.pz-legenda { display:flex; justify-content:space-between; font-size:11px; color:#9d97c9; }
.pz-decisao { margin-top:14px; display:flex; align-items:center; gap:12px; font-size:15px; }
.pz-decisao b { font-weight:800; font-size:18px; padding:4px 14px; border-radius:10px; }
.pz-d-esperar { background:#4a466b; }
.pz-d-matar { background:#e53935; }
.pz-d-entrar { background:#3fae6a; }
</style>
"""


def html_tela(partida: dict, pistas: list, passos_na_nevoa: int, base,
              garantia_matar: float = 0.80, garantia_entrar: float = 0.95,
              criaturas_por_nivel: int = 3, vidas_iniciais: int = 3) -> str:
    colunas = TOTAL_PASSOS + 1
    centro = lambda passo: (passo - 0.5) / colunas * 100
    passo_atual = len(pistas)
    mente = calcular_pensamento(pistas, base, garantia_matar, garantia_entrar)

    # topo: nível, pontos e corações
    coracoes = "".join(
        f'<div class="pz-coracao" style="background-image:url({arte.CORACAO_CHEIO if i < partida["vidas"] else arte.CORACAO_VAZIO})"></div>'
        for i in range(vidas_iniciais)
    )
    topo = (f'<div class="pz-topo"><div class="pz-nivel">Nível {partida["nivel"]}'
            f'<small>criatura {partida["criatura"]} de {criaturas_por_nivel}</small></div>'
            f'<div class="pz-hud"><span class="pz-pontos">{partida["pontos"]} pts</span>'
            f'<div class="pz-vidas">{coracoes}</div></div></div>')

    # silhueta andando
    silhueta = ""
    if passo_atual:
        de, ate = centro(max(passo_atual - 1, 0.2)), centro(passo_atual)
        altura = 96 + passo_atual * 14
        neblina = "opacity:.5;filter:blur(3px);" if passo_atual <= passos_na_nevoa else ""
        silhueta = (
            f'<style>@keyframes pz-andar-{passo_atual} {{ from {{ left:{de:.2f}% }} to {{ left:{ate:.2f}% }} }}</style>'
            f'<div class="pz-silhueta" style="left:{ate:.2f}%;height:{altura}px;background-image:url({arte.SILHUETA});{neblina}'
            f'animation:pz-andar-{passo_atual} 1s ease-out, pz-balanco .5s ease-in-out 2;"></div>'
        )
    nevoa = ""
    if passos_na_nevoa:
        nevoa = f'<div class="pz-nevoa" style="width:{passos_na_nevoa / colunas * 100:.2f}%"><span>névoa</span></div>'

    cena = (f'<div class="pz-cena"><div class="pz-lua"></div>'
            f'<div class="pz-paisagem" style="background-image:url({arte.CENARIO})"></div>'
            f'<div class="pz-porta" style="left:{centro(colunas):.2f}%;background-image:url({arte.PORTA})"></div>'
            f'{silhueta}{nevoa}</div><div class="pz-chao"></div>')

    # números dos passos e cards
    numeros = "".join(
        f'<div class="pz-num{"" if p <= passo_atual else " pz-apagado"}">{p}</div>' for p in range(1, TOTAL_PASSOS + 1)
    ) + '<div class="pz-num"></div>'

    vistas = {c.id for c in pistas if c}
    explicada_por = {
        r.ambigua: base.caracteristicas[r.atenuante].descricao
        for r in base.regras_anulacao if r.ambigua in vistas and r.atenuante in vistas
    }
    cards = []
    for passo in range(1, TOTAL_PASSOS + 1):
        if passo > passo_atual:
            cards.append("<div></div>")
            continue
        c = pistas[passo - 1]
        novo = " pz-novo" if passo == passo_atual else ""
        if c is None:
            cards.append(f'<div class="pz-card pz-card-nevoa{novo}"><div class="pz-icone" style="background-image:url({arte.icone(None)})"></div>'
                         f'<div class="pz-nome">Névoa</div><span class="pz-selo">nada visto</span></div>')
            continue
        rotulo, classe = _categoria(c)
        extra = ""
        if c.tipo == "especifica":
            extra += f" pz-prova-{c.lado}"
        carimbo = ""
        if c.id in explicada_por:
            extra += " pz-explicada"
            carimbo = '<div class="pz-carimbo">EXPLICADA</div>'
        cards.append(
            f'<div class="pz-card{novo}{extra}" title="{html.escape(texto_fator(base.fator(c.id)))}">'
            f'<div class="pz-icone" style="background-image:url({arte.icone(c.id)})"></div>{carimbo}'
            f'<div class="pz-nome">{html.escape(c.descricao)}</div>'
            f'<span class="pz-selo {classe}">{rotulo}</span></div>'
        )
    cards.append("<div></div>")

    # pensamento da IA
    linhas = ['<tr><td>início</td><td>chance 1 : 1</td><td class="pz-direita">50%</td></tr>']
    for l in mente["linhas"]:
        nota = f'<div class="pz-nota">{html.escape(l["nota"])}</div>' if l["nota"] else ""
        linhas.append(f'<tr><td>passo {l["passo"]} · {html.escape(l["nome"].lower())}{nota}</td>'
                      f'<td>{html.escape(l["conta"])}</td><td class="pz-direita">{l["chance"]:.0%}</td></tr>')
    entra, mata = (1 - garantia_entrar) * 100, garantia_matar * 100
    classe_dec = {"esperar": "pz-d-esperar", "matar": "pz-d-matar", "deixar entrar": "pz-d-entrar"}[mente["decisao"]]
    tipo = f' <span style="color:#9d97c9">({mente["tipo"]})</span>' if mente["tipo"] else ""
    pensamento = (
        f'<div class="pz-mente"><h4>Pensamento da IA</h4><table class="pz-conta">{"".join(linhas)}</table>'
        f'<div class="pz-barra" style="--entra:{entra:.1f}%;--mata:{mata:.1f}%">'
        f'<div class="pz-agulha" style="left:{mente["chance"] * 100:.1f}%"></div></div>'
        f'<div class="pz-legenda"><span>humano · deixa entrar ≤ {entra:.0f}%</span>'
        f'<span>chance de monstro: <b style="color:#fff">{mente["chance"]:.0%}</b></span>'
        f'<span>mata ≥ {mata:.0f}% · monstro</span></div>'
        f'<div class="pz-decisao">Decisão: <b class="{classe_dec}">{mente["decisao"].upper()}</b>{tipo}</div></div>'
    )

    return (f'{CSS}<div class="pz">{topo}{cena}'
            f'<div class="pz-grade">{numeros}</div><div class="pz-grade">{"".join(cards)}</div>'
            f'{pensamento}</div>')


def desenhar_tela(*args, **kwargs) -> dict:
    """Desenha a tela de jogo e devolve o pensamento calculado (chance e decisão)."""
    st.html(html_tela(*args, **kwargs))
    pistas, base = args[1], args[3]
    gm = kwargs.get("garantia_matar", 0.80)
    ge = kwargs.get("garantia_entrar", 0.95)
    return calcular_pensamento(pistas, base, gm, ge)
