# Grafo con la estructura de conexiones
# Se organizan los datos para poder usarlos fácilmente

class BaseConocimiento:

    # estaciones: diccionario con info de cada estación
    # conexiones: lista de conexiones entre estaciones
    def __init__(self, estaciones, conexiones):
        self.estaciones = estaciones
        self.grafo = {}

        # Se inicializa cada estación en el grafo
        for estacion in estaciones:
            self.grafo[estacion] = []

        # Se agregan las conexiones (aristas del grafo)
        for origen, destino, tiempo in conexiones:
            self.grafo[origen].append((destino, tiempo))
            self.grafo[destino].append((origen, tiempo))

    # Devuelve las estaciones conectadas a la estación actual"""
    def obtener_vecinos(self, estacion):
        return self.grafo.get(estacion, [])

    # Devuelve la línea a la que pertenece una estación"""
    def obtener_linea(self, estacion):
        return self.estaciones[estacion]["linea"]

    # Devuelve coordenadas (x, y) de la estación"""
    def obtener_coord(self, estacion):
        return self.estaciones[estacion]["coord"]