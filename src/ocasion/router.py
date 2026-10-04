"""Elige el modelo más barato que sirve para cada tarea."""

from ocasion import llm


def modelo_informe(analisis: list[dict], estrategia: str = "router") -> str:
    """Devuelve el modelo para el informe.

    'router' decide según la dificultad; 'haiku' y 'sonnet' fuerzan uno (para comparar).
    """
    if estrategia == "haiku":
        return llm.HAIKU
    if estrategia == "sonnet":
        return llm.SONNET
    varios_anuncios = len(analisis) > 1
    alertas_graves = any(a["nivel"] == "grave" for x in analisis for a in x["alertas"])
    muchos_desconocidos = any(
        sum(p == "desconocido" for p in x["procedencia"].values()) > 8 for x in analisis
    )
    # Comparar, casos con señales graves o anuncios muy incompletos: modelo potente.
    if varios_anuncios or alertas_graves or muchos_desconocidos:
        return llm.SONNET
    return llm.HAIKU
