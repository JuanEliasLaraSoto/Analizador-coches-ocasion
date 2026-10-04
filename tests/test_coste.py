import pytest

from ocasion.coste import coste_total


def test_coste_diesel_calculado_a_mano():
    c = coste_total(
        precio=10_000,
        combustible="diesel",
        km_coche=100_000,
        km_anuales=10_000,
        precio_litro=1.5,
        anios=3,
    )
    # 10.000 km/año * 5,2 L/100 km * 1,5 €/L = 780 €/año -> 2.340 € en 3 años
    assert c.energia == pytest.approx(2340)
    # 350 + 100.000/10.000 * 40 = 750 €/año -> 2.250 €
    assert c.mantenimiento == pytest.approx(2250)
    assert c.total == pytest.approx(10_000 + 2340 + 1350 + 2250)


def test_electrico_no_usa_precio_litro():
    a = coste_total(20_000, "electrico", 0, 10_000, precio_litro=1.0)
    b = coste_total(20_000, "electrico", 0, 10_000, precio_litro=9.9)
    assert a.energia == b.energia
