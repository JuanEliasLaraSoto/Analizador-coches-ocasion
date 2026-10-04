"""Reglas deterministas: lo que se puede deducir sin IA."""

from dataclasses import dataclass
from datetime import date

KM_MEDIOS_ANUALES = 13_000  # referencia aproximada para turismos en España


@dataclass
class Alerta:
    nivel: str  # "info", "aviso" o "grave"
    mensaje: str


def edad(anio: int, hoy: date | None = None) -> int:
    hoy = hoy or date.today()
    return hoy.year - anio


def frecuencia_itv(anio: int, hoy: date | None = None) -> str:
    """Periodicidad de la ITV de un turismo particular según su antigüedad."""
    e = edad(anio, hoy)
    if e < 4:
        return "exento (menos de 4 años)"
    if e < 10:
        return "cada 2 años"
    return "cada año"


def comprobar_km(anio: int, km: int, hoy: date | None = None) -> Alerta | None:
    """Marca kilometrajes muy bajos (posible manipulación) o muy altos para su edad."""
    anios = max(edad(anio, hoy), 1)
    km_anio = km / anios
    if anios >= 3 and km_anio < 0.3 * KM_MEDIOS_ANUALES:
        mensaje = (
            f"Kilometraje muy bajo para su edad ({km_anio:,.0f} km/año). Pide el historial de ITV."
        )
        return Alerta("aviso", mensaje)
    if km_anio > 2.5 * KM_MEDIOS_ANUALES:
        mensaje = f"Kilometraje alto ({km_anio:,.0f} km/año): uso intensivo, revisa el desgaste."
        return Alerta("info", mensaje)
    return None


def comprobar_coherencia(
    anio: int | None, km: int | None, precio: int | None, hoy: date | None = None
) -> list[Alerta]:
    """Detecta datos imposibles o absurdos."""
    hoy = hoy or date.today()
    alertas = []
    if anio is not None and (anio > hoy.year or anio < 1950):
        alertas.append(Alerta("grave", f"Año de matriculación imposible: {anio}."))
    if km is not None and (km < 0 or km > 1_500_000):
        alertas.append(Alerta("grave", f"Kilometraje imposible: {km}."))
    if precio is not None and precio < 500:
        alertas.append(
            Alerta("grave", f"Precio sospechosamente bajo ({precio} €): posible estafa o error.")
        )
    return alertas
