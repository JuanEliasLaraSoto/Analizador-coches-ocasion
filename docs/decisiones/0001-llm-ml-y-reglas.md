# 0001. Combinar LLM, ML clásico y reglas
Fecha: 04/10/2026
## Contexto
La app analiza anuncios de coches de ocasión: extraer datos de texto libre,
estimar si el precio es justo y comprobar cosas como la ITV o los km.
## Decisión- LLM para lo que requiere entender lenguaje: extraer la ficha y redactar el informe.- Modelo de ML (regresión) para estimar el precio de mercado a partir de datos.- Código determinista para reglas y cálculos (ITV, km/año, coste a 3 años).
## Alternativas descartadas- Pedirle todo al LLM: inventa cifras, no es reproducible y es más caro.- Solo reglas y ML: no puede leer anuncios escritos de forma libre.
## Consecuencias
Cada dato lleva su procedencia (anuncio / deducido / desconocido) y la
evaluación mide por separado cada pieza.