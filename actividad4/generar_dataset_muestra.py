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


# Genera condiciones de operacion para un escenario de demanda/congestion.
def generar_escenario() -> dict[str, int | float | str]:
    escenario = random.choices(
        population=["estable", "alta_demanda", "critico"],
        weights=[0.50, 0.35, 0.15],
        k=1,
    )[0]

    if escenario == "estable":
        hora = random.randint(10, 16)
        clima = random.choices(["despejado", "lluvia"], weights=[0.85, 0.15], k=1)[0]
        congestion = random.randint(1, 3)
        incidente = int(random.random() < 0.02)
        demanda = random.randint(90, 180)
    elif escenario == "alta_demanda":
        hora = random.choice([6, 7, 8, 9, 17, 18, 19, 20])
        clima = random.choices(["despejado", "lluvia", "lluvia_fuerte"], weights=[0.60, 0.30, 0.10], k=1)[0]
        congestion = random.randint(3, 5)
        incidente = int(random.random() < 0.08)
        demanda = random.randint(220, 360)
    else:
        hora = random.choice([7, 8, 9, 16, 17, 18, 19, 20, 21])
        clima = random.choices(["lluvia", "lluvia_fuerte"], weights=[0.40, 0.60], k=1)[0]
        congestion = random.randint(4, 5)
        incidente = int(random.random() < 0.35)
        demanda = random.randint(180, 320)

    ocupacion = min(100.0, max(35.0, (demanda / 4.0) + random.uniform(-8.0, 8.0)))

    return {
        "hora": hora,
        "clima": clima,
        "nivel_congestion": congestion,
        "incidente": incidente,
        "demanda_estimada": demanda,
        "ocupacion_pct": round(ocupacion, 2),
    }


# Construye un registro sintetico de operacion para clustering no supervisado.
def generar_registro(
    conocimiento: BaseConocimiento,
    reglas: Reglas,
    conexiones: list[tuple[str, str, int]],
    fecha_base: date,
) -> dict[str, str | int | float]:
    origen, destino, tiempo_base = random.choice(conexiones)
    fecha = fecha_base + timedelta(days=random.randint(0, 29))
    escenario = generar_escenario()

    hora = int(escenario["hora"])
    clima = str(escenario["clima"])
    congestion = int(escenario["nivel_congestion"])
    incidente = int(escenario["incidente"])
    demanda = int(escenario["demanda_estimada"])
    ocupacion = float(escenario["ocupacion_pct"])

    coord_origen = conocimiento.obtener_coord(origen)
    coord_destino = conocimiento.obtener_coord(destino)
    distancia = manhattan(coord_origen, coord_destino)
    transbordo = int(reglas.requiere_transbordo(origen, destino))
    pico = es_hora_pico(hora)

    clima_extra = {"despejado": 0.0, "lluvia": 2.0, "lluvia_fuerte": 4.5}[clima]
    ruido = random.uniform(-1.5, 1.5)
    tiempo_observado = (
        float(tiempo_base)
        + (3.5 if transbordo else 0.0)
        + (0.7 * distancia)
        + (1.4 * congestion)
        + clima_extra
        + (6.0 if incidente else 0.0)
        + (1.6 if pico else 0.0)
        + ruido
    )
    tiempo_observado = round(max(float(tiempo_base), tiempo_observado), 2)

    return {
        "fecha": fecha.isoformat(),
        "hora": hora,
        "origen": origen,
        "destino": destino,
        "distancia_manhattan": distancia,
        "transbordo": transbordo,
        "clima": clima,
        "nivel_congestion": congestion,
        "incidente": incidente,
        "demanda_estimada": demanda,
        "ocupacion_pct": ocupacion,
        "es_hora_pico": pico,
        "tiempo_observado_min": tiempo_observado,
    }


# Genera el CSV completo del dataset no supervisado con semilla reproducible.
def generar_dataset(ruta_salida: Path, cantidad: int = 360, semilla: int = 123) -> None:
    random.seed(semilla)

    estaciones = obtener_estaciones()
    conexiones = obtener_conexiones()
    conocimiento = BaseConocimiento(estaciones, conexiones)
    reglas = Reglas(conocimiento)

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    fecha_base = date(2026, 4, 1)

    columnas = [
        "fecha",
        "hora",
        "origen",
        "destino",
        "distancia_manhattan",
        "transbordo",
        "clima",
        "nivel_congestion",
        "incidente",
        "demanda_estimada",
        "ocupacion_pct",
        "es_hora_pico",
        "tiempo_observado_min",
    ]

    with ruta_salida.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        writer.writeheader()
        for _ in range(cantidad):
            writer.writerow(generar_registro(conocimiento, reglas, conexiones, fecha_base))

    print(f"Dataset no supervisado generado en: {ruta_salida}")
    print(f"Registros: {cantidad}")


if __name__ == "__main__":
    salida = ROOT / "actividad4" / "datos" / "operacion_transmilenio_muestra.csv"
    generar_dataset(salida, cantidad=360, semilla=123)
