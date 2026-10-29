"""Servidor gRPC del ejercicio 1: conversión unaria de Celsius a Fahrenheit."""

import logging
import math
from concurrent import futures

import grpc

# pb2: clases de los mensajes. pb2_grpc: clases del servicio generadas por protoc.
import temperatura_pb2
import temperatura_pb2_grpc

DIRECCION = "127.0.0.1:50051"
LOGGER = logging.getLogger(__name__)


# Heredamos el Servicer generado para implementar el servicio del archivo .proto.
class ConversorTemperatura(temperatura_pb2_grpc.ConversorTemperaturaServicer):
    def Convertir(self, request, context):
        # gRPC invoca este método: request es el mensaje deserializado del cliente.
        # context permite indicar errores y consultar el estado de la llamada.
        # El contrato double garantiza un número, pero permite NaN e infinito.
        if not math.isfinite(request.celsius):
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "La temperatura debe ser un número finito.",
            )

        fahrenheit = request.celsius * 1.8 + 32
        if not math.isfinite(fahrenheit):
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "La temperatura es demasiado grande para realizar la conversión.",
            )

        LOGGER.info(
            "Convertir: %.2f °C -> %.2f °F (una solicitud, una respuesta)",
            request.celsius,
            fahrenheit,
        )
        # En un RPC unario se devuelve UN mensaje. gRPC lo serializa y lo envía.
        return temperatura_pb2.RespuestaTemperatura(fahrenheit=fahrenheit)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    # El servidor recibe las llamadas; el pool permite atender varios clientes.
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    # Registrar vincula el servicio del .proto con nuestra implementación.
    temperatura_pb2_grpc.add_ConversorTemperaturaServicer_to_server(
        ConversorTemperatura(), servidor
    )
    try:
        # Dirección de escucha sin TLS, apropiada para esta práctica local.
        if servidor.add_insecure_port(DIRECCION) == 0:
            raise RuntimeError("No se pudo abrir el puerto.")
        # start() comienza a escuchar sin bloquear este hilo.
        servidor.start()
    except RuntimeError as error:
        LOGGER.error("No se pudo iniciar el servidor en %s: %s", DIRECCION, error)
        return 1

    LOGGER.info("EJERCICIO 1 | Servidor unario en %s", DIRECCION)
    LOGGER.info("Fórmula: °F = °C x 1,8 + 32. Para detener: Ctrl+C.")
    try:
        # Mantiene vivo el proceso para que pueda seguir recibiendo solicitudes.
        servidor.wait_for_termination()
    except KeyboardInterrupt:
        LOGGER.info("Deteniendo el servidor.")
    finally:
        servidor.stop(grace=0).wait()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
