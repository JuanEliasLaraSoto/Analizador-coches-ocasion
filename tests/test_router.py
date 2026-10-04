from ocasion import llm
from ocasion.router import modelo_informe


def analisis(alertas=(), desconocidos=2):
    proc = {f"c{i}": "desconocido" for i in range(desconocidos)}
    return {"alertas": [{"nivel": n, "mensaje": ""} for n in alertas], "procedencia": proc}


def test_caso_sencillo_usa_haiku():
    assert modelo_informe([analisis()]) == llm.HAIKU


def test_varios_anuncios_usa_sonnet():
    assert modelo_informe([analisis(), analisis()]) == llm.SONNET


def test_alerta_grave_usa_sonnet():
    assert modelo_informe([analisis(alertas=["grave"])]) == llm.SONNET


def test_estrategia_forzada():
    assert modelo_informe([analisis(), analisis()], "haiku") == llm.HAIKU
