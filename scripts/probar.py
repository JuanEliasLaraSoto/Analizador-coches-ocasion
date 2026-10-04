"""Prueba rápida desde la terminal (llama a la API de verdad).

Uso:
    uv run python scripts/probar.py "Vendo Seat León 1.6 TDI de 2016, 85.000 km, 11.900 €"
"""

import json
import sys

from ocasion.analizar import analizar

if __name__ == "__main__":
    resultado = analizar([sys.argv[1]])
    print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str))
