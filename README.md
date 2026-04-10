# Sistema de Transporte TransMilenio

Proyecto academico que simula un sistema inteligente de rutas de TransMilenio usando:

- Representacion del conocimiento (grafo de estaciones)
- Sistema basado en reglas (penalizacion por transbordo)
- Busqueda informada A* (A estrella)

## Objetivo

Encontrar la mejor ruta entre una estacion de origen y una de destino, minimizando el costo total del viaje.

El costo total combina:

- Tiempo real entre estaciones
- Penalizacion cuando hay cambio de linea (transbordo)

## Estructura del proyecto

```text
sistema-transporte-transmilenio/
|-- datos_transmilenio.py
|-- conocimiento.py
|-- reglas.py
|-- busqueda.py
|-- main.py
|-- README.md
```

### 1) `datos_transmilenio.py`

Define los datos base del dominio:

- `obtener_estaciones()`: devuelve estaciones con su linea y coordenadas `(x, y)`.
- `obtener_conexiones()`: devuelve conexiones con el formato `(origen, destino, tiempo)`.

### 2) `conocimiento.py`

Construye la base de conocimiento como un grafo:

- `BaseConocimiento.__init__`: arma nodos y aristas bidireccionales.
- `obtener_vecinos(estacion)`: retorna estaciones conectadas.
- `obtener_linea(estacion)`: retorna la linea de la estacion.
- `obtener_coord(estacion)`: retorna coordenadas para heuristica.

### 3) `reglas.py`

Contiene reglas del sistema experto:

- `misma_linea(e1, e2)`: valida si dos estaciones estan en la misma linea.
- `requiere_transbordo(e1, e2)`: determina si hay cambio de linea.
- `costo(actual, vecino, tiempo_base)`: suma penalizacion de `+4` si hay transbordo.

### 4) `busqueda.py`

Implementa el algoritmo A*:

- `heuristica(actual, destino)`: distancia Manhattan.
- `buscar(inicio, objetivo)`: explora el grafo con cola de prioridad.
- `reconstruir_ruta(...)`: reconstruye el camino final.

Formula usada por A*:

```text
prioridad = costo_acumulado + heuristica
```

### 5) `main.py`

Punto de entrada del sistema:

1. Carga datos.
2. Construye conocimiento.
3. Inicializa reglas.
4. Crea buscador A*.
5. Pide origen y destino por consola.
6. Ejecuta busqueda y muestra ruta/costo.

## Requisitos

- Python 3.10 o superior
- No requiere librerias externas (solo modulos estandar)

## Ejecucion

Desde la carpeta del proyecto:

```bash
python main.py
```

## Flujo de uso

1. El sistema muestra estaciones disponibles.
2. El usuario ingresa estacion de origen.
3. El usuario ingresa estacion de destino.
4. El sistema calcula la mejor ruta con A* + reglas.
5. Se imprime:
   - Ruta encontrada
   - Costo total

## Ejemplo de salida

```text
SISTEMA DE RUTAS TRANSMILENIO
...
Ruta encontrada:
Portal Norte -> Calle 100 -> Calle 72 -> Calle 26 -> Av Jimenez -> Portal Sur
Costo total: 33
```

## Decisiones de diseno

- Separacion por capas:
  - Datos (hechos)
  - Conocimiento (estructura)
  - Reglas (logica de negocio)
  - Busqueda (motor de decision)
  - Interfaz por consola (main)
- Facilita mantenimiento, pruebas y extensiones.

## Posibles mejoras

- Agregar mas estaciones y conexiones reales.
- Incluir horarios y frecuencia de buses.
- Diferenciar tipos de penalizacion por horario.
- Crear interfaz grafica o API web.
- Agregar pruebas unitarias por modulo.

## Contexto academico

Actividad 2: Busqueda y sistemas basados en reglas.

Este proyecto demuestra como combinar metodos de IA simbolica (reglas) con busqueda heuristica (A*).

---

## Actividad 3: Metodos de aprendizaje supervisado

Como complemento de la Actividad 2, se agrega un flujo simple de aprendizaje supervisado para estimar `tiempo_real_min` en un tramo del sistema.

### Fuentes de datos identificadas

1. Datos operacionales por tramo (tiempos reales por franja horaria).
2. Datos de demanda por estacion y hora.
3. Datos de incidentes operacionales (bloqueos, accidentes, cierres).
4. Datos de clima (lluvia e intensidad por hora/zona).

Detalle en: `actividad3/fuentes_datos.md`

### Dataset de muestra incluido

Cuando no se cuenta con todas las fuentes reales integradas, se usa un dataset sintetico:

- Ruta: `actividad3/datos/viajes_transmilenio_muestra.csv`
- Generador: `actividad3/generar_dataset_muestra.py`
- Target supervisado: `tiempo_real_min`

### Modelo supervisado implementado

- Tipo: Regresion lineal (entrenada con descenso de gradiente, sin librerias externas).
- Script: `actividad3/entrenar_modelo_supervisado.py`
- Modelo guardado: `actividad3/modelos/modelo_regresion_lineal.json`
- Script de inferencia: `actividad3/predecir_tiempo.py`

### Comandos de ejecucion (Actividad 3)

Desde la raiz del proyecto:

```bash
python actividad3/generar_dataset_muestra.py
python actividad3/entrenar_modelo_supervisado.py
python actividad3/predecir_tiempo.py
```

### Campos del dataset de muestra

- `fecha`, `hora`, `origen`, `destino`
- `tiempo_base_min`, `transbordo`, `distancia_manhattan`
- `clima`, `nivel_congestion`, `incidente`, `demanda_estimada`, `es_hora_pico`
- `tiempo_real_min` (variable objetivo)
