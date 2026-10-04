import importlib.util
from pathlib import Path

ruta = Path(__file__).parents[1] / "evals" / "evaluar.py"
spec = importlib.util.spec_from_file_location("evaluar", ruta)
evaluar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluar)


def test_cifras_inventadas():
    datos = '{"precio": 11900, "rango_min": 9800}'
    assert evaluar.cifras_inventadas("Cuesta 11.900 € y el mínimo es 9.800 €", datos) == []
    assert evaluar.cifras_inventadas("Gasta 4.500 € al año", datos) == ["4500"]


def test_iguales_ignora_tildes_y_mayusculas():
    assert evaluar.iguales("León", "leon")
    assert not evaluar.iguales(2016, 2017)
