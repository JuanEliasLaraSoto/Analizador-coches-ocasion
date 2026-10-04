"""Tests de opiniones con una respuesta falsa de la API: sin internet y sin gastar dinero."""

from types import SimpleNamespace as N

import pytest

from ocasion import llm, opiniones


def texto(t, *urls):
    citas = [N(type="web_search_result_location", url=u, title=f"Título {u}") for u in urls]
    return N(type="text", text=t, citations=citas or None)


# Así llega una respuesta real: la búsqueda, y el texto partido en trozos con sus citas.
BLOQUES = [
    N(type="server_tool_use"),
    N(type="web_search_tool_result"),
    texto("Esto es lo que dicen los propietarios:\n"),
    texto("+ Consumo bajo en carretera", "https://foro.example/a", "https://foro.example/a"),
    texto("\n"),
    texto("- Fallos en la válvula EGR", "https://foro.example/b"),
    texto("\n- El embrague dura poco"),  # sin cita: debe descartarse
]


def respuesta_falsa(bloques=BLOQUES, busquedas=2):
    servidor = N(web_search_requests=busquedas)
    uso = N(input_tokens=20_000, output_tokens=300, server_tool_use=servidor)
    return N(content=bloques, usage=uso)


def test_solo_se_quedan_los_puntos_con_fuente():
    puntos, descartadas = opiniones.puntos_con_fuente(BLOQUES)
    assert [(p["tipo"], p["texto"]) for p in puntos] == [
        ("fuerte", "Consumo bajo en carretera"),
        ("problema", "Fallos en la válvula EGR"),
    ]
    assert descartadas == 1
    assert len(puntos[0]["fuentes"]) == 1  # el enlace repetido aparece una sola vez


def test_enlaces_raros_no_cuentan_como_fuente():
    puntos, descartadas = opiniones.puntos_con_fuente([texto("- Malo", "javascript:alert(1)")])
    assert puntos == [] and descartadas == 1


def test_sin_datos_no_devuelve_puntos():
    puntos, descartadas = opiniones.puntos_con_fuente([texto("SIN_DATOS")])
    assert puntos == [] and descartadas == 0


@pytest.fixture
def api_falsa(monkeypatch):
    llamadas = []

    def falsa(consulta):
        llamadas.append(consulta)
        return respuesta_falsa()

    monkeypatch.setattr(opiniones, "_llamar_api", falsa)
    monkeypatch.setattr(llm, "PROVEEDOR", "claude")
    opiniones._CACHE.clear()
    return llamadas


def test_buscar_calcula_coste_con_busquedas(api_falsa):
    r, ll = opiniones.buscar("Seat", "León", 2016, "diesel")
    assert api_falsa == ["Coche: Seat León de 2016 diesel"]
    assert len(r["puntos"]) == 2 and r["descartados_sin_fuente"] == 1
    # 20.000 tokens de entrada + 300 de salida con Haiku + 2 búsquedas a 0,01 $
    assert ll.coste_usd == pytest.approx((20_000 * 1 + 300 * 5) / 1_000_000 + 2 * 0.01)


def test_la_segunda_vez_sale_de_la_cache(api_falsa):
    opiniones.buscar("Seat", "León", 2016, "diesel")
    r, ll = opiniones.buscar("SEAT", "León ", 2016, "diesel")  # mayúsculas/espacios: mismo coche
    assert len(api_falsa) == 1  # la API solo se ha llamado una vez
    assert r["desde_cache"] is True and ll is None


def test_llamada_sin_busquedas_cuesta_solo_tokens():
    ll = llm.Llamada("x", llm.HAIKU, 1_000_000, 0, 1.0)
    assert ll.coste_usd == pytest.approx(1.0)


def test_con_gemini_no_se_buscan_opiniones(api_falsa, monkeypatch):
    monkeypatch.setattr(llm, "PROVEEDOR", "gemini")
    r, ll = opiniones.buscar("Seat", "León", 2016, "diesel")
    assert r["puntos"] == [] and ll is None and api_falsa == []
