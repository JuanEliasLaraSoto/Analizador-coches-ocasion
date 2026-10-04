# Ficha del modelo de precio

## Qué hace
Estima el precio de mercado de un coche de ocasión y un rango donde caen ~80 % de los precios reales.

## Datos
- Dataset: (nombre, autores, enlace, licencia)
- Fecha de los datos: (p. ej. abril 2022) → los precios actuales pueden ser más altos.
- Filas tras la limpieza: (n)
- Variables: marca, modelo, año, km, combustible, cambio (y potencia si existe).

## Modelo
- HistGradientBoostingRegressor de scikit-learn sobre log(precio).
- Rango: conformal prediction con un 20 % de datos de calibración (cobertura objetivo 80 %).

## Resultados (test, 20 % de los datos)
| Modelo | MAE (€) | MAPE (%) |
|---|---|---|
| Baseline (mediana por modelo y año) | | |
| Gradient boosting | | |

Cobertura real del rango: __ %

## Limitaciones
- Dataset pequeño y de una sola zona: menos fiable en marcas o modelos poco frecuentes.
- No conoce el estado real del coche, el equipamiento ni el historial.
- Precios de la fecha del dataset.
