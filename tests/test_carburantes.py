from ocasion import carburantes
from ocasion.carburantes import a_numero, precio_actual, precio_mediano
from ocasion.texto import normalizar

ESTACIONES = [
    {"Precio Gasoleo A": "1,459", "Precio Gasolina 95 E5": "1,559"},
    {"Precio Gasoleo A": "1,399", "Precio Gasolina 95 E5": ""},
    {"Precio Gasoleo A": "1,519", "Precio Gasolina 95 E5": "1,609"},
]


def test_a_numero():
    assert a_numero("1,459") == 1.459
    assert a_numero("") is None


def test_normalizar_provincia():
    assert normalizar("  Málaga ") == "malaga"


def test_precio_mediano_ignora_vacios():
    assert precio_mediano(ESTACIONES, "diesel") == 1.459
    assert precio_mediano(ESTACIONES, "gasolina") == 1.584


def test_usa_respaldo_si_la_api_falla(monkeypatch):
    def falla(_):
        raise carburantes.httpx.ConnectError("sin red")

    monkeypatch.setattr(carburantes, "descargar_provincia", falla)
    assert precio_actual("Málaga", "diesel") == (carburantes.PRECIO_RESPALDO["diesel"], "respaldo")


def test_provincia_desconocida_usa_respaldo():
    assert precio_actual("Narnia", "gasolina")[1] == "respaldo"
