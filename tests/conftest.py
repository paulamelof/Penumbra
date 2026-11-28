from pathlib import Path

import pytest

from src.base_conhecimento import montar_base
from src.catalogo import carregar_catalogo
from src.modelos import Percepcao

CSV = Path(__file__).resolve().parent.parent / "data" / "caracteristicas.csv"


@pytest.fixture(scope="session")
def catalogo():
    return carregar_catalogo(CSV)


@pytest.fixture(scope="session")
def base(catalogo):
    return montar_base(catalogo)


@pytest.fixture
def percepcao(catalogo):
    """Fábrica de percepções: percepcao(3, "mochila") ou percepcao(1, None) para névoa."""
    por_id = {c.id: c for c in catalogo}

    def criar(passo: int, id_carac: str | None) -> Percepcao:
        carac = por_id[id_carac] if id_carac else None
        return Percepcao(passo=passo, distancia=7 - passo, caracteristica=carac)

    return criar
