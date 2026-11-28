"""Desenhos do Penumbra (todos feitos à mão, em SVG).

O st.html do Streamlit apaga tags <svg> por segurança, então cada desenho vira
uma imagem "data:" e entra como background-image no CSS.
"""

import base64

TRACO = "#141218"


def data_uri(svg: str, viewbox: str = "0 0 64 64") -> str:
    completo = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">{svg}</svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(completo.encode()).decode()


# ----------------------------------------------------------------------
# Peças reutilizadas
# ----------------------------------------------------------------------
def _olho(iris="#6b4423", pupila=6.5, esclera="#f6f1ea", veias=False, olheira=False, luz=False):
    p = []
    if luz:
        p.append('<path d="M2 6 L22 22 M32 2 L32 14 M62 6 L42 22" stroke="#ffd54f" stroke-width="3" stroke-linecap="round"/>')
    p.append(f'<path d="M5 34 Q32 10 59 34 Q32 58 5 34 Z" fill="{esclera}" stroke="{TRACO}" stroke-width="3"/>')
    if veias:
        p.append('<path d="M9 33 Q15 30 19 34 M10 36 Q16 40 20 37 M55 33 Q49 29 45 34 M54 37 Q48 41 44 37" '
                 'stroke="#d32f2f" stroke-width="1.6" fill="none"/>')
    p.append(f'<circle cx="32" cy="34" r="12" fill="{iris}" stroke="{TRACO}" stroke-width="1.5"/>')
    p.append(f'<circle cx="32" cy="34" r="{pupila}" fill="#0d0d0d"/>')
    p.append('<circle cx="27.5" cy="29.5" r="3.2" fill="#fff" opacity=".85"/>')
    p.append(f'<path d="M5 34 Q32 6 59 34" stroke="{TRACO}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    if olheira:
        p.append('<path d="M10 44 Q32 62 54 44" stroke="#5b3d78" stroke-width="6" fill="none" opacity=".75" stroke-linecap="round"/>')
    return "".join(p)


def _rosto(pele="#e8b894", cabelo=None, extra="", olhos=True, boca=True):
    p = []
    if cabelo == "longo":
        p.append('<path d="M14 30 Q12 6 32 6 Q52 6 50 30 L52 56 L12 56 Z" fill="#5b3a29"/>')
    p.append(f'<circle cx="32" cy="32" r="19" fill="{pele}" stroke="{TRACO}" stroke-width="2.5"/>')
    if cabelo == "curto":
        p.append('<path d="M13 28 Q14 10 32 10 Q50 10 51 28 Q44 18 32 19 Q20 18 13 28 Z" fill="#3b2a20"/>')
    if cabelo == "longo":
        p.append('<path d="M13 30 Q16 11 32 11 Q48 11 51 30 Q46 19 32 20 Q18 19 13 30 Z" fill="#5b3a29"/>')
    if cabelo == "branco":
        p.append('<path d="M13 28 Q14 10 32 10 Q50 10 51 28 Q44 18 32 19 Q20 18 13 28 Z" fill="#e7e7ea" stroke="#9e9ea6"/>')
    if olhos:
        p.append(f'<circle cx="25" cy="31" r="2.4" fill="{TRACO}"/><circle cx="39" cy="31" r="2.4" fill="{TRACO}"/>')
    if boca:
        p.append(f'<path d="M26 41 Q32 45 38 41" stroke="{TRACO}" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    p.append(extra)
    return "".join(p)


def _camisa(cor, extra=""):
    return (f'<path d="M20 10 L12 14 L4 26 L13 31 L17 25 L17 56 L47 56 L47 25 L51 31 L60 26 L52 14 L44 10 '
            f'Q32 18 20 10 Z" fill="{cor}" stroke="{TRACO}" stroke-width="2.5" stroke-linejoin="round"/>{extra}')


def _gota(cor, brilho="#ffffff55"):
    return (f'<path d="M32 6 Q50 30 48 42 Q46 58 32 58 Q18 58 16 42 Q14 30 32 6 Z" fill="{cor}" '
            f'stroke="{TRACO}" stroke-width="2.5"/><path d="M24 40 Q24 32 29 26" stroke="{brilho}" '
            f'stroke-width="3.5" fill="none" stroke-linecap="round"/>')


# ----------------------------------------------------------------------
# Um desenho por característica (mesmos ids do CSV)
# ----------------------------------------------------------------------
_ICONES = {
    "genero_feminino": _rosto(cabelo="longo"),
    "genero_masculino": _rosto(cabelo="curto"),
    "idade_jovem": _rosto(cabelo="curto", extra='<path d="M22 40 Q32 49 42 40" stroke="#141218" stroke-width="2.2" fill="none"/>'),
    "idade_idosa": _rosto(cabelo="branco", extra=(
        '<circle cx="25" cy="31" r="5" fill="none" stroke="#141218" stroke-width="1.8"/>'
        '<circle cx="39" cy="31" r="5" fill="none" stroke="#141218" stroke-width="1.8"/>'
        '<path d="M30 31 L34 31 M16 37 Q19 39 21 37 M43 37 Q45 39 48 37" stroke="#141218" stroke-width="1.5" fill="none"/>')),
    "mochila": (
        '<path d="M22 14 Q22 6 32 6 Q42 6 42 14" stroke="#141218" stroke-width="3" fill="none"/>'
        '<rect x="12" y="14" width="40" height="44" rx="10" fill="#6d7b3a" stroke="#141218" stroke-width="2.5"/>'
        '<path d="M12 28 Q32 36 52 28" fill="#56622c" stroke="#141218" stroke-width="2.5"/>'
        '<rect x="20" y="38" width="24" height="14" rx="4" fill="#56622c" stroke="#141218" stroke-width="2"/>'
        '<rect x="29" y="29" width="6" height="6" rx="1" fill="#c9a227"/>'),
    "roupa_suja": _camisa("#8aa0b8", '<circle cx="26" cy="30" r="5" fill="#6b4a2b" opacity=".85"/>'
                          '<circle cx="39" cy="44" r="6.5" fill="#6b4a2b" opacity=".85"/><circle cx="23" cy="47" r="3" fill="#6b4a2b" opacity=".85"/>'),
    "olheiras": _olho(olheira=True),
    "perna_enfaixada": (
        '<path d="M24 4 L40 4 L42 46 Q50 50 54 56 L54 60 L24 60 L24 4 Z" fill="#e8b894" stroke="#141218" stroke-width="2.5"/>'
        '<path d="M23 16 L41 22 M23 23 L41 29 M23 30 L42 36 M23 37 L42 43" stroke="#f5f5f5" stroke-width="5"/>'
        '<path d="M23 16 L41 22 M23 23 L41 29 M23 30 L42 36 M23 37 L42 43" stroke="#c9c9c9" stroke-width="1" />'
        '<circle cx="33" cy="30" r="2.5" fill="#d32f2f"/>'),
    "roupa_molhada": _camisa("#4f7fbf", '<path d="M27 26 Q31 32 27 36 Q23 32 27 26 Z M40 36 Q44 42 40 46 Q36 42 40 36 Z '
                             'M25 44 Q28 49 25 52 Q22 49 25 44 Z" fill="#bfe3ff" stroke="#141218" stroke-width="1.2"/>'),
    "tossindo": _rosto(boca=False, extra=(
        '<ellipse cx="34" cy="42" rx="4" ry="3" fill="#141218"/>'
        '<circle cx="52" cy="40" r="5" fill="#d9dde3" stroke="#141218" stroke-width="1.5"/>'
        '<circle cx="58" cy="32" r="4" fill="#d9dde3" stroke="#141218" stroke-width="1.5"/>'
        '<circle cx="58" cy="48" r="3.5" fill="#d9dde3" stroke="#141218" stroke-width="1.5"/>')),
    "olhos_vermelhos": _olho(esclera="#f7d6d6", veias=True, iris="#7a3b2a"),
    "cheiro_forte": (
        '<path d="M14 54 Q8 44 16 36 Q24 28 16 18 Q12 12 16 6" stroke="#7cb342" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
        '<path d="M32 56 Q26 46 34 38 Q42 30 34 20 Q30 14 34 8" stroke="#9ccc65" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
        '<path d="M50 54 Q44 44 52 36 Q60 28 52 18 Q48 12 52 6" stroke="#7cb342" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
        '<circle cx="24" cy="12" r="2" fill="#141218"/><circle cx="44" cy="26" r="2" fill="#141218"/>'),
    "pele_palida": _rosto(pele="#eef0f4", extra='<path d="M20 36 Q24 38 28 36 M36 36 Q40 38 44 36" stroke="#a9b4c6" stroke-width="2" fill="none"/>'),
    "anda_mancando": (
        '<path d="M18 50 Q12 50 12 42 Q12 32 18 30 Q24 30 24 40 Q24 50 18 50 Z" fill="#8d6e63" stroke="#141218" stroke-width="2"/>'
        '<circle cx="14" cy="25" r="2.5" fill="#8d6e63"/><circle cx="19" cy="23" r="2.5" fill="#8d6e63"/><circle cx="24" cy="25" r="2.5" fill="#8d6e63"/>'
        '<path d="M34 18 Q48 22 54 14" stroke="#8d6e63" stroke-width="5" fill="none" stroke-linecap="round" stroke-dasharray="3 5"/>'
        '<path d="M46 30 Q40 30 40 22 Q40 14 46 12 Q52 12 52 22 Q52 30 46 30 Z" fill="#8d6e63" stroke="#141218" stroke-width="2" transform="rotate(20 46 22)"/>'),
    "voz_rouca": (
        '<path d="M8 30 Q20 18 32 30 Q20 42 8 30 Z" fill="#c0504d" stroke="#141218" stroke-width="2.5"/>'
        '<path d="M14 30 L26 30" stroke="#5a1f1d" stroke-width="3"/>'
        '<path d="M38 18 L42 24 L38 30 L42 36 L38 42 M46 12 L51 20 L46 28 L51 36 L46 44 M54 8 L59 18 L54 30 L59 40 L54 50" '
        'stroke="#b39ddb" stroke-width="3" fill="none" stroke-linejoin="round"/>'),
    "sorriso_fixo": _rosto(pele="#cfd2d6", olhos=False, boca=False, extra=(
        '<circle cx="24" cy="28" r="4" fill="#fff" stroke="#141218" stroke-width="1.5"/><circle cx="24" cy="28" r="1.5" fill="#141218"/>'
        '<circle cx="40" cy="28" r="4" fill="#fff" stroke="#141218" stroke-width="1.5"/><circle cx="40" cy="28" r="1.5" fill="#141218"/>'
        '<path d="M15 36 Q32 54 49 36 Q32 44 15 36 Z" fill="#fff" stroke="#141218" stroke-width="2"/>'
        '<path d="M20 39 L21 44 M25 41 L25 47 M30 42 L30 48 M35 42 L35 48 M40 41 L40 47 M44 39 L43 44" stroke="#141218" stroke-width="1.3"/>')),
    "sem_sombra": (
        '<circle cx="32" cy="12" r="6" fill="#2a2830"/>'
        '<path d="M24 20 L40 20 L42 40 L38 40 L37 56 L33 56 L32 44 L31 56 L27 56 L26 40 L22 40 Z" fill="#2a2830"/>'
        '<ellipse cx="32" cy="58" rx="20" ry="4" fill="none" stroke="#e53935" stroke-width="2" stroke-dasharray="4 3"/>'
        '<path d="M12 50 L52 62" stroke="#e53935" stroke-width="2.5"/>'),
    "dentes_afiados": (
        '<path d="M6 22 Q32 6 58 22 L58 44 Q32 60 6 44 Z" fill="#5a1414" stroke="#141218" stroke-width="2.5"/>'
        '<path d="M8 23 L14 36 L19 21 L25 37 L30 18 L35 37 L40 18 L45 36 L50 21 L56 34 L57 23 Q32 9 8 23 Z" fill="#f3efe2" stroke="#141218" stroke-width="1.5"/>'
        '<path d="M8 43 L15 33 L21 45 L28 33 L33 47 L39 33 L45 45 L51 33 L57 43 Q32 57 8 43 Z" fill="#f3efe2" stroke="#141218" stroke-width="1.5"/>'),
    "sangue_escuro": _gota("#2a0d16", "#ffffff33"),
    "dedos_extras": (
        '<path d="M16 60 L14 34 Q14 30 18 30 L18 14 Q18 10 22 10 Q25 10 25 14 L26 28 L27 8 Q27 4 31 4 Q35 4 35 8 L35 28 '
        'L37 10 Q37 6 41 6 Q44 6 44 10 L43 30 L46 16 Q47 12 50 13 Q53 14 52 18 L49 34 L54 26 Q56 23 59 25 Q61 28 58 31 '
        'L50 44 Q46 58 40 60 Z" fill="#9fb88a" stroke="#141218" stroke-width="2.5" stroke-linejoin="round"/>'
        '<path d="M14 40 L7 28 Q5 24 9 23 Q12 22 14 26 L18 34" fill="#9fb88a" stroke="#141218" stroke-width="2.5"/>'),
    "sangue_vermelho": _gota("#d32f2f"),
    "reflexo_visivel": (
        '<ellipse cx="32" cy="32" rx="22" ry="28" fill="#2d3e57" stroke="#8d6e63" stroke-width="5"/>'
        '<circle cx="32" cy="24" r="7" fill="#e8b894"/><path d="M20 50 Q22 34 32 33 Q42 34 44 50 Z" fill="#4f7fbf"/>'
        '<path d="M18 18 L26 10 M16 26 L30 12" stroke="#ffffff88" stroke-width="2.5" stroke-linecap="round"/>'),
    "pupila_reage": _olho(pupila=2.5, iris="#4f7fbf", luz=True),
}

NEVOA_ICONE = (
    '<path d="M6 22 Q20 14 32 22 T58 22 M4 34 Q18 26 32 34 T60 34 M6 46 Q20 38 32 46 T58 46" '
    'stroke="#c9cbe0" stroke-width="4" fill="none" stroke-linecap="round" opacity=".8"/>'
    '<text x="32" y="44" font-size="30" font-family="sans-serif" font-weight="800" text-anchor="middle" fill="#ffffff">?</text>'
)


def icone(id_caracteristica: str | None) -> str:
    if id_caracteristica is None:
        return data_uri(NEVOA_ICONE)
    return data_uri(_ICONES.get(id_caracteristica, NEVOA_ICONE))


# ----------------------------------------------------------------------
# Cenário, porta, silhueta e corações
# ----------------------------------------------------------------------
_CENARIO = (
    # cidade em ruínas ao fundo
    '<g fill="#221c4a">'
    '<path d="M0 200 L0 120 L40 120 L40 96 L70 96 L78 110 L90 104 L90 200 Z"/>'
    '<path d="M150 200 L150 84 L176 84 L184 70 L196 84 L210 84 L210 200 Z"/>'
    '<path d="M300 200 L300 112 L330 112 L340 100 L352 118 L370 118 L370 200 Z"/>'
    '<path d="M560 200 L560 76 L590 76 L590 60 L604 76 L626 70 L626 200 Z"/>'
    '<path d="M760 200 L760 108 L800 108 L812 92 L826 108 L846 108 L846 200 Z"/>'
    '<path d="M980 200 L980 96 L1006 96 L1016 82 L1030 104 L1040 104 L1040 200 Z"/>'
    '</g>'
    '<g fill="#2f2862"><rect x="158" y="96" width="6" height="8"/><rect x="190" y="120" width="6" height="8"/>'
    '<rect x="572" y="92" width="6" height="8"/><rect x="606" y="130" width="6" height="8"/><rect x="774" y="126" width="6" height="8"/></g>'
    # árvores secas
    '<g stroke="#08060f" stroke-linecap="round" fill="none">'
    '<path d="M250 210 L252 120 M252 150 L226 120 M252 136 L280 104 M266 120 L284 122 M238 132 L230 112" stroke-width="7"/>'
    '<path d="M640 210 L636 132 M636 160 L612 136 M638 146 L664 118 M650 132 L668 132" stroke-width="6"/>'
    '<path d="M930 210 L928 140 M928 166 L908 146 M929 152 L950 128" stroke-width="5"/>'
    '</g>'
    # pinheiros
    '<g fill="#07060e">'
    '<path d="M110 210 L130 120 L150 210 Z M116 170 L130 110 L144 170 Z"/>'
    '<path d="M420 210 L444 110 L468 210 Z M426 160 L444 96 L462 160 Z"/>'
    '<path d="M700 210 L720 130 L740 210 Z"/>'
    '<path d="M860 210 L880 118 L900 210 Z M866 166 L880 104 L894 166 Z"/>'
    '</g>'
    # lápides, cerca quebrada e mãos saindo do chão
    '<g fill="#0a0814">'
    '<path d="M330 210 L330 186 Q340 176 350 186 L350 210 Z"/><path d="M372 210 L372 192 Q380 184 388 192 L388 210 Z"/>'
    '<path d="M520 210 L520 174 L526 174 L526 210 Z M512 186 L534 186 L534 192 L512 192 Z"/>'
    '<path d="M780 210 L780 182 L786 180 L786 210 Z M800 210 L800 186 L806 190 L806 210 Z M772 192 L816 196 L816 200 L772 196 Z"/>'
    '<path d="M560 210 L562 190 L558 180 L562 178 L566 188 L568 176 L572 176 L571 188 L576 180 L579 182 L574 194 L574 210 Z"/>'
    '<path d="M1060 210 L1061 194 L1057 186 L1061 184 L1064 192 L1066 182 L1070 182 L1069 192 L1073 186 L1076 188 L1071 198 L1071 210 Z"/>'
    '<path d="M200 210 L201 196 L198 190 L201 188 L204 194 L206 186 L209 186 L208 194 L212 190 L214 192 L210 200 L210 210 Z"/>'
    '</g>'
)

_PORTA = (
    '<rect x="4" y="4" width="92" height="172" rx="4" fill="#4a4f57" stroke="#1c1f24" stroke-width="5"/>'
    '<rect x="16" y="16" width="68" height="148" rx="2" fill="#6b7280" stroke="#2c3037" stroke-width="3"/>'
    '<rect x="34" y="30" width="32" height="18" rx="2" fill="#f0b65a" stroke="#2c3037" stroke-width="3"/>'
    '<path d="M34 39 L66 39 M50 30 L50 48" stroke="#2c3037" stroke-width="2"/>'
    '<path d="M16 66 L84 76 M16 112 L84 104" stroke="#8b5e3c" stroke-width="10"/>'
    '<g fill="#2c3037"><circle cx="24" cy="24" r="2.5"/><circle cx="76" cy="24" r="2.5"/><circle cx="24" cy="156" r="2.5"/><circle cx="76" cy="156" r="2.5"/></g>'
    '<path d="M16 140 L28 164 M30 140 L42 164 M44 140 L56 164 M58 140 L70 164 M72 140 L82 160" stroke="#f2c230" stroke-width="6"/>'
    '<rect x="70" y="86" width="8" height="16" rx="2" fill="#2c3037"/>'
)

_SILHUETA = (
    '<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#2b2a33"/>'
    '<stop offset="1" stop-color="#55535f"/></linearGradient></defs>'
    '<g fill="url(#g)"><ellipse cx="30" cy="14" rx="9" ry="11"/>'
    '<path d="M24 24 Q30 28 36 24 L44 30 Q48 34 47 44 L50 80 Q50 84 46 83 L43 52 L42 70 L41 84 '
    'L39 136 L32 136 L30 94 L28 136 L21 136 L19 84 L18 70 L17 52 L14 83 Q10 84 10 80 L13 44 '
    'Q12 34 16 30 Z"/></g>'
)

_CORACAO = (
    '<g shape-rendering="crispEdges" fill="{cor}">'
    '<rect x="1" y="0" width="2" height="1"/><rect x="4" y="0" width="2" height="1"/>'
    '<rect x="0" y="1" width="7" height="2"/><rect x="1" y="3" width="5" height="1"/>'
    '<rect x="2" y="4" width="3" height="1"/><rect x="3" y="5" width="1" height="1"/></g>'
    '<rect x="1" y="1" width="1" height="1" fill="#ffffff99"/>'
)

CENARIO = data_uri(_CENARIO, "0 0 1200 210")
PORTA = data_uri(_PORTA, "0 0 100 180")
SILHUETA = data_uri(_SILHUETA, "0 0 60 140")
CORACAO_CHEIO = data_uri(_CORACAO.format(cor="#e53935"), "0 0 7 6")
CORACAO_VAZIO = data_uri(_CORACAO.format(cor="#3a3646").replace("#ffffff99", "#00000000"), "0 0 7 6")
