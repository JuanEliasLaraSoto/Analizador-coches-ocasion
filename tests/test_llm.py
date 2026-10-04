"""Tests del cambio de proveedor con un Gemini falso: sin internet y sin clave."""

import base64
from types import SimpleNamespace as N

import pytest

from ocasion import llm
from ocasion.ficha import FichaExtraida


class GeminiFalso:
    def __init__(self, texto):
        self.texto, self.peticiones = texto, []
        self.models = self  # para poder llamar a cliente.models.generate_content(...)

    def generate_content(self, model, contents, config):
        self.peticiones.append((model, contents, config))
        uso = N(prompt_token_count=900, candidates_token_count=100, thoughts_token_count=50)
        return N(text=self.texto, usage_metadata=uso)


@pytest.fixture
def gemini(monkeypatch):
    falso = GeminiFalso('{"marca": "Seat", "modelo": "León", "anio": 2016, "citas": []}')
    monkeypatch.setattr(llm, "PROVEEDOR", "gemini")
    monkeypatch.setattr(llm, "_cliente_gemini", falso)
    return falso


def test_gemini_devuelve_el_mismo_objeto_que_claude(gemini):
    ficha, ll = llm.parse("extraccion", llm.HAIKU, "system", "anuncio", FichaExtraida)
    assert isinstance(ficha, FichaExtraida) and ficha.marca == "Seat" and ficha.km is None
    modelo, contenido, config = gemini.peticiones[0]
    assert modelo == llm.GEMINI[llm.HAIKU]  # el modelo «rápido» se traduce al de Google
    assert config.system_instruction == "system"
    assert config.response_schema is FichaExtraida
    assert (ll.modelo, ll.tokens_entrada, ll.tokens_salida) == (modelo, 900, 150)
    assert ll.coste_usd == 0  # plan gratuito


def test_gemini_recibe_las_imagenes(gemini):
    imagen = base64.standard_b64encode(b"bytes-de-imagen").decode()
    contenido = [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": imagen}},
        {"type": "text", "text": "Extrae la ficha"},
    ]
    llm.parse("extraccion_imagen", llm.HAIKU, "system", contenido, FichaExtraida)
    partes = gemini.peticiones[0][1]
    assert partes[0].inline_data.data == b"bytes-de-imagen"
    assert partes[0].inline_data.mime_type == "image/png"
    assert partes[1].text == "Extrae la ficha"


def test_json_que_no_encaja_da_error(gemini):
    gemini.texto = '{"anio": "no es un año"}'
    with pytest.raises(ValueError):
        llm.parse("extraccion", llm.HAIKU, "system", "anuncio", FichaExtraida)
