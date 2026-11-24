
from machine import Pin, disable_irq, enable_irq
from time import sleep_us, sleep_ms, ticks_ms, ticks_diff


class HX711:

    def __init__(self, dout, sck):
        self.dout = Pin(dout, Pin.IN)
        self.sck = Pin(sck, Pin.OUT, value=0)

        sleep_ms(500)

    def read(self):

        inicio = ticks_ms()

        # Esperar que el HX711 tenga datos disponibles
        while self.dout.value() == 1:

            if ticks_diff(ticks_ms(), inicio) > 2000:
                raise OSError("HX711 no responde")

            sleep_ms(1)

        dato = 0

        # Proteger la secuencia de pulsos
        estado_irq = disable_irq()

        try:
            # Leer los 24 bits
            for i in range(24):

                self.sck.value(1)
                sleep_us(1)

                bit = self.dout.value()

                self.sck.value(0)
                sleep_us(1)

                dato = (dato << 1) | bit

            # Pulso 25: canal A, ganancia 128
            self.sck.value(1)
            sleep_us(1)
            self.sck.value(0)

        finally:
            self.sck.value(0)
            enable_irq(estado_irq)

        # Conversion a entero con signo
        if dato & 0x800000:
            dato -= 0x1000000

        return dato

    def read_average(self, muestras=10):

        suma = 0

        for i in range(muestras):
            suma += self.read()

        return suma / muestras
