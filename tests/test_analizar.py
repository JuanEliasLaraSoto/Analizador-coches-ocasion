"""Prueba de principio a fin con un LLM falso: no gasta dinero ni necesita API key."""

import pytest

from ocasion import analizar as pipeline
from ocasion import carburantes, informe, llm
from ocasion.ficha import Cita, FichaExtraida
from ocasion.precio import ModeloPrecio

ANUNCIO = "Vendo Seat León 1.6 TDI del 2016, 85.000 km, 11.900 €. Diésel, cambio manual."


def llm_falso(tarea, modelo, system, contenido, formato, max_tokens=2000):
    llamada = llm.Llamada(tarea, modelo, 1000, 200, 0.5)
    if formato is FichaExtraida:
        ficha = FichaExtraida(
            marca="Seat",
            modelo="León",
            anio=2016,
            km=85000,
            precio=11900,
            combustible="diesel",
            num_duenos=1,  # inventado: no aparece en el anuncio
            citas=[
                Cita(campo=c, texto=t)
                for c, t in [
                    ("marca", "Seat"),
                    ("modelo", "León"),
                    ("anio", "2016"),
                    ("km", "85.000 km"),
                    ("precio", "11.900 €"),
                    ("combustible", "Diésel"),
                    ("num_duenos", "1 dueño"),
                ]
            ],
        )
        return ficha, llamada
    return informe.Informe(
        veredicto="ok", puntos_fuertes=[], alertas=[], preguntas_vendedor=[], ranking=[]
    ), llamada


@pytest.fixture
def entorno(monkeypatch, coches_sinteticos):
    monkeypatch.setattr(llm, "parse", llm_falso)
    monkeypatch.setattr(
        carburantes, "descargar_provincia", lambda _: [{"Precio Gasoleo A": "1,500"}]
    )
    carburantes._CACHE.clear()
    monkeypatch.setattr(
        pipeline, "_modelo_precio", ModeloPrecio.entrenar(coches_sinteticos, max_iter=50)
    )


def test_pipeline_completo(entorno):
    r = pipeline.analizar([ANUNCIO], km_anuales=15_000, provincia="Málaga")
    a = r["analisis"][0]
    assert a["ficha"]["num_duenos"] is None  # la alucinación se ha descartado
    assert a["campos_descartados_por_no_tener_cita"] == ["num_duenos"]
    assert a["procedencia"]["num_duenos"] == "desconocido"
    assert a["deducido"]["frecuencia_itv"] == "cada año"
    assert a["valoracion_precio"]["rango_min"] > 0
    assert a["coste_3_anios"]["origen_precio_carburante"] == "api"
    assert r["uso"]["modelos"] == [llm.HAIKU]
    assert r["uso"]["coste_usd"] == pytest.approx(2 * (1000 * 1 + 200 * 5) / 1_000_000)


def test_varios_anuncios_usan_sonnet_para_el_informe(entorno):
    r = pipeline.analizar([ANUNCIO, ANUNCIO])
    assert llm.SONNET in r["uso"]["modelos"]


def test_opiniones_solo_si_se_piden(entorno, monkeypatch):
    def buscar_falso(marca, modelo, anio, combustible):
        llamada = llm.Llamada("opiniones", llm.HAIKU, 0, 0, 1.0, busquedas=1)
        return {"puntos": [], "desde_cache": False}, llamada

    monkeypatch.setattr(pipeline.opiniones, "buscar", buscar_falso)
    sin = pipeline.analizar([ANUNCIO])
    con = pipeline.analizar([ANUNCIO], con_opiniones=True)
    assert "opiniones" not in sin["analisis"][0]
    assert con["analisis"][0]["opiniones"]["puntos"] == []
    assert con["uso"]["coste_usd"] == pytest.approx(sin["uso"]["coste_usd"] + 0.01)
