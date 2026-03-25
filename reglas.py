# Reglas del sistema inteligente
# Estas reglas ayudan a tomar decisiones (ej: penalizar transbordos)

class Reglas:
    def __init__(self, conocimiento):
        self.conocimiento = conocimiento

    """
    Regla: verifica si dos estaciones están en la misma línea
    """
    def misma_linea(self, e1, e2):
        return self.conocimiento.obtener_linea(e1) == self.conocimiento.obtener_linea(e2)

    """
    Regla: si no están en la misma línea, hay transbordo
    """
    def requiere_transbordo(self, e1, e2):
        return not self.misma_linea(e1, e2)

    """
    Calcula el costo de moverse entre estaciones.
    - tiempo_base: tiempo real entre estaciones
    - si hay transbordo, se suma penalización
    """
    def costo(self, actual, vecino, tiempo_base):
        costo = tiempo_base

        # Regla: penalizar transbordo
        if self.requiere_transbordo(actual, vecino):
            costo += 4

        return costo