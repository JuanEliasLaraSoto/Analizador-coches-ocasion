from datetime import date

from ocasion.reglas import comprobar_coherencia, comprobar_km, frecuencia_itv

HOY = date(2026, 10, 1)


def test_itv_por_antiguedad():
    assert frecuencia_itv(2024, HOY).startswith("exento")
    assert frecuencia_itv(2020, HOY) == "cada 2 años"
    assert frecuencia_itv(2014, HOY) == "cada año"


def test_km_normales_no_avisan():
    assert comprobar_km(2016, 130_000, HOY) is None


def test_km_muy_bajos_avisan():
    alerta = comprobar_km(2014, 20_000, HOY)
    assert alerta is not None and alerta.nivel == "aviso"


def test_coherencia_detecta_imposibles():
    niveles = [a.nivel for a in comprobar_coherencia(2030, -5, 100, HOY)]
    assert niveles == ["grave", "grave", "grave"]


def test_coherencia_datos_normales():
    assert comprobar_coherencia(2016, 85_000, 11_900, HOY) == []
