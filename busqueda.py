# Algoritmo A* que encuentra la mejor ruta en el grafo

from heapq import heappush, heappop


class BusquedaAEstrella:    
    def __init__(self, conocimiento, reglas):
        self.conocimiento = conocimiento
        self.reglas = reglas

    """
    Estimación de distancia entre estaciones.
    Se una la distancia Manhattan (simple y rápida).
    """
    def heuristica(self, actual, destino):
        x1, y1 = self.conocimiento.obtener_coord(actual)
        x2, y2 = self.conocimiento.obtener_coord(destino)
        return abs(x1 - x2) + abs(y1 - y2)

    """
    Implementación del algoritmo A*.        
    Retorna:
    - ruta encontrada
    - costo total
    """
    def buscar(self, inicio, objetivo):
        # Cola de prioridad (min-heap)
        frontera = []
        heappush(frontera, (0, inicio))

        # Para reconstruir la ruta
        vino_de = {inicio: None}

        # Costos acumulados
        costo = {inicio: 0}

        while frontera:
            _, actual = heappop(frontera)

            # Si llega al destino, se termina
            if actual == objetivo:
                break

            # Se revisan los vecinos (nodos conectados)
            for vecino, tiempo in self.conocimiento.obtener_vecinos(actual):
                # Se calcula el nuevo costo usando reglas
                nuevo_costo = costo[actual] + self.reglas.costo(actual, vecino, tiempo)

                # Si se encuentra un mejor camino
                if vecino not in costo or nuevo_costo < costo[vecino]:
                    costo[vecino] = nuevo_costo

                    # Prioridad = costo real + heurística
                    prioridad = nuevo_costo + self.heuristica(vecino, objetivo)
                    heappush(frontera, (prioridad, vecino))

                    # Se guarda de dónde venía
                    vino_de[vecino] = actual

        return self.reconstruir_ruta(vino_de, inicio, objetivo), costo.get(objetivo, None)

    """
    Reconstruye el camino desde el destino al inicio
    """
    def reconstruir_ruta(self, vino_de, inicio, objetivo):
        if objetivo not in vino_de:
            return None

        ruta = []
        actual = objetivo

        while actual != inicio:
            ruta.append(actual)
            actual = vino_de[actual]

        # Agregamos el nodo inicial al final
        ruta.append(inicio)

        ruta.reverse()
        return ruta