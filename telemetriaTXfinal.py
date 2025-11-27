from machine import UART, Pin, SPI, I2C
import time
import utime
import dht
from nrf24l01 import NRF24L01
from mpu import MPU6050

# =====================================================
#   CONFIG GPS
# =====================================================
gps = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
ultima_lat = 0.0
ultima_lon = 0.0

def convertir_a_decimal(valor, direccion):
    if valor == "":
        return None
    grados = int(valor[:2])
    minutos = float(valor[2:])
    decimal = grados + minutos / 60
    if direccion in ["S", "W"]:
        decimal *= -1
    return decimal

# =====================================================
#   CONFIG NRF24L01 (TX)
# =====================================================
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
csn = Pin(17, Pin.OUT)
ce  = Pin(15, Pin.OUT)

nrf = NRF24L01(spi, csn, ce, channel=100, payload_size=32)
nrf.open_tx_pipe(b'\xd2\xf0\xf0\xf0\xf0')
nrf.stop_listening()
print("📡 NRF listo (TX)")

# =====================================================
#   DHT11
# =====================================================
sensor_dht = dht.DHT11(Pin(6))
temp = 0
hum = 0
ultima_lectura_dht = time.ticks_ms()

# =====================================================
#   MPU6050
# =====================================================
GRAVEDAD = 9.80665
i2c = I2C(0, scl=Pin(21), sda=Pin(20))
mpu = MPU6050(i2c)

# =====================================================
#   TCRT DIGITAL
# =====================================================
PIN_TCRT = 5
tcrt = Pin(PIN_TCRT, Pin.IN)

REBOTE_FASE_MS  = 100
VENTANA_SEQ_MS  = 6000

secuencia_esperada = [1, 0, 1, 0]

fase = 0
ultimo_ms_fase = 0
inicio_ventana_ms = 0
ultimo_color = None

# =====================================================
# TIMER DE ENVÍO NRF24
# =====================================================
ultimo_envio = time.ticks_ms()

# =====================================================
# LOOP PRINCIPAL
# =====================================================
while True:

    # ---------------- LECTURA GPS ----------------
    if gps.any():
        linea = gps.readline()
        try:
            linea = linea.decode()

            if linea.startswith("$GPRMC"):
                datos = linea.split(",")
                if datos[2] == "A":   # datos válidos
                    ultima_lat = convertir_a_decimal(datos[3], datos[4])
                    ultima_lon = convertir_a_decimal(datos[5], datos[6])

        except:
            pass

    # ---------------- LECTURA DHT11 ----------------
    if time.ticks_diff(time.ticks_ms(), ultima_lectura_dht) > 2000:
        try:
            sensor_dht.measure()
            temp = sensor_dht.temperature()
            hum  = sensor_dht.humidity()
        except:
            temp = -1
            hum = -1

        ultima_lectura_dht = time.ticks_ms()

    # ---------------- LECTURA MPU ----------------
    ax_g, ay_g, az_g = mpu.get_accel()
    gx, gy, gz = mpu.get_gyro()

    ax = ax_g * GRAVEDAD
    ay = ay_g * GRAVEDAD
    az = az_g * GRAVEDAD

    # =====================================================
    #          **T C R T   N - B - N - B**
    # =====================================================
    ahora = time.ticks_ms()
    valor = tcrt.value()  # 1=negro, 0=blanco (ajustable)
    es_negro = (valor == 1)

    # Inicializar el último color
    if ultimo_color is None:
        ultimo_color = valor

    # Si cambia el color
    elif valor != ultimo_color:

        if time.ticks_diff(ahora, ultimo_ms_fase) >= REBOTE_FASE_MS:
            ultimo_ms_fase = ahora
            ultimo_color = valor

            if fase == 0:
                if valor == secuencia_esperada[0]:
                    fase = 1
                    inicio_ventana_ms = ahora

            else:
                if valor == secuencia_esperada[fase]:
                    fase += 1

                    # ---- Secuencia completa ----
                    if fase == 4:
                        print(">>> ¡Secuencia N-B-N-B detectada!")
                        fase = 0

                        # 📡 ENVIAR PAQUETE 3 (EVENTO TCRT)
                        paquete3 = "TCRT:1"
                        nrf.send(paquete3.encode())
                        print("📡 TX P3:", paquete3)

                else:
                    # Resincronizar si ve NEGRO
                    if valor == secuencia_esperada[0]:
                        fase = 1
                        inicio_ventana_ms = ahora
                    else:
                        fase = 0

    # Timeout reinicio
    if fase != 0 and time.ticks_diff(ahora, inicio_ventana_ms) > VENTANA_SEQ_MS:
        fase = 0

    # =====================================================
    #           ENVÍO NORMAL DE 1 Hz POR NRF24
    # =====================================================
    if time.ticks_diff(time.ticks_ms(), ultimo_envio) > 1000:

        # PAQUETE 1: GPS + TEMP + HUM
        paquete1 = f"{ultima_lat:.4f};{ultima_lon:.4f};{temp};{hum}"
        paquete1 = paquete1[:32]
        nrf.send(paquete1.encode())
        print("📡 TX P1:", paquete1)

        utime.sleep_ms(15)

        # PAQUETE 2: MPU6050
        paquete2 = f"{ax:.2f};{ay:.2f};{az:.2f};{gx:.2f};{gy:.2f};{gz:.2f}"
        paquete2 = paquete2[:32]
        nrf.send(paquete2.encode())
        print("📡 TX P2:", paquete2)

        ultimo_envio = time.ticks_ms()

    utime.sleep_ms(2)
