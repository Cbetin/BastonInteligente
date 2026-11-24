
from machine import Pin, ADC
from time import sleep_ms
import sys

# Configuracion del microcontrolador
if sys.platform == "esp32":
    fsr = ADC(Pin(34))
    fsr.atten(ADC.ATTN_11DB)
    print("Placa: ESP32")

elif sys.platform == "rp2":
    fsr = ADC(Pin(26))
    print("Placa: Raspberry Pi Pico")

else:
    raise RuntimeError("Placa no compatible")


# Umbral provisional de agarre
UMBRAL = 10000


# Funcion de lectura con filtro promedio
def leer_fsr():
    suma = 0

    for i in range(20):
        suma += fsr.read_u16()
        sleep_ms(5)

    return suma // 20


# Programa principal
while True:

    lectura = leer_fsr()

    if lectura > UMBRAL:
        estado = "AGARRE DETECTADO"
    else:
        estado = "SIN AGARRE"

    print("ADC:", lectura, "| Estado:", estado)

    sleep_ms(200)
