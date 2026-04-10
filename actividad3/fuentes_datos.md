# Fuentes de Datos para Aprendizaje Supervisado

Este documento identifica fuentes de datos utiles para modelos supervisados en el proyecto de transporte masivo.

## 1) Fuentes reales sugeridas (si estan disponibles)

1. Datos operacionales por tramo:
- Tiempo real entre estaciones por franja horaria.
- Variable objetivo sugerida: `tiempo_real_min`.
- Variables explicativas sugeridas: hora, dia, clima, incidentes, congestion.

2. Datos de demanda de usuarios:
- Entradas/salidas por estacion y hora.
- Variable derivada sugerida: `demanda_estimada`.

3. Datos de incidentes en via o estacion:
- Reportes de bloqueos, accidentes o cierres temporales.
- Variable sugerida: `incidente` (0/1) o severidad.

4. Datos de clima:
- Lluvia e intensidad por zona y hora.
- Variable sugerida: `clima` o categoria de lluvia.

## 2) Dataset de muestra generado para la Actividad 3

Como complemento academico, este proyecto incluye un dataset sintetico:

- Archivo: `actividad3/datos/viajes_transmilenio_muestra.csv`
- Script generador: `actividad3/generar_dataset_muestra.py`
- Tamano por defecto: 300 registros

Columnas del dataset:

- `fecha`: fecha del viaje
- `hora`: hora del viaje (0-23)
- `origen`: estacion de salida
- `destino`: estacion de llegada
- `tiempo_base_min`: tiempo base del tramo
- `transbordo`: 0/1 si hay cambio de linea
- `distancia_manhattan`: distancia aproximada entre estaciones
- `clima`: despejado, lluvia o lluvia_fuerte
- `nivel_congestion`: escala 1-5
- `incidente`: 0/1
- `demanda_estimada`: aproximacion de usuarios
- `es_hora_pico`: 0/1
- `tiempo_real_min`: tiempo observado/simulado (target)

Este dataset permite practicar el ciclo completo de aprendizaje supervisado aun cuando no se tenga acceso directo a datos historicos institucionales.
