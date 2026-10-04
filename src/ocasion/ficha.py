"""Esquema de la ficha de un coche extraída de un anuncio.

Regla de oro: si el anuncio no dice algo, el campo queda en None.
La procedencia de cada dato se calcula en código, no la decide el LLM.
"""

from typing import Literal

from pydantic import BaseModel, Field

Combustible = Literal[
    "gasolina", "diesel", "hibrido", "hibrido_enchufable", "electrico", "glp", "gnc"
]
Cambio = Literal["manual", "automatico"]
Vendedor = Literal["particular", "profesional"]


class Cita(BaseModel):
    """Fragmento literal del anuncio que justifica un campo."""

    campo: str = Field(description="Nombre del campo de la ficha, p. ej. 'km'")
    texto: str = Field(description="Texto copiado literalmente del anuncio")


class FichaExtraida(BaseModel):
    """Lo que el LLM devuelve. Todo opcional: None significa 'el anuncio no lo dice'."""

    marca: str | None = None
    modelo: str | None = None
    version: str | None = Field(None, description="Motor o acabado, p. ej. '1.6 TDI Style'")
    anio: int | None = Field(None, description="Año de matriculación")
    km: int | None = None
    precio: int | None = Field(None, description="Precio en euros")
    combustible: Combustible | None = None
    cambio: Cambio | None = None
    potencia_cv: int | None = None
    num_duenos: int | None = None
    itv_hasta: str | None = Field(None, description="Fecha de validez de la ITV tal como aparece")
    libro_revisiones: bool | None = None
    tipo_vendedor: Vendedor | None = None
    provincia: str | None = None
    citas: list[Cita] = Field(
        default_factory=list, description="Una cita literal por cada campo rellenado"
    )


Procedencia = Literal["anuncio", "deducido", "desconocido"]

CAMPOS_FICHA = [c for c in FichaExtraida.model_fields if c != "citas"]


def procedencias(ficha: FichaExtraida) -> dict[str, Procedencia]:
    """Para cada campo: 'anuncio' si tiene valor, 'desconocido' si no."""
    return {
        c: ("anuncio" if getattr(ficha, c) is not None else "desconocido") for c in CAMPOS_FICHA
    }
