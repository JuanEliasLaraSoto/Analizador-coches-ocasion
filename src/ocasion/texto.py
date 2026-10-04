"""Utilidades de texto."""

import unicodedata


def normalizar(texto: str) -> str:
    """'  Málaga ' -> 'malaga': minúsculas, sin tildes y sin espacios sobrantes."""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_tildes.lower().strip()
