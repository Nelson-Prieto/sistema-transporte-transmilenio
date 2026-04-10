# Datos del sistema

# Retorna un diccionario con estaciones de TransMilenio.    
# Cada estación tiene:
# - línea a la que pertenece
# - coordenadas (para la heurística del algoritmo)
def obtener_estaciones():
    return {
        "Portal Norte": {"linea": "Norte", "coord": (0, 0)},
        "Calle 100": {"linea": "Norte", "coord": (1, 0)},
        "Calle 72": {"linea": "Norte", "coord": (2, 0)},
        "Calle 26": {"linea": "Centro", "coord": (3, 0)},
        "Av Jiménez": {"linea": "Centro", "coord": (4, 0)},
        "Portal Sur": {"linea": "Sur", "coord": (5, 0)},
        "Banderas": {"linea": "Sur", "coord": (4, 1)},
        "Américas": {"linea": "Sur", "coord": (3, 1)},
    }

# Lista de conexiones entre estaciones.    
# Cada tupla significa: (origen, destino, tiempo en minutos)

def obtener_conexiones():
    return [
        ("Portal Norte", "Calle 100", 5),
        ("Calle 100", "Calle 72", 4),
        ("Calle 72", "Calle 26", 6),
        ("Calle 26", "Av Jiménez", 3),
        ("Av Jiménez", "Portal Sur", 7),
        ("Calle 26", "Américas", 5),
        ("Américas", "Banderas", 4),
        ("Banderas", "Portal Sur", 6),
    ]