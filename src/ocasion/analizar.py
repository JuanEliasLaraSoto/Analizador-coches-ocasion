"""Orquesta todas las piezas: extracción -> reglas -> precio -> coste -> informe."""

from dataclasses import asdict
from datetime import date

from ocasion import informe, router
from ocasion.carburantes import precio_actual
from ocasion.coste import coste_total
from ocasion.extraccion import extraer_de_imagen, extraer_de_texto
from ocasion.ficha import FichaExtraida, procedencias
from ocasion.precio import ModeloPrecio, valorar
from ocasion.reglas import comprobar_coherencia, comprobar_km, frecuencia_itv
from ocasion.texto import normalizar

_modelo_precio: ModeloPrecio | None = None


def modelo_precio() -> ModeloPrecio:
    global _modelo_precio
    if _modelo_precio is None:
        _modelo_precio = ModeloPrecio.cargar()
    return _modelo_precio


def analizar_ficha(
    ficha: FichaExtraida, km_anuales: int, provincia: str, descartados: list[str]
) -> dict:
    """Todo lo determinista: sin LLM. Fácil de testear."""
    hoy = date.today()
    proc = procedencias(ficha)
    deducido: dict = {}
    alertas = comprobar_coherencia(ficha.anio, ficha.km, ficha.precio, hoy)

    if ficha.anio:
        deducido["frecuencia_itv"] = frecuencia_itv(ficha.anio, hoy)
        if ficha.km is not None and (a := comprobar_km(ficha.anio, ficha.km, hoy)):
            alertas.append(a)

    valoracion = None
    if ficha.marca and ficha.modelo and ficha.anio and ficha.km is not None:
        coche = {
            "marca": normalizar(ficha.marca),
            "modelo": normalizar(ficha.modelo),
            "combustible": ficha.combustible,
            "cambio": ficha.cambio,
            "anio": ficha.anio,
            "km": ficha.km,
            "potencia_cv": ficha.potencia_cv,
            "precio": ficha.precio,
        }
        valoracion = valorar(modelo_precio(), coche)

    coste = None
    if ficha.precio and ficha.combustible:
        litro, origen = precio_actual(provincia, ficha.combustible)
        c = coste_total(ficha.precio, ficha.combustible, ficha.km or 0, km_anuales, litro)
        coste = {**asdict(c), "total": round(c.total), "origen_precio_carburante": origen}

    return {
        "ficha": ficha.model_dump(exclude={"citas"}),
        "procedencia": proc,
        "campos_descartados_por_no_tener_cita": descartados,
        "deducido": deducido,
        "alertas": [asdict(a) for a in alertas],
        "valoracion_precio": valoracion,
        "coste_3_anios": coste,
    }


def analizar(
    anuncios: list[str],
    km_anuales: int = 15_000,
    provincia: str = "Malaga",
    imagenes: list[tuple[bytes, str]] | None = None,
    estrategia: str = "router",
) -> dict:
    llamadas = []
    resultados = []
    for texto in anuncios:
        ficha, descartados, ll = extraer_de_texto(texto)
        llamadas.append(ll)
        resultados.append(analizar_ficha(ficha, km_anuales, provincia, descartados))
    for imagen, mime in imagenes or []:
        ficha, descartados, ll = extraer_de_imagen(imagen, mime)
        llamadas.append(ll)
        r = analizar_ficha(ficha, km_anuales, provincia, descartados)
        r["nota"] = "Datos leídos de una imagen: no se han podido verificar las citas."
        resultados.append(r)

    modelo = router.modelo_informe(resultados, estrategia)
    inf, ll = informe.redactar(resultados, modelo)
    llamadas.append(ll)

    return {
        "informe": inf.model_dump(),
        "analisis": resultados,
        "uso": {
            "modelos": sorted({x.modelo for x in llamadas}),
            "coste_usd": round(sum(x.coste_usd for x in llamadas), 5),
            "segundos": round(sum(x.segundos for x in llamadas), 2),
            "tokens": sum(x.tokens_entrada + x.tokens_salida for x in llamadas),
        },
    }
