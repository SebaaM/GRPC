# Ejercicios de gRPC en Python

## Archivos

Los archivos `.proto` son el **contrato de comunicación**: definen los servicios, los métodos y los datos que intercambian cliente y servidor.

| Archivo                         | Qué hace                                                                                           |
| ------------------------------- | -------------------------------------------------------------------------------------------------- |
| `ejercicio_1/temperatura.proto` | Define la solicitud y respuesta de la conversión.                                                  |
| `ejercicio_2/monitoreo.proto`   | Define la solicitud y los reportes del monitoreo.                                                  |
| `servidor.py` de cada ejercicio | Implementa el servicio: convierte la temperatura o genera los reportes.                            |
| `cliente.py` de cada ejercicio  | Pide la entrada, llama al servidor y muestra las respuestas.                                       |
| `*_pb2.py`                      | **Generado automáticamente** desde el `.proto`. Contiene las clases de los mensajes.               |
| `*_pb2_grpc.py`                 | **Generado automáticamente**. Contiene el cliente gRPC (Stub) y la base del servicio del servidor. |
| `README.md`                     | Explica cómo instalar y ejecutar los ejercicios.                                                   |

El prefijo `*` corresponde a `temperatura` o `monitoreo`.
Los archivos generados se crean con `grpc_tools.protoc`; no se editan a mano.

## Preparación

Usar Python 3.13 y un entorno virtual activo. Ejecutar los comandos desde la carpeta del proyecto.

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejercicio 1: conversor de temperaturas

Patrón unario: una solicitud y una respuesta.
El servidor convierte Celsius a Fahrenheit con la fórmula **°F = °C × 1,8 + 32**.

Iniciar el servidor en una terminal:

```bash
python ejercicio_1/servidor.py
```

Ejecutar el cliente en otra terminal:

```bash
python ejercicio_1/cliente.py
```

Ingresar una temperatura. Se acepta punto o coma decimal.

| Entrada en °C | Resultado en °F |
| ------------- | --------------- |
| 0             | 32              |
| 25            | 77              |
| 100           | 212             |
| -40           | -40             |
| 36,5          | 97,70           |

Probar también texto, una entrada vacía, `NaN` o `inf`: el cliente debe volver a pedir un número.

## Ejercicio 2: monitoreo del servidor

Streaming del servidor: una solicitud y cinco reportes, uno cada dos segundos.

Iniciar el servidor en una terminal:

```bash
python ejercicio_2/servidor.py
```

Ejecutar el cliente en otra terminal:

```bash
python ejercicio_2/cliente.py
```

Presionar Enter. Cada reporte muestra CPU, RAM disponible en MB y disco libre en GB de la máquina del servidor.
En Linux se consulta `/`; en Windows, la unidad del sistema.

Después de los cinco reportes debe aparecer `Monitoreo finalizado.`.
