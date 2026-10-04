import numpy as np
import pandas as pd

from ocasion.datos import a_entero, cargar, limpiar


def test_a_entero_formatos_espanoles():
    assert a_entero("12.500 €") == 12500
    assert a_entero("85.000 km") == 85000
    assert a_entero("110 CV") == 110
    assert a_entero(2016) == 2016
    assert np.isnan(a_entero(None))


def test_limpiar_normaliza_y_filtra():
    df = pd.DataFrame(
        {
            "marca": ["SEAT", "Seat", "Kia"],
            "modelo": ["León", "León", "Ceed"],
            "anio": [2016, 2016, 2035],
            "km": ["85.000 km", "85.000 km", "10"],
            "combustible": ["Diésel", "Diésel", "Gasolina"],
            "cambio": ["Manual", "Manual", "Manual"],
            "potencia_cv": [np.nan] * 3,
            "precio": ["11.900 €", "11.900 €", "9.000 €"],
        }
    )
    limpio = limpiar(df, anio_actual=2026)
    assert len(limpio) == 1  # duplicado eliminado y año imposible fuera
    fila = limpio.iloc[0]
    assert (fila["marca"], fila["modelo"], fila["combustible"], fila["precio"]) == (
        "seat",
        "leon",
        "diesel",
        11900,
    )


def test_cargar_csv_real_latin1_con_punto_y_coma(tmp_path):
    """Mismo formato que el dataset de Zenodo: separador ';', Latin-1 y motor con 'cv'."""
    ruta = tmp_path / "coches.csv"
    contenido = (
        "brand;model;price (eur);engine;year;mileage (kms);fuel;gearbox;location\n"
        "SEAT;Ibiza;8990;SC 1.2 TSI 90cv Style;2016;67000 ;Gasolina;Manual;Granollers\n"
        "Hyundai;i30;9990;1.6 CRDi 110cv Tecno;2014;104868 ;Diésel;Manual;Viladecans\n"
    )
    ruta.write_bytes(contenido.encode("latin-1"))
    mapa = {
        "brand": "marca",
        "model": "modelo",
        "year": "anio",
        "mileage (kms)": "km",
        "fuel": "combustible",
        "gearbox": "cambio",
        "engine": "motor",
        "price (eur)": "precio",
    }
    df = limpiar(cargar(str(ruta), mapa), anio_actual=2026)
    assert len(df) == 2
    assert df["potencia_cv"].tolist() == [90, 110]
    assert df["combustible"].tolist() == ["gasolina", "diesel"]
    assert df["km"].tolist() == [67000, 104868]
