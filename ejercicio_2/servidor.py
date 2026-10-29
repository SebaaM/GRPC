"""Servidor gRPC del ejercicio 2: cinco reportes reales cada dos segundos."""

import logging
import os
from concurrent import futures
from pathlib import Path

import grpc
import psutil

# Mensajes y base del servicio generados por el compilador de Protocol Buffers.
import monitoreo_pb2
import monitoreo_pb2_grpc

DIRECCION = "127.0.0.1:50052"
CANTIDAD_REPORTES = 5
INTERVALO_SEGUNDOS = 2
LOGGER = logging.getLogger(__name__)


def raiz_disco():
    """En Windows devuelve la unidad del sistema; en Linux, la raíz /."""
    if os.name == "nt":
        return Path(os.environ.get("SystemRoot", "C:\\Windows")).anchor
    return "/"


# Implementamos el servicio que declara monitoreo.proto.
class MonitorServidor(monitoreo_pb2_grpc.MonitorServidorServicer):
    def Monitorear(self, request, context):
        # Se invoca UNA vez por consulta. El generador produce cinco respuestas.
        raiz = raiz_disco()
        enviados = 0
        LOGGER.info("Monitorear: una solicitud; hasta cinco reportes. Disco: %s", raiz)
        try:
            for numero in range(1, CANTIDAD_REPORTES + 1):
                # Si el cliente cancela o vence su plazo, dejamos de producir datos.
                if not context.is_active():
                    return

                # Esta medición ya espera dos segundos. No agregar time.sleep(2).
                cpu = psutil.cpu_percent(interval=INTERVALO_SEGUNDOS)
                if not context.is_active():
                    return

                # Las consultas ocurren aquí, en la máquina del servidor.
                reporte = monitoreo_pb2.ReporteEstado(
                    cpu_porcentaje=cpu,
                    ram_disponible_mb=psutil.virtual_memory().available / 1_000_000,
                    disco_libre_gb=psutil.disk_usage(raiz).free / 1_000_000_000,
                )
                LOGGER.info(
                    "Reporte %d/5 | CPU: %.2f %% | RAM disponible: %.2f MB | "
                    "Disco libre: %.2f GB",
                    numero,
                    reporte.cpu_porcentaje,
                    reporte.ram_disponible_mb,
                    reporte.disco_libre_gb,
                )
                enviados += 1
                # yield entrega un mensaje al stream sin terminar el método.
                # Al agotarse el bucle, el stream se cierra de forma normal.
                yield reporte
        except OSError:
            LOGGER.exception("No se pudieron obtener las métricas del servidor.")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "No se pudieron obtener las métricas del servidor.",
            )
        finally:
            LOGGER.info("Monitoreo cerrado: %d/5 reportes enviados.", enviados)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    # Cada llamada se atiende en un trabajador del servidor gRPC.
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    # Registro: asocia las rutas RPC del contrato con nuestra implementación.
    monitoreo_pb2_grpc.add_MonitorServidorServicer_to_server(
        MonitorServidor(), servidor
    )
    try:
        # Puerto local sin TLS para esta demostración.
        if servidor.add_insecure_port(DIRECCION) == 0:
            raise RuntimeError("No se pudo abrir el puerto.")
        servidor.start()  # Inicia la escucha sin bloquear el hilo principal.
    except RuntimeError as error:
        LOGGER.error("No se pudo iniciar el servidor en %s: %s", DIRECCION, error)
        return 1

    LOGGER.info("EJERCICIO 2 | Servidor de monitoreo en %s", DIRECCION)
    LOGGER.info("Métricas de ESTA máquina. Raíz/unidad del sistema: %s", raiz_disco())
    LOGGER.info("Cinco reportes, uno cada dos segundos. Para detener: Ctrl+C.")
    try:
        servidor.wait_for_termination()  # Espera nuevas llamadas hasta Ctrl+C.
    except KeyboardInterrupt:
        LOGGER.info("Deteniendo el servidor.")
    finally:
        servidor.stop(grace=0).wait()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
