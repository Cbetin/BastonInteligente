
from machine import UART, Pin
from time import ticks_ms, ticks_diff
import sys


class GPS:

    def __init__(self, baudrate=9600):

        if sys.platform == "esp32":

            self.uart = UART(
                2,
                baudrate=baudrate,
                tx=Pin(17),
                rx=Pin(16),
                rxbuf=2048,
                timeout=0
            )

        elif sys.platform == "rp2":

            self.uart = UART(
                0,
                baudrate=baudrate,
                tx=Pin(0),
                rx=Pin(1),
                rxbuf=2048,
                timeout=0
            )

        else:

            raise RuntimeError("Placa no compatible")

        self.buffer = bytearray()
        self.datos = None
        self.ultima_lectura = None


    # Convertir coordenadas NMEA a grados decimales
    def convertir_coordenada(self, valor, hemisferio):

        numero = float(valor)

        grados = int(numero / 100)
        minutos = numero - grados * 100

        decimal = grados + minutos / 60

        if hemisferio in ("S", "W"):
            decimal = -decimal

        return decimal


    # Verificar integridad de la trama NMEA
    def verificar_checksum(self, trama):

        if not trama.startswith("$"):
            return False

        if "*" not in trama:
            return False

        cuerpo, checksum = trama[1:].split("*", 1)

        calculado = 0

        for caracter in cuerpo:
            calculado ^= ord(caracter)

        try:
            return calculado == int(checksum, 16)

        except ValueError:
            return False


    # Interpretar trama GGA
    def procesar_trama(self, trama):

        if not self.verificar_checksum(trama):
            return

        campos = trama.split("*")[0].split(",")

        if campos[0][-3:] != "GGA":
            return

        try:

            hora = campos[1]
            calidad = int(campos[6] or 0)
            satelites = int(campos[7] or 0)

            hdop = (
                float(campos[8])
                if campos[8] else None
            )

            latitud = None
            longitud = None
            altitud = None

            fix = (
                calidad > 0
                and bool(campos[2])
                and bool(campos[4])
                and campos[3] in ("N", "S")
                and campos[5] in ("E", "W")
            )

            if fix:

                latitud = self.convertir_coordenada(
                    campos[2],
                    campos[3]
                )

                longitud = self.convertir_coordenada(
                    campos[4],
                    campos[5]
                )

                if campos[9]:
                    altitud = float(campos[9])

            self.datos = {
                "fix": fix,
                "hora_utc": hora,
                "latitud": latitud,
                "longitud": longitud,
                "altitud": altitud,
                "satelites": satelites,
                "calidad": calidad,
                "hdop": hdop
            }

            self.ultima_lectura = ticks_ms()

        except (ValueError, IndexError):
            return


    # Leer continuamente sin esperar una posicion
    def actualizar(self):

        disponibles = self.uart.any()

        if not disponibles:
            return

        datos = self.uart.read(disponibles)

        if not datos:
            return

        for byte in datos:

            # Inicio de una nueva trama
            if byte == 36:

                self.buffer = bytearray()
                self.buffer.append(byte)

            # Final de la trama
            elif byte == 10:

                if self.buffer:

                    try:
                        trama = self.buffer.decode().strip()
                        self.procesar_trama(trama)

                    except ValueError:
                        pass

                self.buffer = bytearray()

            elif self.buffer:

                self.buffer.append(byte)

                if len(self.buffer) > 128:
                    self.buffer = bytearray()


    # Obtener la informacion mas reciente
    def obtener_datos(self):

        if self.ultima_lectura is None:
            return None

        antiguedad = ticks_diff(
            ticks_ms(),
            self.ultima_lectura
        )

        if antiguedad > 5000:
            return None

        return self.datos
