
from hx711 import HX711
from time import sleep_ms
import sys


# Configuracion de pines segun la placa
if sys.platform == "esp32":

    sensor = HX711(dout=18, sck=19)
    print("Placa: ESP32 DEVKIT V1")

elif sys.platform == "rp2":

    sensor = HX711(dout=2, sck=3)
    print("Placa: Raspberry Pi Pico")

else:

    raise RuntimeError("Placa no compatible")


print("Iniciando HX711...")
print("No aplicar fuerza sobre la galga")

sleep_ms(3000)

# Obtener referencia sin carga
tara = sensor.read_average(20)

print("Tara:", tara)
print("Iniciando mediciones...")

while True:

    lectura = sensor.read_average(5)

    diferencia = lectura - tara

    print(
        "Lectura:", int(lectura),
        "| Diferencia:", int(diferencia)
    )

    sleep_ms(200)
