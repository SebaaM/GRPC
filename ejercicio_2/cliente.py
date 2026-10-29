"""Cliente del ejercicio 2: consume cinco respuestas de una única llamada."""

from datetime import datetime

import grpc

# Clases generadas desde el contrato .proto compartido con el servidor.
import monitoreo_pb2
import monitoreo_pb2_grpc

DIRECCION = "127.0.0.1:50052"
CANTIDAD_REPORTES = 5


def main():
    print("EJERCICIO 2 | Monitoreo del servidor | Streaming del servidor")
    llamada = None
    try:
        input("Presioná Enter para iniciar la consulta...")
        # Canal de comunicación local sin TLS; se cierra al salir del bloque.
        with grpc.insecure_channel(DIRECCION) as canal:
            # El Stub permite invocar el servicio remoto desde Python.
            cliente = monitoreo_pb2_grpc.MonitorServidorStub(canal)
            # Se llama UNA vez; el iterador entrega los reportes al llegar.
            llamada = cliente.Monitorear(
                monitoreo_pb2.SolicitudMonitoreo(),
                timeout=20,  # Plazo para el stream completo, no para cada reporte.
            )
            recibidos = 0
            # Iterar espera cada respuesta a medida que llega por el mismo RPC.
            # Este bucle NO vuelve a llamar a Monitorear ni consulta métricas locales.
            for recibidos, reporte in enumerate(llamada, start=1):
                hora = datetime.now().strftime("%H:%M:%S")
                print(f"Reporte {recibidos}/5 [{hora}]", flush=True)
                print(
                    f"  CPU: {reporte.cpu_porcentaje:.2f} % | "
                    f"RAM disponible: {reporte.ram_disponible_mb:.2f} MB | "
                    f"Disco libre: {reporte.disco_libre_gb:.2f} GB",
                    flush=True,
                )

        if recibidos != CANTIDAD_REPORTES:
            print(f"Error: se recibieron {recibidos} reportes; se esperaban cinco.")
            return 1

        print("Monitoreo finalizado.")
        return 0
    # Un stream puede fallar al iniciarse o mientras se está recorriendo.
    except grpc.RpcError as error:
        print(f"Error gRPC ({error.code().name}): {error.details()}")
        print("Monitoreo interrumpido. Verificá que el servidor esté disponible.")
        return 1
    except EOFError:
        print("\nEntrada finalizada. No se inició el monitoreo.")
        return 1
    except KeyboardInterrupt:
        if llamada is not None:
            llamada.cancel()  # Comunica al servidor que ya no esperamos reportes.
        print("\nMonitoreo cancelado por el usuario.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
