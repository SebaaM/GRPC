"""Cliente del ejercicio 1: valida la entrada y hace una única llamada gRPC."""

import math

import grpc

# Mensajes y stub generados a partir del mismo contrato que usa el servidor.
import temperatura_pb2
import temperatura_pb2_grpc

DIRECCION = "127.0.0.1:50051"


def leer_celsius():
    while True:
        texto = input("Ingresá una temperatura en °C: ").strip()
        try:
            # Se admite, por ejemplo, 36.5 o 36,5.
            celsius = float(texto.replace(",", "."))
        except ValueError:
            print("Entrada inválida. Ingresá un número, por ejemplo 25 o 36,5.")
            continue
        if not math.isfinite(celsius):
            print("Entrada inválida. El número debe ser finito (sin NaN ni infinito).")
            continue
        return celsius


def main():
    print("EJERCICIO 1 | Conversor de temperaturas | Patrón unario")
    try:
        celsius = leer_celsius()
        # El canal conecta con el servidor. "insecure" significa sin TLS.
        # El bloque with cierra el canal al terminar, incluso si hay un error.
        with grpc.insecure_channel(DIRECCION) as canal:
            # El Stub es el representante local del servicio remoto.
            cliente = temperatura_pb2_grpc.ConversorTemperaturaStub(canal)
            # Parece una función local, pero envía la solicitud por gRPC y espera
            # una respuesta del servidor. El plazo máximo es de cinco segundos.
            respuesta = cliente.Convertir(
                temperatura_pb2.SolicitudTemperatura(celsius=celsius),
                timeout=5,
            )
        print(f"Resultado: {celsius:.2f} °C = {respuesta.fahrenheit:.2f} °F")
        return 0
    # Los errores remotos y de conexión llegan como RpcError, con código y detalle.
    except grpc.RpcError as error:
        print(f"Error gRPC ({error.code().name}): {error.details()}")
        print("Verificá que el servidor del ejercicio 1 esté ejecutándose.")
        return 1
    except EOFError:
        print("\nEntrada finalizada. No se realizó la conversión.")
        return 1
    except KeyboardInterrupt:
        print("\nConversión cancelada.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
