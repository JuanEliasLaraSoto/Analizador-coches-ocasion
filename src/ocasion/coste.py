"""Coste total estimado de tener el coche durante varios años."""

from dataclasses import dataclass

# Supuestos orientativos y visibles en el informe. Ajústalos si tienes mejores datos.
CONSUMO_L_100KM = {
    "gasolina": 6.5,
    "diesel": 5.2,
    "hibrido": 4.8,
    "hibrido_enchufable": 3.0,
    "glp": 8.5,
    "gnc": 6.0,
}
CONSUMO_KWH_100KM_ELECTRICO = 16.0
PRECIO_KWH = 0.20
SEGURO_ANUAL = 450.0
MANTENIMIENTO_ANUAL_BASE = 350.0
MANTENIMIENTO_EXTRA_POR_10K_KM = 40.0  # coches con más km necesitan más mantenimiento


@dataclass
class Coste:
    compra: float
    energia: float
    seguro: float
    mantenimiento: float
    anios: int
    supuestos: list[str]

    @property
    def total(self) -> float:
        return self.compra + self.energia + self.seguro + self.mantenimiento


def coste_total(
    precio: int,
    combustible: str,
    km_coche: int,
    km_anuales: int,
    precio_litro: float,
    anios: int = 3,
) -> Coste:
    """Compra + energía + seguro + mantenimiento durante `anios` años."""
    if combustible == "electrico":
        energia_anual = km_anuales / 100 * CONSUMO_KWH_100KM_ELECTRICO * PRECIO_KWH
        sup_energia = f"Eléctrico: {CONSUMO_KWH_100KM_ELECTRICO} kWh/100 km a {PRECIO_KWH} €/kWh"
    else:
        consumo = CONSUMO_L_100KM.get(combustible, CONSUMO_L_100KM["gasolina"])
        energia_anual = km_anuales / 100 * consumo * precio_litro
        sup_energia = f"Consumo medio de {consumo} L/100 km a {precio_litro:.3f} €/L"

    mantenimiento_anual = (
        MANTENIMIENTO_ANUAL_BASE + km_coche / 10_000 * MANTENIMIENTO_EXTRA_POR_10K_KM
    )
    return Coste(
        compra=float(precio),
        energia=round(energia_anual * anios, 2),
        seguro=SEGURO_ANUAL * anios,
        mantenimiento=round(mantenimiento_anual * anios, 2),
        anios=anios,
        supuestos=[
            sup_energia,
            f"{km_anuales:,} km al año".replace(",", "."),
            f"Seguro orientativo de {SEGURO_ANUAL:.0f} €/año",
            f"Mantenimiento de {mantenimiento_anual:.0f} €/año según los km del coche",
        ],
    )
