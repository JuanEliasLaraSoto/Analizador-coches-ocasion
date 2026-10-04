import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def coches_sinteticos() -> pd.DataFrame:
    """Dataset pequeño e inventado para probar el modelo sin depender del real."""
    rng = np.random.default_rng(0)
    filas = []
    for _ in range(300):
        modelo, base = [("leon", 22000), ("ibiza", 17000), ("golf", 26000)][rng.integers(3)]
        anio = int(rng.integers(2010, 2025))
        km = int(13000 * (2026 - anio) + rng.integers(0, 5000))
        precio = base * 0.87 ** (2026 - anio) * rng.lognormal(0, 0.05)
        filas.append(
            {
                "marca": "seat" if modelo != "golf" else "volkswagen",
                "modelo": modelo,
                "anio": anio,
                "km": km,
                "combustible": "diesel",
                "cambio": "manual",
                "potencia_cv": np.nan,
                "precio": round(precio),
            }
        )
    return pd.DataFrame(filas)
