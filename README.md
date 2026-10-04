---
title: Analizador de coches de ocasión
emoji: 🚗
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Analizador de coches de ocasión

Pega uno o varios anuncios de coches de segunda mano y la app te dice si el precio es justo,
qué señales de alarma tiene, cuánto te costará en 3 años y qué preguntarle al vendedor.

**Demo:** https://huggingface.co/spaces/TU-USUARIO/analizador-coches-ocasion

## Cómo funciona

| Pieza | Técnica |
|---|---|
| Extracción del anuncio | LLM (Claude Haiku 4.5) con salida estructurada + verificación de citas contra el texto |
| Precio de mercado | Gradient boosting (scikit-learn) + rango calibrado con conformal prediction |
| Reglas (ITV, km/año, coherencia) | Python determinista con tests |
| Coste a 3 años | Consumo × precio real del carburante (API abierta del Ministerio) |
| Informe | LLM con router: Haiku para casos sencillos, Sonnet para comparar o casos dudosos |

Principio de diseño: **el LLM entiende y redacta, el ML estima, el código calcula**.
Cada dato lleva su procedencia (anuncio / deducido / desconocido) y los campos que el modelo
no puede justificar con una cita literal del anuncio se descartan.

## Resultados

_(Rellena con tus números de `scripts/entrenar_precio.py` y `evals/evaluar.py`.)_

| Métrica | Valor |
|---|---|
| Error medio del modelo de precio (MAPE) | |
| Error del baseline (MAPE) | |
| Cobertura del rango de precio | |
| Campos extraídos correctamente | |
| Alucinaciones tras verificar | |
| Coste medio por anuncio | |

## Ejecutar en local

```bash
uv sync
cp .env.example .env                   # y pon tu ANTHROPIC_API_KEY
uv run python scripts/entrenar_precio.py data/coches.csv
uv run uvicorn ocasion.api:app --reload
```

## Datos

- Precios de coches: _(nombre del dataset, autores, licencia y fecha)_.
- Precios de carburantes: datos abiertos del Ministerio (precios en estaciones de servicio).

Proyecto personal, no oficial. Los resultados son orientativos.
