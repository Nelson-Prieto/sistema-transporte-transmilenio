# Actividad 4 - Metodos de Aprendizaje No Supervisado

Este modulo agrega un flujo simple de aprendizaje no supervisado para identificar patrones de operacion en el sistema de transporte.

## Archivos

- `actividad4/fuentes_datos.md`: fuentes identificadas y descripcion del dataset.
- `actividad4/generar_dataset_muestra.py`: crea el dataset sintetico para clustering.
- `actividad4/entrenar_modelo_no_supervisado.py`: entrena K-Means y resume clusters.
- `actividad4/asignar_cluster.py`: clasifica un escenario nuevo al cluster mas cercano.
- `actividad4/datos/operacion_transmilenio_muestra.csv`: datos no supervisados.
- `actividad4/modelos/modelo_kmeans.json`: modelo de clustering entrenado.

## Ejecucion

Desde la raiz del proyecto:

```bash
python actividad4/generar_dataset_muestra.py
python actividad4/entrenar_modelo_no_supervisado.py
python actividad4/asignar_cluster.py
```

## Salida esperada

- En entrenamiento:
  - Numero de clusters.
  - Inercia y silhouette score.
  - Resumen interpretable de perfiles por cluster.
- En asignacion:
  - Id de cluster del escenario ingresado.
  - Perfil operativo estimado y sugerencia de gestion.
