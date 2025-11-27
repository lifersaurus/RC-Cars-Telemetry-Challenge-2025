import utime
from machine import Pin, SPI
from nrf24l01 import NRF24L01

# --- CONFIG NRF ---
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn = Pin(17, Pin.OUT)
ce  = Pin(15, Pin.OUT)

nrf = NRF24L01(spi, csn, ce, channel=100, payload_size=32)
nrf.open_rx_pipe(1, b'\xd2\xf0\xf0\xf0\xf0')
nrf.start_listening()

print("📡 Receptor listo...\n")

# Variables iniciales de los paquetes
paquete1 = {"lat": "--", "lon": "--", "temp": "--", "hum": "--"}
paquete2 = {"ax": "--", "ay": "--", "az": "--", "gx": "--", "gy": "--", "gz": "--"}
evento_tcrt = 0  # 0 = no hay evento, 1 = secuencia detectada

# Tiempo para imprimir cada intervalo
intervalo = 1  # segundos
ultimo_tiempo = utime.time()

while True:

    # Si llegó un paquete por radio
    if nrf.any():
        data = nrf.recv()
        msg = data.decode().strip("\x00")
        print("📥 Recibido:", msg)

        # -------- PAQUETE 3 → TCRT EVENTO --------
        if msg.startswith("TCRT:"):
            evento_tcrt = int(msg.split(":")[1])
            print("→ Evento TCRT recibido!")
            continue

        partes = msg.split(";")

        # -------- PAQUETE 1 → GPS + DHT --------
        if len(partes) == 4:
            paquete1 = {
                "lat": partes[0],
                "lon": partes[1],
                "temp": partes[2],
                "hum": partes[3]
            }
            print("→ Paquete 1 actualizado")

        # -------- PAQUETE 2 → MPU6050 --------
        elif len(partes) == 6:
            paquete2 = {
                "ax": partes[0],
                "ay": partes[1],
                "az": partes[2],
                "gx": partes[3],
                "gy": partes[4],
                "gz": partes[5]
            }
            print("→ Paquete 2 actualizado")

    # -------- IMPRIMIR DATOS CADA 1 SEGUNDO --------
    if utime.time() - ultimo_tiempo >= intervalo:
        ultimo_tiempo = utime.time()

        print("\n======================================")
        print("📦 ACTUALIZACIÓN DE PAQUETES")
        print("======================================")

        print("\n📌 PAQUETE 1 (GPS + DHT)")
        print("Lat:", paquete1["lat"])
        print("Lon:", paquete1["lon"])
        print("Temp:", paquete1["temp"], "°C")
        print("Hum :", paquete1["hum"], "%")

        print("\n📌 PAQUETE 2 (MPU6050)")
        print("Ax:", paquete2["ax"])
        print("Ay:", paquete2["ay"])
        print("Az:", paquete2["az"])
        print("Gx:", paquete2["gx"])
        print("Gy:", paquete2["gy"])
        print("Gz:", paquete2["gz"])

        print("\n📌 EVENTO TCRT")
        if evento_tcrt == 1:
            print("🔥 Secuencia N-B-N-B detectada!")
            evento_tcrt = 0  # reset después de mostrarlo
        else:
            print("Sin evento")

        print("======================================\n")

    utime.sleep(0.05)
