"""Opiniones de propietarios: Claude busca en la web y resume, citando cada fuente.

No rastreamos foros con un robot propio (suele estar prohibido y trae datos personales).
Usamos la herramienta de búsqueda web de la API de Claude y nos quedamos solo con los puntos
que traen una cita a una página pública: lo que no tiene fuente, se descarta.
"""

import json
import logging
import time

from ocasion import llm

MAX_BUSQUEDAS = 3  # cada búsqueda cuesta dinero: limitamos cuántas puede hacer Claude
CACHE_SEGUNDOS = 7 * 24 * 3600  # las opiniones de un modelo no cambian de un día para otro

SYSTEM = """Eres un asistente que investiga la fiabilidad de coches de segunda mano en España.
Busca en la web opiniones de propietarios (foros, reseñas, pruebas de larga duración)
del coche que te indican y resume lo que más se repite.
Formato de la respuesta, una idea por línea:
+ punto fuerte que mencionan los propietarios
- problema, avería o queja típica
Reglas:
- Cada línea debe apoyarse en lo que has encontrado en la búsqueda. No inventes nada.
- Máximo 4 líneas con + y 4 con -. Frases cortas, en español.
- No incluyas nombres de usuario, nicks ni datos personales.
- Si no encuentras opiniones fiables de ese modelo, responde solo: SIN_DATOS"""

log = logging.getLogger("ocasion.opiniones")
_CACHE: dict[tuple, tuple[float, dict]] = {}


def _clave(marca: str, modelo: str, anio: int | None, combustible: str | None) -> tuple:
    return (marca.lower().strip(), modelo.lower().strip(), anio, combustible)


def _consulta(marca: str, modelo: str, anio: int | None, combustible: str | None) -> str:
    partes = [marca, modelo]
    if anio:
        partes.append(f"de {anio}")
    if combustible:
        partes.append(combustible)
    return "Coche: " + " ".join(partes)


def puntos_con_fuente(bloques) -> tuple[list[dict], int]:
    """Convierte la respuesta en puntos {tipo, texto, fuentes}.

    La API devuelve el texto en trozos (bloques); cada trozo trae las citas en las que se
    apoya. Juntamos los trozos línea a línea y descartamos las líneas sin ninguna cita.
    Devuelve (puntos, número de líneas descartadas por no tener fuente).
    """
    lineas: list[dict] = [{"texto": "", "fuentes": {}}]
    for b in bloques:
        if getattr(b, "type", None) != "text":
            continue  # bloques de la búsqueda en sí: no son texto para el usuario
        trozos = b.text.split("\n")
        for i, trozo in enumerate(trozos):
            if i > 0:
                lineas.append({"texto": "", "fuentes": {}})
            lineas[-1]["texto"] += trozo
        for c in getattr(b, "citations", None) or []:
            es_web = getattr(c, "type", None) == "web_search_result_location"
            if es_web and c.url.startswith(("https://", "http://")):
                lineas[-1]["fuentes"][c.url] = c.title or c.url  # dict: sin enlaces repetidos

    puntos, descartadas = [], 0
    for linea in lineas:
        texto = linea["texto"].strip()
        if not texto or texto[0] not in "+-":
            continue  # líneas de relleno ("Esto es lo que he encontrado:")
        if not linea["fuentes"]:
            descartadas += 1  # sin cita no hay forma de comprobarlo: fuera
            continue
        puntos.append(
            {
                "tipo": "fuerte" if texto[0] == "+" else "problema",
                "texto": texto[1:].strip(),
                "fuentes": [{"url": u, "titulo": t} for u, t in linea["fuentes"].items()],
            }
        )
    return puntos, descartadas


def _llamar_api(consulta: str):
    """La única función que habla con la API (en los tests se sustituye por una falsa)."""
    return llm.cliente().messages.create(
        model=llm.HAIKU,
        max_tokens=1500,
        system=SYSTEM,
        messages=[{"role": "user", "content": consulta}],
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": MAX_BUSQUEDAS,
                "user_location": {"type": "approximate", "country": "ES"},
            }
        ],
    )


def buscar(
    marca: str, modelo: str, anio: int | None = None, combustible: str | None = None
) -> tuple[dict, llm.Llamada | None]:
    """Devuelve (opiniones, Llamada). Si estaba en caché, la Llamada es None (coste 0)."""
    if llm.PROVEEDOR != "claude":
        # La búsqueda web con citas es una herramienta de la API de Claude.
        aviso = "Las opiniones de propietarios solo están disponibles con PROVEEDOR=claude."
        return {
            "puntos": [],
            "descartados_sin_fuente": 0,
            "aviso": aviso,
            "desde_cache": False,
        }, None
    clave = _clave(marca, modelo, anio, combustible)
    guardado = _CACHE.get(clave)
    if guardado and time.time() - guardado[0] < CACHE_SEGUNDOS:
        return {**guardado[1], "desde_cache": True}, None

    inicio = time.perf_counter()
    respuesta = _llamar_api(_consulta(marca, modelo, anio, combustible))
    uso_servidor = getattr(respuesta.usage, "server_tool_use", None)
    llamada = llm.Llamada(
        "opiniones",
        llm.HAIKU,
        respuesta.usage.input_tokens,
        respuesta.usage.output_tokens,
        round(time.perf_counter() - inicio, 2),
        busquedas=getattr(uso_servidor, "web_search_requests", 0) or 0,
    )

    puntos, descartadas = puntos_con_fuente(respuesta.content)
    resultado = {
        "puntos": puntos,
        "descartados_sin_fuente": descartadas,
        "aviso": "Opiniones de internet resumidas por IA. No son hechos comprobados.",
        "desde_cache": False,
    }
    _CACHE[clave] = (time.time(), resultado)
    log.info(json.dumps({"tarea": "opiniones", "puntos": len(puntos), "descartados": descartadas}))
    return resultado, llamada
