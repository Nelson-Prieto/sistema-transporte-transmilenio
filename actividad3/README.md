# Actividad 3 - Metodos de Aprendizaje Supervisado

Este modulo agrega un flujo sencillo de aprendizaje supervisado al proyecto de rutas:

1. Generar dataset de muestra.
2. Entrenar un modelo de regresion lineal.
3. Usar el modelo para predecir tiempo estimado de viaje.

## Archivos

- `actividad3/fuentes_datos.md`: fuentes identificadas y descripcion del dataset.
- `actividad3/generar_dataset_muestra.py`: crea el dataset sintetico.
- `actividad3/entrenar_modelo_supervisado.py`: entrena y evalua el modelo.
- `actividad3/predecir_tiempo.py`: realiza predicciones con el modelo entrenado.
- `actividad3/datos/viajes_transmilenio_muestra.csv`: datos de entrenamiento.
- `actividad3/modelos/modelo_regresion_lineal.json`: modelo entrenado.

## Ejecucion

Desde la raiz del proyecto:

```bash
python actividad3/generar_dataset_muestra.py
python actividad3/entrenar_modelo_supervisado.py
python actividad3/predecir_tiempo.py
```

## Salida esperada

- En entrenamiento: metricas de evaluacion (`MAE`, `RMSE`, `R2`) y ruta del modelo guardado.
- En prediccion: tiempo estimado de viaje en minutos para el escenario ingresado.
