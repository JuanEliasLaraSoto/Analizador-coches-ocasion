"""Evalúa la extracción y el informe con anuncios de prueba (llama a la API de verdad).

Uso:
    uv run python evals/evaluar.py                 # estrategia router
    uv run python evals/evaluar.py --estrategia sonnet
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from ocasion import analizar, informe, router
from ocasion.extraccion import extraer_de_texto
from ocasion.ficha import CAMPOS_FICHA
from ocasion.texto import normalizar

CASOS = Path(__file__).parent / "anuncios.jsonl"
RESULTADOS = Path(__file__).parent / "resultados"


def iguales(a, b) -> bool:
    if isinstance(a, str) and isinstance(b, str):
        return normalizar(a) == normalizar(b)
    return a == b


def cifras_inventadas(texto: str, datos: str) -> list[str]:
    """Números de 3 o más cifras del informe que no aparecen en los datos de entrada."""
    numeros_datos = set(re.findall(r"\d+", datos.replace(".", "")))
    return [n for n in re.findall(r"\d{3,}", texto.replace(".", "")) if n not in numeros_datos]


def evaluar(estrategia: str) -> dict:
    casos = [json.loads(linea) for linea in CASOS.read_text().splitlines() if linea.strip()]
    aciertos = total = alucinaciones = descartes = inventadas = 0
    coste = segundos = 0.0
    fallos = []

    for caso in casos:
        ficha, descartados, ll = extraer_de_texto(caso["texto"])
        coste += ll.coste_usd
        segundos += ll.segundos
        descartes += len(descartados)
        esperado = caso["esperado"]
        for campo in CAMPOS_FICHA:
            obtenido, correcto = getattr(ficha, campo), esperado.get(campo)
            total += 1
            if iguales(obtenido, correcto):
                aciertos += 1
            else:
                fallos.append(f"{caso['id']}.{campo}: esperado {correcto!r}, obtenido {obtenido!r}")
                if correcto is None and obtenido is not None:
                    alucinaciones += 1

        # Informe: ¿usa cifras que no estaban en los datos?
        resultado = analizar.analizar_ficha(ficha, 15_000, "Malaga", descartados)
        modelo = router.modelo_informe([resultado], estrategia)
        inf, ll = informe.redactar([resultado], modelo)
        coste += ll.coste_usd
        segundos += ll.segundos
        datos = json.dumps(resultado, ensure_ascii=False, default=str)
        inventadas += len(
            cifras_inventadas(json.dumps(inf.model_dump(), ensure_ascii=False), datos)
        )

    return {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "estrategia": estrategia,
        "casos": len(casos),
        "campos_correctos_pct": round(aciertos / total * 100, 1),
        "alucinaciones_tras_verificar": alucinaciones,
        "campos_descartados_por_cita": descartes,
        "cifras_inventadas_en_informes": inventadas,
        "coste_total_usd": round(coste, 4),
        "coste_por_anuncio_usd": round(coste / len(casos), 5),
        "segundos_por_anuncio": round(segundos / len(casos), 2),
        "fallos": fallos,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--estrategia", choices=["router", "haiku", "sonnet"], default="router")
    r = evaluar(parser.parse_args().estrategia)
    RESULTADOS.mkdir(exist_ok=True)
    (RESULTADOS / f"{r['fecha'][:10]}_{r['estrategia']}.json").write_text(
        json.dumps(r, indent=2, ensure_ascii=False)
    )
    print(json.dumps({k: v for k, v in r.items() if k != "fallos"}, indent=2, ensure_ascii=False))
    print("\nFallos:", *r["fallos"], sep="\n  ")
