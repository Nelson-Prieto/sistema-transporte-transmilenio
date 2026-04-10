from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUTA_DATASET = ROOT / "actividad3" / "datos" / "viajes_transmilenio_muestra.csv"
RUTA_MODELO = ROOT / "actividad3" / "modelos" / "modelo_regresion_lineal.json"

MAPEO_CLIMA = {"despejado": 0.0, "lluvia": 1.0, "lluvia_fuerte": 2.0}
FEATURES = [
    "tiempo_base_min",
    "transbordo",
    "distancia_manhattan",
    "hora",
    "es_hora_pico",
    "clima_cod",
    "nivel_congestion",
    "incidente",
    "demanda_estimada",
]
TARGET = "tiempo_real_min"

# Lee el dataset CSV y convierte columnas a formato numerico utilizable.
def cargar_dataset(ruta_csv: Path) -> list[dict[str, float]]:
    if not ruta_csv.exists():
        raise FileNotFoundError(f"No existe el dataset: {ruta_csv}")

    registros: list[dict[str, float]] = []
    with ruta_csv.open("r", newline="", encoding="utf-8") as archivo:
        reader = csv.DictReader(archivo)
        for fila in reader:
            registros.append(
                {
                    "tiempo_base_min": float(fila["tiempo_base_min"]),
                    "transbordo": float(fila["transbordo"]),
                    "distancia_manhattan": float(fila["distancia_manhattan"]),
                    "hora": float(fila["hora"]),
                    "es_hora_pico": float(fila["es_hora_pico"]),
                    "clima_cod": MAPEO_CLIMA[fila["clima"]],
                    "nivel_congestion": float(fila["nivel_congestion"]),
                    "incidente": float(fila["incidente"]),
                    "demanda_estimada": float(fila["demanda_estimada"]),
                    TARGET: float(fila[TARGET]),
                }
            )
    return registros


# Divide registros en entrenamiento y prueba con mezcla aleatoria reproducible.
def separar_train_test(
    registros: list[dict[str, float]],
    test_ratio: float = 0.2,
    semilla: int = 42,
) -> tuple[list[dict[str, float]], list[dict[str, float]]]:
    datos = registros[:]
    random.Random(semilla).shuffle(datos)
    corte = int(len(datos) * (1 - test_ratio))
    return datos[:corte], datos[corte:]


# Separa las variables de entrada (X) y la variable objetivo (y).
def extraer_xy(registros: list[dict[str, float]]) -> tuple[list[list[float]], list[float]]:
    x = [[registro[feature] for feature in FEATURES] for registro in registros]
    y = [registro[TARGET] for registro in registros]
    return x, y


# Normaliza train/test con estadisticas calculadas solo desde train.
def normalizar_train_test(
    x_train: list[list[float]],
    x_test: list[list[float]],
) -> tuple[list[list[float]], list[list[float]], list[float], list[float]]:
    n_features = len(x_train[0])
    medias: list[float] = []
    desvios: list[float] = []

    for j in range(n_features):
        columna = [fila[j] for fila in x_train]
        media = sum(columna) / len(columna)
        varianza = sum((valor - media) ** 2 for valor in columna) / len(columna)
        desvio = math.sqrt(varianza) if varianza > 0 else 1.0
        medias.append(media)
        desvios.append(desvio)

    # Aplica la normalizacion estandar fila por fila.
    def normalizar(x: list[list[float]]) -> list[list[float]]:
        salida: list[list[float]] = []
        for fila in x:
            salida.append(
                [(fila[j] - medias[j]) / (desvios[j] if desvios[j] != 0 else 1.0) for j in range(n_features)]
            )
        return salida

    return normalizar(x_train), normalizar(x_test), medias, desvios


# Entrena una regresion lineal usando descenso de gradiente batch.
def entrenar_regresion_lineal(
    x_train: list[list[float]],
    y_train: list[float],
    lr: float = 0.01,
    epochs: int = 4000,
) -> list[float]:
    n_muestras = len(x_train)
    n_features = len(x_train[0])
    pesos = [0.0] * (n_features + 1)

    for _ in range(epochs):
        gradientes = [0.0] * (n_features + 1)
        for i in range(n_muestras):
            pred = pesos[0] + sum(pesos[j + 1] * x_train[i][j] for j in range(n_features))
            error = pred - y_train[i]
            gradientes[0] += error
            for j in range(n_features):
                gradientes[j + 1] += error * x_train[i][j]

        factor = 2.0 / n_muestras
        for j in range(n_features + 1):
            pesos[j] -= lr * factor * gradientes[j]

    return pesos


# Genera predicciones para una matriz de entrada X dada.
def predecir(x: list[list[float]], pesos: list[float]) -> list[float]:
    n_features = len(x[0])
    predicciones: list[float] = []
    for fila in x:
        pred = pesos[0] + sum(pesos[j + 1] * fila[j] for j in range(n_features))
        predicciones.append(pred)
    return predicciones


# Calcula metricas de evaluacion de regresion: MAE, RMSE y R2.
def calcular_metricas(y_real: list[float], y_pred: list[float]) -> dict[str, float]:
    n = len(y_real)
    mae = sum(abs(y_real[i] - y_pred[i]) for i in range(n)) / n
    rmse = math.sqrt(sum((y_real[i] - y_pred[i]) ** 2 for i in range(n)) / n)
    media_real = sum(y_real) / n
    ss_tot = sum((valor - media_real) ** 2 for valor in y_real)
    ss_res = sum((y_real[i] - y_pred[i]) ** 2 for i in range(n))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
    return {"mae": round(mae, 4), "rmse": round(rmse, 4), "r2": round(r2, 4)}


# Guarda en JSON los pesos del modelo y parametros de normalizacion.
def guardar_modelo(ruta_modelo: Path, pesos: list[float], medias: list[float], desvios: list[float]) -> None:
    ruta_modelo.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "algoritmo": "regresion_lineal_descenso_gradiente",
        "features": FEATURES,
        "target": TARGET,
        "pesos": pesos,
        "normalizacion": {"medias": medias, "desvios": desvios},
        "mapeo_clima": MAPEO_CLIMA,
    }
    with ruta_modelo.open("w", encoding="utf-8") as archivo:
        json.dump(payload, archivo, ensure_ascii=False, indent=2)


# Orquesta el flujo completo: carga, entrenamiento, evaluacion y guardado.
def main() -> None:
    registros = cargar_dataset(RUTA_DATASET)
    train, test = separar_train_test(registros, test_ratio=0.2, semilla=42)

    x_train, y_train = extraer_xy(train)
    x_test, y_test = extraer_xy(test)
    x_train_norm, x_test_norm, medias, desvios = normalizar_train_test(x_train, x_test)

    pesos = entrenar_regresion_lineal(x_train_norm, y_train, lr=0.01, epochs=4000)
    y_pred = predecir(x_test_norm, pesos)
    metricas = calcular_metricas(y_test, y_pred)

    guardar_modelo(RUTA_MODELO, pesos, medias, desvios)

    print("Modelo entrenado y guardado.")
    print(f"Dataset: {RUTA_DATASET}")
    print(f"Modelo: {RUTA_MODELO}")
    print(f"Registros train: {len(train)}")
    print(f"Registros test: {len(test)}")
    print("Metricas en test:")
    print(f"- MAE:  {metricas['mae']}")
    print(f"- RMSE: {metricas['rmse']}")
    print(f"- R2:   {metricas['r2']}")


if __name__ == "__main__":
    main()
