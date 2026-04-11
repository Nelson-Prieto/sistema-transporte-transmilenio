from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUTA_MODELO = ROOT / "actividad4" / "modelos" / "modelo_kmeans.json"


# Marca si una hora cae en franja pico del sistema.
def es_hora_pico(hora: int) -> int:
    return int((6 <= hora <= 9) or (17 <= hora <= 20))


# Carga desde disco el modelo de clustering entrenado.
def cargar_modelo(ruta_modelo: Path) -> dict:
    if not ruta_modelo.exists():
        raise FileNotFoundError(
            f"No existe el modelo entrenado en {ruta_modelo}. "
            "Primero ejecuta actividad4/entrenar_modelo_no_supervisado.py"
        )
    with ruta_modelo.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


# Solicita un numero decimal por consola y valida rango opcional.
def pedir_float(mensaje: str, minimo: float | None = None, maximo: float | None = None) -> float:
    while True:
        valor_str = input(f"{mensaje}: ").strip().replace(",", ".")
        try:
            valor = float(valor_str)
        except ValueError:
            print("Valor invalido. Ingresa un numero.")
            continue

        if minimo is not None and valor < minimo:
            print(f"El valor debe ser mayor o igual a {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"El valor debe ser menor o igual a {maximo}.")
            continue
        return valor


# Solicita un numero entero por consola y valida rango opcional.
def pedir_entero(mensaje: str, minimo: int | None = None, maximo: int | None = None) -> int:
    while True:
        valor_str = input(f"{mensaje}: ").strip()
        try:
            valor = int(valor_str)
        except ValueError:
            print("Valor invalido. Ingresa un numero entero.")
            continue

        if minimo is not None and valor < minimo:
            print(f"El valor debe ser mayor o igual a {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"El valor debe ser menor o igual a {maximo}.")
            continue
        return valor


# Solicita una respuesta Si/No y la transforma a 1 o 0.
def pedir_si_no(mensaje: str) -> int:
    opciones_si = {"si", "s", "yes", "y"}
    opciones_no = {"no", "n"}
    while True:
        valor = input(f"{mensaje} (Si/No): ").strip().lower()
        if valor in opciones_si:
            return 1
        if valor in opciones_no:
            return 0
        print("Valor invalido. Responde Si o No.")


# Solicita el clima y valida que sea una categoria permitida.
def pedir_clima() -> str:
    opciones = {"despejado", "lluvia", "lluvia_fuerte"}
    while True:
        clima = input("Clima (despejado/lluvia/lluvia_fuerte): ").strip().lower()
        if clima in opciones:
            return clima
        print("Clima invalido. Usa: despejado, lluvia o lluvia_fuerte.")


# Aplica normalizacion estandar usando medias y desvios del entrenamiento.
def normalizar_vector(vector: list[float], medias: list[float], desvios: list[float]) -> list[float]:
    return [(vector[i] - medias[i]) / (desvios[i] if desvios[i] != 0 else 1.0) for i in range(len(vector))]


# Calcula distancia euclidiana cuadrada entre dos vectores.
def distancia_cuadrada(a: list[float], b: list[float]) -> float:
    return sum((a[i] - b[i]) ** 2 for i in range(len(a)))


# Devuelve el indice del cluster mas cercano para un nuevo vector normalizado.
def cluster_mas_cercano(vector_norm: list[float], centroides_norm: list[list[float]]) -> int:
    distancias = [distancia_cuadrada(vector_norm, centroide) for centroide in centroides_norm]
    return distancias.index(min(distancias))


# Busca la etiqueta descriptiva de un cluster dentro del resumen del modelo.
def obtener_etiqueta_cluster(modelo: dict, cluster_id: int) -> str:
    for perfil in modelo.get("resumen_clusters", []):
        if int(perfil.get("cluster", -1)) == cluster_id:
            return str(perfil.get("etiqueta", "Cluster sin etiqueta"))
    return "Cluster sin etiqueta"


# Orquesta la captura de datos, asigna cluster y muestra la interpretacion.
def main() -> None:
    modelo = cargar_modelo(RUTA_MODELO)

    print("Ingresa los parametros para clasificar el escenario operativo:")
    hora = pedir_entero("Hora del viaje (0-23)", minimo=0, maximo=23)
    transbordo = pedir_si_no("Hay transbordo")
    distancia = pedir_float("Distancia Manhattan entre estaciones", minimo=0.0)
    clima = pedir_clima()
    congestion = pedir_float("Nivel de congestion (1-5)", minimo=1.0, maximo=5.0)
    incidente = pedir_si_no("Hay incidente reportado")
    demanda = pedir_float("Demanda estimada de usuarios", minimo=0.0)
    ocupacion = pedir_float("Ocupacion estimada del bus (%)", minimo=0.0, maximo=100.0)

    clima_cod = modelo["mapeo_clima"][clima]
    vector = [
        float(hora),
        float(es_hora_pico(hora)),
        float(transbordo),
        float(distancia),
        float(clima_cod),
        float(congestion),
        float(incidente),
        float(demanda),
        float(ocupacion),
    ]

    medias = modelo["normalizacion"]["medias"]
    desvios = modelo["normalizacion"]["desvios"]
    vector_norm = normalizar_vector(vector, medias, desvios)

    cluster_id = cluster_mas_cercano(vector_norm, modelo["centroides_norm"])
    etiqueta = obtener_etiqueta_cluster(modelo, cluster_id)

    print(f"Cluster asignado: {cluster_id}")
    print(f"Perfil operativo estimado: {etiqueta}")

    if etiqueta == "Operacion critica":
        print("Sugerencia: priorizar monitoreo, control de incidentes y ajuste de frecuencias.")
    elif etiqueta == "Alta demanda":
        print("Sugerencia: reforzar capacidad en horas pico y gestionar aforo en estaciones.")
    else:
        print("Sugerencia: mantener plan operativo base y monitoreo preventivo.")


if __name__ == "__main__":
    main()
