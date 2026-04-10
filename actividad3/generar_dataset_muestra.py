from __future__ import annotations

import csv
import random
import sys
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from datos_transmilenio import obtener_conexiones, obtener_estaciones
from conocimiento import BaseConocimiento
from reglas import Reglas

# Calcula distancia Manhattan entre dos coordenadas.
def manhattan(coord_a: tuple[int, int], coord_b: tuple[int, int]) -> int:
    return abs(coord_a[0] - coord_b[0]) + abs(coord_a[1] - coord_b[1])


# Marca si una hora cae en franja pico del sistema.
def es_hora_pico(hora: int) -> int:
    return int((6 <= hora <= 9) or (17 <= hora <= 20))


# Selecciona un estado de clima usando probabilidades simples.
def clima_del_dia() -> str:
    return random.choices(
        population=["despejado", "lluvia", "lluvia_fuerte"],
        weights=[0.65, 0.25, 0.10],
        k=1,
    )[0]


# Construye un registro sintetico de viaje con variables explicativas y target.
def generar_registro(conocimiento: BaseConocimiento, reglas: Reglas, conexiones: list[tuple[str, str, int]], fecha_base: date) -> dict[str, str | int | float]:
    origen, destino, tiempo_base = random.choice(conexiones)

    fecha = fecha_base + timedelta(days=random.randint(0, 29))
    hora = random.randint(5, 22)
    clima = clima_del_dia()

    clima_extra = {"despejado": 0.0, "lluvia": 2.0, "lluvia_fuerte": 4.0}[clima]
    pico = es_hora_pico(hora)
    incidente_prob = 0.03 + (0.06 if pico else 0.0) + (0.06 if clima == "lluvia_fuerte" else 0.0)
    incidente = int(random.random() < incidente_prob)

    coord_origen = conocimiento.obtener_coord(origen)
    coord_destino = conocimiento.obtener_coord(destino)
    distancia = manhattan(coord_origen, coord_destino)
    transbordo = int(reglas.requiere_transbordo(origen, destino))

    congestion_base = random.randint(1, 3)
    congestion = min(5, congestion_base + pico + int(clima != "despejado"))

    demanda_base = random.randint(60, 130)
    demanda = demanda_base + (80 if pico else 0) + (congestion * 25)

    ruido = random.uniform(-1.2, 1.2)
    tiempo_real = (
        tiempo_base
        + (4.0 if transbordo else 0.0)
        + (0.8 * distancia)
        + (1.2 * congestion)
        + clima_extra
        + (6.0 if incidente else 0.0)
        + (1.5 if pico else 0.0)
        + ruido
    )
    tiempo_real = round(max(float(tiempo_base), tiempo_real), 2)

    return {
        "fecha": fecha.isoformat(),
        "hora": hora,
        "origen": origen,
        "destino": destino,
        "tiempo_base_min": tiempo_base,
        "transbordo": transbordo,
        "distancia_manhattan": distancia,
        "clima": clima,
        "nivel_congestion": congestion,
        "incidente": incidente,
        "demanda_estimada": demanda,
        "es_hora_pico": pico,
        "tiempo_real_min": tiempo_real,
    }


# Genera el CSV completo del dataset de muestra con semilla reproducible.
def generar_dataset(ruta_salida: Path, cantidad: int = 300, semilla: int = 42) -> None:
    random.seed(semilla)

    estaciones = obtener_estaciones()
    conexiones = obtener_conexiones()
    conocimiento = BaseConocimiento(estaciones, conexiones)
    reglas = Reglas(conocimiento)

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    fecha_base = date(2026, 3, 1)

    columnas = [
        "fecha",
        "hora",
        "origen",
        "destino",
        "tiempo_base_min",
        "transbordo",
        "distancia_manhattan",
        "clima",
        "nivel_congestion",
        "incidente",
        "demanda_estimada",
        "es_hora_pico",
        "tiempo_real_min",
    ]

    with ruta_salida.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        writer.writeheader()
        for _ in range(cantidad):
            writer.writerow(generar_registro(conocimiento, reglas, conexiones, fecha_base))

    print(f"Dataset generado en: {ruta_salida}")
    print(f"Registros: {cantidad}")


if __name__ == "__main__":
    salida = ROOT / "actividad3" / "datos" / "viajes_transmilenio_muestra.csv"
    generar_dataset(salida, cantidad=300, semilla=42)
