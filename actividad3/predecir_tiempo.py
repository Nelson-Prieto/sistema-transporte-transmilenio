from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUTA_MODELO = ROOT / "actividad3" / "modelos" / "modelo_regresion_lineal.json"

# Carga desde disco el modelo entrenado en formato JSON.
def cargar_modelo(ruta_modelo: Path) -> dict:
    if not ruta_modelo.exists():
        raise FileNotFoundError(
            f"No existe el modelo entrenado en {ruta_modelo}. "
            "Primero ejecuta entrenar_modelo_supervisado.py"
        )
    with ruta_modelo.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)

# Aplica normalizacion estandar usando medias y desvios del entrenamiento.
def normalizar_vector(vector: list[float], medias: list[float], desvios: list[float]) -> list[float]:
    normalizado: list[float] = []
    for i, valor in enumerate(vector):
        desvio = desvios[i] if desvios[i] != 0 else 1.0
        normalizado.append((valor - medias[i]) / desvio)
    return normalizado


# Calcula la prediccion final en minutos con los pesos de la regresion lineal.
def predecir_tiempo(modelo: dict, vector: list[float]) -> float:
    pesos = modelo["pesos"]
    pred = pesos[0] + sum(pesos[i + 1] * vector[i] for i in range(len(vector)))
    return round(pred, 2)


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


# Orquesta la captura de datos, prepara el vector y muestra la prediccion.
def main() -> None:
    print("Ingresa los parametros para estimar el tiempo de viaje:")
    tiempo_base = pedir_float("Tiempo base entre estaciones (min)", minimo=0.0)
    transbordo = pedir_si_no("Hay transbordo")
    distancia = pedir_float("Distancia Manhattan entre estaciones", minimo=0.0)
    hora = pedir_entero("Hora del viaje (0-23)", minimo=0, maximo=23)
    hora_pico = pedir_si_no("Es hora pico")
    clima = pedir_clima()
    congestion = pedir_float("Nivel de congestion (1-5)", minimo=1.0, maximo=5.0)
    incidente = pedir_si_no("Hay incidente reportado")
    demanda = pedir_float("Demanda estimada de usuarios", minimo=0.0)

    modelo = cargar_modelo(RUTA_MODELO)

    clima_cod = modelo["mapeo_clima"][clima]
    vector = [
        float(tiempo_base),
        float(transbordo),
        float(distancia),
        float(hora),
        float(hora_pico),
        float(clima_cod),
        float(congestion),
        float(incidente),
        float(demanda),
    ]

    medias = modelo["normalizacion"]["medias"]
    desvios = modelo["normalizacion"]["desvios"]
    vector_norm = normalizar_vector(vector, medias, desvios)
    pred = predecir_tiempo(modelo, vector_norm)

    print(f"Tiempo estimado de viaje: {pred} minutos")


if __name__ == "__main__":
    main()
