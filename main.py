from datos_transmilenio import obtener_estaciones, obtener_conexiones
from conocimiento import BaseConocimiento
from reglas import Reglas
from busqueda import BusquedaAEstrella

"""
Permite al usuario seleccionar una estación válida desde consola
"""
def seleccionar_estacion(estaciones, mensaje):    
    while True:
        print("\nEstaciones disponibles:")
        for nombre in estaciones:
            print(f"- {nombre}")

        seleccion = input(f"\n{mensaje}: ").strip()

        if seleccion in estaciones:
            return seleccion
        else:
            print("Estación no válida, intenta de nuevo.")

# Ejecución principal del sistema
def main():

    # 1. Cargar datos (hechos)
    estaciones = obtener_estaciones()
    conexiones = obtener_conexiones()

    # 2. Crear base de conocimiento (grafo)
    conocimiento = BaseConocimiento(estaciones, conexiones)

    # 3. Crear sistema de reglas
    reglas = Reglas(conocimiento)

    # 4. Crear buscador A*
    buscador = BusquedaAEstrella(conocimiento, reglas)

    print("SISTEMA DE RUTAS TRANSMILENIO")

    # 5. Definir origen y destino
    origen = seleccionar_estacion(estaciones, "Ingrese estación de ORIGEN")
    destino = seleccionar_estacion(estaciones, "Ingrese estación de DESTINO")

    # Evitar mismo origen y destino
    if origen == destino:
        print("El origen y destino no pueden ser iguales.")
        return
    
    # 6. Ejecutar búsqueda
    ruta, costo = buscador.buscar(origen, destino)

    # 7. Mostrar resultado
    if ruta:
        print("Ruta encontrada:")
        print(" -> ".join(ruta))
        print(f"Costo total: {costo}")
    else:
        print("No se encontró ruta")

# Ejecutar el programa
if __name__ == "__main__":
    main()