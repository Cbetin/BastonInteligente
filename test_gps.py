
from gps import GPS
from time import sleep_ms, ticks_ms, ticks_diff


gps = GPS()

ultimo_reporte = ticks_ms()

print("GPS NEO-6M iniciado")
print("Buscando satelites...")


while True:

    gps.actualizar()

    ahora = ticks_ms()

    # Mostrar informacion cada segundo
    if ticks_diff(ahora, ultimo_reporte) >= 1000:

        ultimo_reporte = ahora

        datos = gps.obtener_datos()

        if datos is None:

            print("Esperando datos GGA del GPS...")

        elif datos["fix"]:

            print("------------------------------")
            print("POSICION VALIDA")

            print("Latitud:", datos["latitud"])
            print("Longitud:", datos["longitud"])
            print("Altitud:", datos["altitud"], "m")
            print("Satelites:", datos["satelites"])
            print("HDOP:", datos["hdop"])
            print("Hora UTC:", datos["hora_utc"])

            print(
                "Mapa: https://maps.google.com/?q="
                + str(datos["latitud"])
                + ","
                + str(datos["longitud"])
            )

        else:

            print(
                "Buscando posicion...",
                "| Satelites:", datos["satelites"],
                "| HDOP:", datos["hdop"]
            )

    sleep_ms(20)
