import dataclasses
from dataclasses import dataclass, field

from src.base_conhecimento import BaseConhecimento
from src.inferencia import chance_monstro
from src.modelos import Acao, Percepcao, Resultado

# Pontuação do PEAS: o "custo" de cada erro.
CUSTO_MONSTRO_ADMITIDO = 20  # deixar um monstro entrar (erro grave)
CUSTO_HUMANO_MORTO = 5  # matar um humano (erro leve)

ULTIMO_PASSO = 6
TOLERANCIA = 1e-9  # evita erro de arredondamento ao comparar com a garantia


@dataclass
class Decisao:
    """O que o agente pensou e fez em UM passo (serve para a tela e para o histórico)."""

    passo: int
    distancia: int
    caracteristica: str | None  # id da pista vista, ou None na névoa
    acao: Acao
    tipo: str | None  # "provada" | "garantia" | "forcada"; None quando só espera
    chance_monstro: float
    explicadas: list[str] = field(default_factory=list)
    regras: list[str] = field(default_factory=list)
    explicacao: str = ""


def _num(x: float, algarismos: int = 3) -> str:
    """Número com vírgula, como no português: 0.3 -> '0,3', 2.25 -> '2,25'."""
    return f"{x:.{algarismos}g}".replace(".", ",")


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%".replace(".", ",")


class Agente:
    def __init__(self, base: BaseConhecimento, garantia_matar: float = 0.80, garantia_entrar: float = 0.95):
        for nome, valor in (("garantia_matar", garantia_matar), ("garantia_entrar", garantia_entrar)):
            if not 0 < valor <= 1:
                raise ValueError(f"{nome} precisa estar entre 0 e 1 (recebi {valor})")
        self.base = base
        self.garantia_matar = garantia_matar
        self.garantia_entrar = garantia_entrar
        self.reiniciar()

    # ------------------------------------------------------------------ estado
    def reiniciar(self) -> None:
        """Esquece o encontro atual (chamado sozinho no passo 1)."""
        self.fatos: list[str] = []  # ids das pistas vistas, na ordem
        self.registro: list[Decisao] = []  # uma Decisao por passo
        self.decisao: Decisao | None = None  # a do passo mais recente

    # ---------------------------------------------------------------- principal
    def perceber(self, percepcao: Percepcao) -> Acao:
        """Recebe a percepção do passo e devolve a ação (esperar, matar ou permitir)."""
        if percepcao.passo == 1:
            self.reiniciar()

        carac = percepcao.caracteristica
        if carac is not None and carac.id not in self.fatos:
            self.fatos.append(carac.id)  # acrescenta aos fatos do encontro

        decisao = self._decidir(percepcao)
        self.registro.append(decisao)
        self.decisao = decisao
        return decisao.acao

    def explicar(self) -> list[str]:
        """A explicação passo a passo do encontro até agora (uma linha por passo)."""
        return [d.explicacao for d in self.registro]

    # ------------------------------------------------------------------ decisão
    def _decidir(self, p: Percepcao) -> Decisao:
        carac_id = p.caracteristica.id if p.caracteristica else None
        cabecalho = f"Passo {p.passo} (distância {p.distancia}): "

        # Ciclo de decisão, item 2: na névoa o agente só espera (e não pode decidir).
        if carac_id is None and p.passo < ULTIMO_PASSO:
            calculo = chance_monstro(self.fatos, self.base)
            texto = cabecalho + "névoa, nenhuma característica visível. Espera."
            return Decisao(p.passo, p.distancia, None, Acao.ESPERAR, None,
                           calculo.chance_monstro, calculo.explicadas, calculo.regras, texto)

        # Itens 3 a 5: aplica certeza e anulação e recalcula a chance do zero.
        calculo = chance_monstro(self.fatos, self.base)
        chance = calculo.chance_monstro
        texto = cabecalho + self._descrever_pista(carac_id, calculo)

        def decisao(acao: Acao, tipo: str | None, resumo: str) -> Decisao:
            return Decisao(p.passo, p.distancia, carac_id, acao, tipo, chance,
                           calculo.explicadas, calculo.regras, texto + resumo)

        # Item 4: certeza (específica) decide na hora.
        if calculo.prova == "monstro":
            return decisao(Acao.MATAR, "provada", f" Decisão: MATAR (provada: {carac_id} prova que é monstro).")
        if calculo.prova == "humano":
            return decisao(Acao.PERMITIR, "provada", f" Decisão: DEIXAR ENTRAR (provada: {carac_id} prova que é humano).")

        # Item 6: garantia de matar.
        if chance + TOLERANCIA >= self.garantia_matar:
            return decisao(Acao.MATAR, "garantia",
                           f" Decisão: MATAR (por garantia: {_pct(chance)} ≥ {_pct(self.garantia_matar)} de monstro).")

        # Item 7: garantia de entrada.
        chance_humano = 1 - chance
        if chance_humano + TOLERANCIA >= self.garantia_entrar:
            return decisao(Acao.PERMITIR, "garantia",
                           f" Decisão: DEIXAR ENTRAR (por garantia: {_pct(chance_humano)} ≥ {_pct(self.garantia_entrar)} de humano).")

        # Item 8: ainda dá tempo, espera.
        if p.passo < ULTIMO_PASSO:
            return decisao(Acao.ESPERAR, None, " Sem garantia ainda. Espera.")

        # Item 9: 6º passo sem garantia, decisão forçada pelo menor custo esperado.
        custo_matar = CUSTO_HUMANO_MORTO * chance_humano  # só erro se for humano
        custo_entrar = CUSTO_MONSTRO_ADMITIDO * chance  # só erro se for monstro
        conta = (f" Decisão forçada (6º passo). Custo de matar = {CUSTO_HUMANO_MORTO} × {_pct(chance_humano)} = {_num(custo_matar)}; "
                 f"custo de deixar entrar = {CUSTO_MONSTRO_ADMITIDO} × {_pct(chance)} = {_num(custo_entrar)}.")
        if custo_entrar < custo_matar:  # empate: na dúvida, não abre
            return decisao(Acao.PERMITIR, "forcada", conta + " Decisão: DEIXAR ENTRAR (forçada, menor custo).")
        return decisao(Acao.MATAR, "forcada", conta + " Decisão: MATAR (forçada, menor custo).")

    def _descrever_pista(self, carac_id: str | None, calculo) -> str:
        """Texto da parte 'o que vi e o que concluí' de um passo visível."""
        if carac_id is None:
            return "sem característica neste passo."
        fator = self.base.fatores[carac_id]
        if carac_id in self.base.certeza_por_id:
            lado = self.base.certeza_por_id[carac_id].conclusao
            texto = f"viu {carac_id} (específica: certeza de {lado})."
        else:
            texto = f"viu {carac_id} (fator ×{_num(fator)})."
        for regra in calculo.regras:
            if regra.startswith("anulação"):
                texto += f" {regra.capitalize()}."
        if calculo.prova is None:
            texto += f" Chance de monstro: {_pct(calculo.chance_monstro)}."
        return texto


def completar_resultado(resultado: Resultado, agente: Agente) -> Resultado:
    """Cola no Resultado do ambiente o que só o agente sabe.

    O ambiente não conhece o agente, então ele não consegue preencher o tipo de decisão,
    a chance e a cadeia de raciocínio. Quem junta os dois (metricas.py e app.py) chama
    esta função logo depois de ambiente.aplicar(acao).
    """
    d = agente.decisao
    return dataclasses.replace(
        resultado,
        tipo_decisao=d.tipo or "",
        chance_monstro=d.chance_monstro,
        cadeia=agente.explicar(),
    )
