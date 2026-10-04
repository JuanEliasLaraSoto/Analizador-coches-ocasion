from ocasion.extraccion import quitar_datos_personales, verificar_citas
from ocasion.ficha import Cita, FichaExtraida, procedencias

ANUNCIO = "Vendo Seat León 1.6 TDI del 2016, 85.000 km. 11.900 €. Llamar al 612 345 678"


def test_quita_telefono_y_email():
    limpio = quitar_datos_personales("Llamar al 612 345 678 o pepe@correo.com")
    assert "612" not in limpio and "@" not in limpio


def test_no_borra_precios_ni_km():
    texto = "85.000 km, 11.900 €"
    assert quitar_datos_personales(texto) == texto


def test_campo_sin_cita_se_descarta():
    ficha = FichaExtraida(
        marca="Seat",
        km=85000,
        num_duenos=1,  # num_duenos no aparece en el anuncio
        citas=[
            Cita(campo="marca", texto="Seat"),
            Cita(campo="km", texto="85.000 km"),
            Cita(campo="num_duenos", texto="único dueño"),
        ],
    )
    verificada, descartados = verificar_citas(ficha, ANUNCIO)
    assert verificada.marca == "Seat" and verificada.km == 85000
    assert verificada.num_duenos is None
    assert descartados == ["num_duenos"]


def test_procedencias():
    proc = procedencias(FichaExtraida(marca="Seat"))
    assert proc["marca"] == "anuncio" and proc["km"] == "desconocido"
