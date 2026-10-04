import numpy as np

from ocasion.precio import ModeloPrecio, baseline, valorar


def test_modelo_aprende(coches_sinteticos):
    """Comprueba que el código funciona. Si gana o no al baseline se mide con datos reales."""
    train, test = coches_sinteticos.iloc[:240], coches_sinteticos.iloc[240:]
    modelo = ModeloPrecio.entrenar(train, max_iter=100)
    error_pct = np.mean(
        np.abs(modelo.predecir(test)["precio_estimado"] - test["precio"]) / test["precio"]
    )
    assert error_pct < 0.15


def test_baseline_usa_medianas(coches_sinteticos):
    pred = baseline(coches_sinteticos, coches_sinteticos.head(5))
    assert len(pred) == 5 and (pred > 0).all()


def test_rango_contiene_la_estimacion(coches_sinteticos):
    modelo = ModeloPrecio.entrenar(coches_sinteticos, max_iter=50)
    pred = modelo.predecir(coches_sinteticos.head(20))
    assert (pred["rango_min"] <= pred["precio_estimado"]).all()
    assert (pred["precio_estimado"] <= pred["rango_max"]).all()


def test_valorar_un_coche(coches_sinteticos):
    modelo = ModeloPrecio.entrenar(coches_sinteticos, max_iter=50)
    v = valorar(
        modelo,
        {
            "marca": "seat",
            "modelo": "leon",
            "anio": 2016,
            "km": 130_000,
            "combustible": "diesel",
            "cambio": "manual",
            "precio": 50_000,
        },
    )
    assert v["veredicto"] == "por encima del rango"
