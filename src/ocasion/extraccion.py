"""Anuncio (texto o imagen) -> ficha estructurada, con control de alucinaciones."""

import base64
import re

from ocasion import llm
from ocasion.ficha import CAMPOS_FICHA, FichaExtraida

SYSTEM = """Eres un extractor de datos de anuncios de coches de segunda mano en España.
Rellena la ficha SOLO con información que aparezca explícitamente en el anuncio.
Reglas:
- Si un dato no aparece, déjalo en null. Nunca lo deduzcas ni lo inventes.
- Por cada campo que rellenes, añade una cita con el texto copiado literalmente del anuncio.
- Normaliza: precio en euros como entero (11.900 € -> 11900), km como entero, año con 4 cifras.
- combustible: TDI/TDCI/HDI/dCi/CRDi/diésel -> "diesel"; TSI/TFSI/gasolina -> "gasolina".
- Ignora teléfonos, nombres y cualquier dato personal."""

MAX_CARACTERES = 6000
_TELEFONO = re.compile(r"(\+34[\s-]?)?[6789]\d{2}[\s.-]?\d{3}[\s.-]?\d{3}")
_EMAIL = re.compile(r"\S+@\S+\.\S+")


def quitar_datos_personales(texto: str) -> str:
    """Borra teléfonos y emails antes de enviar el texto a ningún sitio."""
    return _EMAIL.sub("[email]", _TELEFONO.sub("[teléfono]", texto))


def _normalizar(t: str) -> str:
    return re.sub(r"\s+", " ", t.lower()).strip()


def verificar_citas(ficha: FichaExtraida, anuncio: str) -> tuple[FichaExtraida, list[str]]:
    """Anula los campos cuya cita no aparece literalmente en el anuncio.

    Es la red de seguridad contra alucinaciones: si el modelo no puede señalar
    dónde lo dice el anuncio, el dato no se acepta.
    """
    texto = _normalizar(anuncio)
    citados = {c.campo for c in ficha.citas if _normalizar(c.texto) in texto}
    descartados = []
    datos = ficha.model_dump()
    for campo in CAMPOS_FICHA:
        if datos[campo] is not None and campo not in citados:
            datos[campo] = None
            descartados.append(campo)
    datos["citas"] = [c for c in ficha.citas if c.campo in citados]
    return FichaExtraida.model_validate(datos), descartados


def extraer_de_texto(anuncio: str, modelo: str = llm.HAIKU):
    """Devuelve (ficha verificada, campos descartados, llamada)."""
    anuncio = quitar_datos_personales(anuncio[:MAX_CARACTERES])
    ficha, llamada = llm.parse(
        "extraccion", modelo, SYSTEM, f"<anuncio>\n{anuncio}\n</anuncio>", FichaExtraida
    )
    ficha, descartados = verificar_citas(ficha, anuncio)
    return ficha, descartados, llamada


def extraer_de_imagen(imagen: bytes, tipo_mime: str, modelo: str = llm.HAIKU):
    """Igual que extraer_de_texto, pero con una captura del anuncio.

    Con imágenes no se pueden verificar las citas contra el texto, así que se avisa en el informe.
    """
    contenido = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": tipo_mime,
                "data": base64.standard_b64encode(imagen).decode(),
            },
        },
        {"type": "text", "text": "Extrae la ficha de este anuncio."},
    ]
    ficha, llamada = llm.parse("extraccion_imagen", modelo, SYSTEM, contenido, FichaExtraida)
    return ficha, [], llamada
