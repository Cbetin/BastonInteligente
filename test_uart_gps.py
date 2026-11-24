
from machine import UART, Pin
from time import sleep_ms
import sys


if sys.platform == "esp32":

    gps = UART(
        2,
        baudrate=9600,
        tx=Pin(17),
        rx=Pin(16)
    )

elif sys.platform == "rp2":

    gps = UART(
        0,
        baudrate=9600,
        tx=Pin(0),
        rx=Pin(1)
    )

else:

    raise RuntimeError("Placa no compatible")


print("Iniciando comunicacion con GPS...")

while True:

    if gps.any():

        datos = gps.read()

        if datos:
            print(datos.decode("ascii", "ignore"), end="")

    sleep_ms(20)
