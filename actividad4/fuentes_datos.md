# Fuentes de Datos para Aprendizaje No Supervisado

Este documento identifica fuentes de datos utiles para aplicar metodos no supervisados en el proyecto de transporte masivo.

## 1) Fuentes reales sugeridas (si estan disponibles)

1. Telemetria operativa por franja horaria:
- Demanda por estacion y tramo.
- Tiempos de recorrido observados.
- Nivel de ocupacion de buses.

2. Eventos operacionales:
- Incidentes, bloqueos, cierres y desvíos.
- Frecuencia de incidentes por zona y horario.

3. Condiciones externas:
- Clima por hora y zona.
- Variables de entorno que impacten la operacion.

4. Variables de red de transporte:
- Distancia entre estaciones.
- Existencia de transbordo.
- Tramos con mayor variabilidad operacional.

## 2) Dataset de muestra para Actividad 4

Como complemento academico, se incluye un dataset sintetico orientado a clustering:

- Archivo: `actividad4/datos/operacion_transmilenio_muestra.csv`
- Script generador: `actividad4/generar_dataset_muestra.py`
- Tamano por defecto: 360 registros

Variables principales incluidas:

- `hora`
- `distancia_manhattan`
- `transbordo`
- `clima`
- `nivel_congestion`
- `incidente`
- `demanda_estimada`
- `ocupacion_pct`
- `es_hora_pico`
- `tiempo_observado_min`

Estas variables permiten descubrir patrones de operacion sin variable objetivo (clusters de comportamiento operativo).
