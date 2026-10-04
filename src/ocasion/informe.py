"""Redacta el informe final a partir de los datos ya calculados."""

import json

from pydantic import BaseModel

from ocasion import llm

SYSTEM = """Eres un asesor que ayuda a comprar coches de segunda mano en España.
Recibes en JSON los datos ya calculados de uno o varios anuncios.
Reglas:
- Usa SOLO las cifras del JSON. No inventes precios, consumos ni datos del coche.
- Distingue lo que dice el vendedor (procedencia 'anuncio'), lo deducido y lo desconocido.
- Lo desconocido se convierte en preguntas concretas para el vendedor.
- Recomienda siempre pedir el informe del vehículo de la DGT y una revisión mecánica
  antes de pagar.
- Si hay varios anuncios, compáralos y ordénalos del más al menos recomendable.
- Tono claro y directo, en español, sin tecnicismos."""


class Informe(BaseModel):
    veredicto: str
    puntos_fuertes: list[str]
    alertas: list[str]
    preguntas_vendedor: list[str]
    ranking: list[str]  # vacío si solo hay un anuncio


def redactar(analisis: list[dict], modelo: str):
    datos = json.dumps(analisis, ensure_ascii=False, default=str)
    return llm.parse(
        "informe", modelo, SYSTEM, f"<datos>\n{datos}\n</datos>", Informe, max_tokens=1500
    )
