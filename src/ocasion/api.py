"""API web con FastAPI."""

import logging
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ocasion.analizar import analizar

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Analizador de coches de ocasión")
WEB = Path("web/index.html")  # rutas relativas a la raíz del proyecto

LIMITE_POR_HORA = 20
MAX_IMAGEN_BYTES = 5 * 1024 * 1024
TIPOS_IMAGEN = {"image/png", "image/jpeg", "image/webp"}
_peticiones: dict[str, deque] = defaultdict(deque)


def comprobar_limite(ip: str) -> None:
    """Máximo LIMITE_POR_HORA análisis por IP y hora, para proteger el saldo de la API."""
    ahora = time.time()
    cola = _peticiones[ip]
    while cola and ahora - cola[0] > 3600:
        cola.popleft()
    if len(cola) >= LIMITE_POR_HORA:
        raise HTTPException(429, "Has llegado al límite de análisis por hora. Prueba más tarde.")
    cola.append(ahora)


class Peticion(BaseModel):
    anuncios: list[str] = Field(min_length=1, max_length=3)
    km_anuales: int = Field(15_000, ge=1_000, le=100_000)
    provincia: str = "Malaga"


@app.get("/health")
def health():
    return {"estado": "ok"}


@app.get("/")
def portada():
    return FileResponse(WEB)


@app.post("/analizar")
def analizar_texto(peticion: Peticion, request: Request):
    comprobar_limite(request.client.host if request.client else "desconocida")
    if any(len(a) > 6000 for a in peticion.anuncios):
        raise HTTPException(422, "Cada anuncio puede tener como máximo 6000 caracteres.")
    return analizar(peticion.anuncios, peticion.km_anuales, peticion.provincia)


@app.post("/analizar-imagen")
async def analizar_imagen(
    request: Request,
    imagen: UploadFile = File(...),
    km_anuales: int = Form(15_000),
    provincia: str = Form("Malaga"),
):
    comprobar_limite(request.client.host if request.client else "desconocida")
    if imagen.content_type not in TIPOS_IMAGEN:
        raise HTTPException(415, "Sube una imagen PNG, JPG o WEBP.")
    datos = await imagen.read()
    if len(datos) > MAX_IMAGEN_BYTES:
        raise HTTPException(413, "La imagen no puede superar 5 MB.")
    return analizar([], km_anuales, provincia, imagenes=[(datos, imagen.content_type)])
