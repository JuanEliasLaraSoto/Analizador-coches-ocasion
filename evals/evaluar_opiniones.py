"""Evalúa las opiniones de propietarios (llama a la API de verdad: cuesta unos céntimos).

Uso:
    uv run python evals/evaluar_opiniones.py
"""

import json
from datetime import datetime
from pathlib import Path

from ocasion import opiniones

COCHES = [
    ("Seat", "León", 2016, "diesel"),
    ("Volkswagen", "Golf", 2018, "gasolina"),
    ("Toyota", "Corolla", 2020, "hibrido"),
    ("Renault", "Clio", 2015, "gasolina"),
    ("Peugeot", "308", 2017, "diesel"),
]
RESULTADOS = Path(__file__).parent / "resultados"


def main() -> None:
    puntos = descartados = busquedas = 0
    coste = segundos = 0.0
    sin_resultados = []
    for coche in COCHES:
        r, ll = opiniones.buscar(*coche)
        puntos += len(r["puntos"])
        descartados += r["descartados_sin_fuente"]
        if not r["puntos"]:
            sin_resultados.append(" ".join(map(str, coche)))
        if ll:
            coste += ll.coste_usd
            segundos += ll.segundos
            busquedas += ll.busquedas

    total = puntos + descartados
    resumen = {
        "coches": len(COCHES),
        "puntos_con_fuente": puntos,
        "puntos_descartados_sin_fuente": descartados,
        "pct_con_fuente": round(100 * puntos / total, 1) if total else None,
        "coches_sin_resultados": sin_resultados,
        "busquedas": busquedas,
        "coste_usd_medio": round(coste / len(COCHES), 4),
        "segundos_medios": round(segundos / len(COCHES), 1),
    }
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    RESULTADOS.mkdir(exist_ok=True)
    nombre = f"opiniones-{datetime.now():%Y%m%d-%H%M}.json"
    (RESULTADOS / nombre).write_text(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
