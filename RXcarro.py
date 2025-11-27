from machine import Pin, SPI, PWM
from nrf24l01 import NRF24L01, POWER_3, SPEED_250K
import utime, struct
from servo import Servo

led = Pin("LED", Pin.OUT)
led.value(0)

esc = PWM(Pin(0))
esc.freq(50)
current_pwm = 4420

s1 = Servo(2)

def servo_Map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def servo_Angle(angle):
    if angle < 0:
        angle = 0
    elif angle > 180:
        angle = 180
    pwm_value = round(servo_Map(angle, 0, 180, 0, 1024))
    s1.goto(pwm_value)

spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
csn = Pin(13, Pin.OUT)
ce  = Pin(14, Pin.OUT)

nrf = NRF24L01(spi, csn, ce, channel=100, payload_size=3)
nrf.set_power_speed(POWER_3, SPEED_250K)
nrf.set_crc(2)
nrf.reg_write(0x04, (10 << 4) | 5)

nrf.open_tx_pipe(b'\xd2\xf0\xf0\xf0\xf0')
nrf.open_rx_pipe(1, b'\xe1\xf0\xf0\xf0\xf0')
nrf.start_listening()

print("🟢 Receptor combinado listo...")

while True:
    if nrf.any():
        msg = nrf.recv()
        if len(msg) == 3:
            angulo = struct.unpack("B", msg[0:1])[0]
            pwm_recv = struct.unpack("H", msg[1:3])[0]

            servo_Angle(angulo)
            esc.duty_u16(pwm_recv)

            led.value(1)
            utime.sleep_ms(50)
            led.value(0)

            print(f"📩 Ángulo: {angulo}° | PWM ESC: {pwm_recv}")

    utime.sleep(0.02)