from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUTA_DATASET = ROOT / "actividad4" / "datos" / "operacion_transmilenio_muestra.csv"
RUTA_MODELO = ROOT / "actividad4" / "modelos" / "modelo_kmeans.json"

MAPEO_CLIMA = {"despejado": 0.0, "lluvia": 1.0, "lluvia_fuerte": 2.0}
FEATURES = [
    "hora",
    "es_hora_pico",
    "transbordo",
    "distancia_manhattan",
    "clima_cod",
    "nivel_congestion",
    "incidente",
    "demanda_estimada",
    "ocupacion_pct",
]
K_CLUSTERS = 3


# Lee el dataset no supervisado y convierte columnas a formato numerico.
def cargar_dataset(ruta_csv: Path) -> list[dict[str, float]]:
    if not ruta_csv.exists():
        raise FileNotFoundError(
            f"No existe el dataset en {ruta_csv}. Ejecuta primero actividad4/generar_dataset_muestra.py"
        )

    registros: list[dict[str, float]] = []
    with ruta_csv.open("r", newline="", encoding="utf-8") as archivo:
        reader = csv.DictReader(archivo)
        for fila in reader:
            registros.append(
                {
                    "hora": float(fila["hora"]),
                    "es_hora_pico": float(fila["es_hora_pico"]),
                    "transbordo": float(fila["transbordo"]),
                    "distancia_manhattan": float(fila["distancia_manhattan"]),
                    "clima_cod": MAPEO_CLIMA[fila["clima"]],
                    "nivel_congestion": float(fila["nivel_congestion"]),
                    "incidente": float(fila["incidente"]),
                    "demanda_estimada": float(fila["demanda_estimada"]),
                    "ocupacion_pct": float(fila["ocupacion_pct"]),
                }
            )
    return registros


# Extrae la matriz X del dataset usando el orden fijo de FEATURES.
def extraer_x(registros: list[dict[str, float]]) -> list[list[float]]:
    return [[registro[feature] for feature in FEATURES] for registro in registros]


# Calcula estadisticas de normalizacion y transforma la matriz de entrada.
def normalizar_x(x: list[list[float]]) -> tuple[list[list[float]], list[float], list[float]]:
    n_features = len(x[0])
    medias: list[float] = []
    desvios: list[float] = []

    for j in range(n_features):
        columna = [fila[j] for fila in x]
        media = sum(columna) / len(columna)
        varianza = sum((valor - media) ** 2 for valor in columna) / len(columna)
        desvio = math.sqrt(varianza) if varianza > 0 else 1.0
        medias.append(media)
        desvios.append(desvio)

    x_norm: list[list[float]] = []
    for fila in x:
        x_norm.append([(fila[j] - medias[j]) / (desvios[j] if desvios[j] != 0 else 1.0) for j in range(n_features)])

    return x_norm, medias, desvios


# Calcula distancia euclidiana cuadrada entre dos vectores.
def distancia_cuadrada(a: list[float], b: list[float]) -> float:
    return sum((a[i] - b[i]) ** 2 for i in range(len(a)))


# Inicializa centroides tomando puntos aleatorios del dataset normalizado.
def inicializar_centroides(x: list[list[float]], k: int, semilla: int = 42) -> list[list[float]]:
    random.seed(semilla)
    indices = random.sample(range(len(x)), k)
    return [x[i][:] for i in indices]


# Asigna cada punto al centroide mas cercano.
def asignar_clusters(x: list[list[float]], centroides: list[list[float]]) -> list[int]:
    asignaciones: list[int] = []
    for fila in x:
        distancias = [distancia_cuadrada(fila, centroide) for centroide in centroides]
        asignaciones.append(distancias.index(min(distancias)))
    return asignaciones


# Recalcula centroides como el promedio de los puntos asignados a cada cluster.
def recalcular_centroides(
    x: list[list[float]], asignaciones: list[int], k: int, semilla: int = 42
) -> list[list[float]]:
    random.seed(semilla)
    n_features = len(x[0])
    centroides: list[list[float]] = []

    for cluster_id in range(k):
        puntos = [x[i] for i in range(len(x)) if asignaciones[i] == cluster_id]
        if not puntos:
            centroides.append(x[random.randint(0, len(x) - 1)][:])
            continue
        centroides.append([sum(punto[j] for punto in puntos) / len(puntos) for j in range(n_features)])

    return centroides


# Calcula inercia total del modelo (suma de distancias cuadradas intra-cluster).
def calcular_inercia(x: list[list[float]], asignaciones: list[int], centroides: list[list[float]]) -> float:
    return sum(distancia_cuadrada(x[i], centroides[asignaciones[i]]) for i in range(len(x)))


# Calcula silhouette score promedio para evaluar separacion de clusters.
def calcular_silhouette(x: list[list[float]], asignaciones: list[int], k: int) -> float:
    if len(x) < 3 or k < 2:
        return 0.0

    grupos: dict[int, list[int]] = {cluster_id: [] for cluster_id in range(k)}
    for i, cluster_id in enumerate(asignaciones):
        grupos[cluster_id].append(i)

    puntajes: list[float] = []
    for i in range(len(x)):
        cluster_actual = asignaciones[i]
        propios = grupos[cluster_actual]

        if len(propios) <= 1:
            puntajes.append(0.0)
            continue

        a_i = sum(math.sqrt(distancia_cuadrada(x[i], x[j])) for j in propios if j != i) / (len(propios) - 1)

        b_i = float("inf")
        for otro_cluster in range(k):
            if otro_cluster == cluster_actual or not grupos[otro_cluster]:
                continue
            promedio = sum(
                math.sqrt(distancia_cuadrada(x[i], x[j])) for j in grupos[otro_cluster]
            ) / len(grupos[otro_cluster])
            b_i = min(b_i, promedio)

        denominador = max(a_i, b_i)
        puntajes.append((b_i - a_i) / denominador if denominador > 0 else 0.0)

    return sum(puntajes) / len(puntajes)


# Entrena K-Means con criterio de convergencia por movimiento de centroides.
def entrenar_kmeans(
    x: list[list[float]],
    k: int,
    max_iter: int = 100,
    tol: float = 1e-4,
    semilla: int = 42,
) -> tuple[list[list[float]], list[int], float, int]:
    centroides = inicializar_centroides(x, k=k, semilla=semilla)

    for iteracion in range(1, max_iter + 1):
        asignaciones = asignar_clusters(x, centroides)
        nuevos_centroides = recalcular_centroides(x, asignaciones, k=k, semilla=semilla + iteracion)

        movimiento = sum(math.sqrt(distancia_cuadrada(centroides[i], nuevos_centroides[i])) for i in range(k))
        centroides = nuevos_centroides

        if movimiento < tol:
            break

    asignaciones = asignar_clusters(x, centroides)
    inercia = calcular_inercia(x, asignaciones, centroides)
    return centroides, asignaciones, inercia, iteracion


# Devuelve el vector de centroide en escala original para interpretacion.
def desnormalizar_centroide(centroide: list[float], medias: list[float], desvios: list[float]) -> list[float]:
    return [(centroide[i] * (desvios[i] if desvios[i] != 0 else 1.0)) + medias[i] for i in range(len(centroide))]


# Asigna una etiqueta textual al cluster segun su perfil operativo promedio.
def etiquetar_cluster(perfil: dict[str, float]) -> str:
    if perfil["nivel_congestion"] >= 4.0 or perfil["incidente_rate"] >= 0.20:
        return "Operacion critica"
    if perfil["demanda_estimada"] >= 190.0 or perfil["ocupacion_pct"] >= 60.0 or perfil["es_hora_pico"] >= 0.35:
        return "Alta demanda"
    return "Flujo estable"


# Construye un resumen interpretable por cluster para reporte final.
def resumir_clusters(
    registros: list[dict[str, float]],
    asignaciones: list[int],
    k: int,
) -> list[dict[str, float | int | str]]:
    resumen: list[dict[str, float | int | str]] = []

    for cluster_id in range(k):
        puntos = [registros[i] for i in range(len(registros)) if asignaciones[i] == cluster_id]
        cantidad = len(puntos)
        if cantidad == 0:
            perfil = {
                "cluster": cluster_id,
                "cantidad": 0,
                "hora_promedio": 0.0,
                "es_hora_pico": 0.0,
                "nivel_congestion": 0.0,
                "incidente_rate": 0.0,
                "demanda_estimada": 0.0,
                "ocupacion_pct": 0.0,
                "clima_cod": 0.0,
                "transbordo_rate": 0.0,
            }
            perfil["etiqueta"] = "Sin datos"
            resumen.append(perfil)
            continue

        perfil = {
            "cluster": cluster_id,
            "cantidad": cantidad,
            "hora_promedio": sum(p["hora"] for p in puntos) / cantidad,
            "es_hora_pico": sum(p["es_hora_pico"] for p in puntos) / cantidad,
            "nivel_congestion": sum(p["nivel_congestion"] for p in puntos) / cantidad,
            "incidente_rate": sum(p["incidente"] for p in puntos) / cantidad,
            "demanda_estimada": sum(p["demanda_estimada"] for p in puntos) / cantidad,
            "ocupacion_pct": sum(p["ocupacion_pct"] for p in puntos) / cantidad,
            "clima_cod": sum(p["clima_cod"] for p in puntos) / cantidad,
            "transbordo_rate": sum(p["transbordo"] for p in puntos) / cantidad,
        }
        perfil["etiqueta"] = etiquetar_cluster(perfil)
        resumen.append(perfil)

    return resumen


# Guarda el modelo K-Means, centroides y resumen en formato JSON.
def guardar_modelo(
    ruta_modelo: Path,
    centroides_norm: list[list[float]],
    centroides_originales: list[list[float]],
    medias: list[float],
    desvios: list[float],
    resumen_clusters: list[dict[str, float | int | str]],
) -> None:
    ruta_modelo.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "algoritmo": "kmeans",
        "k": len(centroides_norm),
        "features": FEATURES,
        "centroides_norm": centroides_norm,
        "centroides_originales": centroides_originales,
        "normalizacion": {"medias": medias, "desvios": desvios},
        "mapeo_clima": MAPEO_CLIMA,
        "resumen_clusters": resumen_clusters,
    }

    with ruta_modelo.open("w", encoding="utf-8") as archivo:
        json.dump(payload, archivo, ensure_ascii=False, indent=2)


# Orquesta el flujo completo: carga de datos, clustering, evaluacion y guardado.
def main() -> None:
    registros = cargar_dataset(RUTA_DATASET)
    x = extraer_x(registros)
    x_norm, medias, desvios = normalizar_x(x)

    centroides_norm, asignaciones, inercia, iteraciones = entrenar_kmeans(
        x_norm,
        k=K_CLUSTERS,
        max_iter=120,
        tol=1e-4,
        semilla=42,
    )
    silhouette = calcular_silhouette(x_norm, asignaciones, K_CLUSTERS)
    centroides_originales = [desnormalizar_centroide(c, medias, desvios) for c in centroides_norm]
    resumen = resumir_clusters(registros, asignaciones, K_CLUSTERS)

    guardar_modelo(
        RUTA_MODELO,
        centroides_norm=centroides_norm,
        centroides_originales=centroides_originales,
        medias=medias,
        desvios=desvios,
        resumen_clusters=resumen,
    )

    print("Modelo no supervisado entrenado y guardado.")
    print(f"Dataset: {RUTA_DATASET}")
    print(f"Modelo: {RUTA_MODELO}")
    print(f"Registros: {len(registros)}")
    print(f"Clusters (k): {K_CLUSTERS}")
    print(f"Iteraciones: {iteraciones}")
    print(f"Inercia: {round(inercia, 4)}")
    print(f"Silhouette: {round(silhouette, 4)}")
    print("Resumen de clusters:")
    for perfil in resumen:
        print(
            f"- Cluster {perfil['cluster']} | {perfil['etiqueta']} | "
            f"n={perfil['cantidad']} | congestion={round(float(perfil['nivel_congestion']), 2)} | "
            f"demanda={round(float(perfil['demanda_estimada']), 2)} | "
            f"incidentes={round(float(perfil['incidente_rate']) * 100, 1)}%"
        )


if __name__ == "__main__":
    main()
