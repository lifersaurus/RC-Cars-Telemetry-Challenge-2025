from machine import Pin, ADC, SPI
from nrf24l01 import NRF24L01, POWER_3, SPEED_250K
import utime, struct

xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))

button_accel  = Pin(4, Pin.IN, Pin.PULL_UP)
button_reverse = Pin(6, Pin.IN, Pin.PULL_UP)

spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
csn = Pin(13, Pin.OUT)
ce  = Pin(14, Pin.OUT)

emergency_btn = Pin(16, Pin.IN, Pin.PULL_UP)

nrf = NRF24L01(spi, csn, ce, channel=100, payload_size=3)
nrf.set_power_speed(POWER_3, SPEED_250K)
nrf.set_crc(2)
nrf.reg_write(0x04, (10 << 4) | 5)
nrf.open_tx_pipe(b'\xe1\xf0\xf0\xf0\xf0')
nrf.open_rx_pipe(1, b'\xd2\xf0\xf0\xf0\xf0')

PULSE_ACCEL   = 1000
PULSE_NEUTRAL = 1500
PULSE_REVERSE = 2000
led = Pin("LED", Pin.OUT)
led.value(1)
period_us = 1_000_000 // 30
while True:

    # Emergencia
    if emergency_btn.value() == 0:
        angulo = 90
        pwm_real = PULSE_NEUTRAL
        paquete = struct.pack("<BH", angulo, pwm_real)
        try:
            nrf.send(paquete)
        except:
            pass
        utime.sleep_ms(20)
        continue

    joy_x = xAxis.read_u16()
    joy_y = yAxis.read_u16()

    # Botones
    if button_accel.value() == 0:
        duty_f = PULSE_ACCEL / period_us
        duty_u16 = int(duty_f * 65535)
       
    elif button_reverse.value() == 0:
        duty_f = PULSE_REVERSE / period_us
        duty_u16 = int(duty_f * 65535)
    
    else:
        duty_f = PULSE_NEUTRAL / period_us
        duty_u16 = int(duty_f * 65535)
       

    # Joystick solo controla dirección
    if joy_y > 40000:
        angulo = 0
    elif joy_y < 30000:
        angulo = 180
    else:
        angulo = 90

    paquete = struct.pack("<BH", angulo, duty_u16)

    try:
        nrf.send(paquete)
        print(f"E {angulo} {pwm_real}")
    except:
        print("F")

    utime.sleep_ms(20)   # 50 Hz = rápido y estable