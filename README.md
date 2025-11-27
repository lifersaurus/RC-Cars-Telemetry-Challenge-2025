# Telemetry-Challenge-2025

VIDEO YOUTUBE: https://youtu.be/mQSniKknSO8

Este proyecto consistió en el diseño y construcción de un **sistema de telemetría inalámbrica para un carro RC**, desarrollado como parte del RC Cars Telemetry Challenge 2025. Se utilizó una **Raspberry Pi Pico 2W** como microcontrolador principal y un **módulo nRF24L01** para la transmisión de datos a una estación base en PC, permitiendo la visualización en tiempo real de múltiples parámetros del vehículo.

## Resumen del Proyecto

El objetivo principal fue integrar sensores, control del vehículo, electrónica propia y transmisión de datos en un solo sistema funcional. Para ello, se abordaron varias etapas:

### 1. Diseño y modificación mecánica del vehículo
- Se seleccionó un carro RC como plataforma base y se reemplazó el motor original por un motor DC de 12 V, más potente, lo que requirió ajustes en la transmisión y la estructura del chasis.
- Se realizaron pruebas de laboratorio para determinar los parámetros óptimos de PWM y asegurar estabilidad en aceleración y frenado.
- Los soportes iniciales de PVC se moldearon mediante corte, calentamiento y aplanamiento repetido hasta obtener placas planas y resistentes. Sin embargo, no ofrecían la rigidez suficiente para soportar el nuevo motor.
- Se fabricó un **soporte en madera de balsa**, cortando palos y pegándolos para formar un bloque sólido. Este soporte se moldeó con bisturí y mototool, ajustando un hueco preciso para encajar el motor, y se realizaron ajustes en los piñones para adaptarlos a la nueva potencia, pasando de tres a dos piñones.

### 2. Sistema de dirección
- Se instaló un **servomotor** para controlar la dirección del vehículo, acoplado al eje delantero mediante un alambre rígido.
- Se realizaron pruebas de PWM para verificar el giro del servomotor y asegurar su respuesta correcta.

### 3. Diseño electrónico del vehículo
- Se implementó un sistema de alimentación dual: una batería de 7.4 V – 1200 mAh para el motor y otra de 9 V regulada a 5 V para la Raspberry Pi Pico 2W, sensores y nRF24L01.
- Se tomaron medidas del chasis y se diseñó el **esquemático de conexiones** entre el microcontrolador, el ESC, el servomotor y los sensores.
- El ESC se probó primero de forma independiente y luego conectado al GPIO correspondiente de la Raspberry Pi Pico 2W. Se verificó la señal PWM usando un osciloscopio, observando un período de 880 ms durante la aceleración y un rango de voltaje de aproximadamente –2.53 V a 6.92 V al invertir el sentido del motor.

### 4. Control remoto
- Inicialmente se empleaban dos joysticks; luego se simplificó a un solo joystick y dos botones: uno para acelerar y otro para reversa.
- Se diseñó un **PCB en EasyEDA** para organizar los componentes del control. La primera impresión presentó fallos, por lo que se optó por implementar el control en una baquelita, garantizando un funcionamiento estable y seguro.
- El joystick controla el ángulo del servomotor mediante el eje Y: valores menores a 30 000 mueven la dirección a la izquierda, mayores a 40 000 a la derecha, y entre esos valores permanece en neutro (90°). Los botones controlan aceleración y reversa.

### 5. Integración de sensores y sistema de telemetría
- Los sensores implementados en el sistema fueron:
  - **GPS GY-NEO6M2**: posición, velocidad y tiempo.
  - **MPU6050**: aceleración y giroscopio.
  - **TCRT5000**: detección de meta.
  - **Sensor de temperatura**: monitoreo del motor.
- La Raspberry Pi Pico 2W adquiría, procesaba y empaquetaba los datos para enviarlos vía nRF24L01 a la estación base.
- Se elaboró un **esquema electrónico** y se diseñó la PCB correspondiente en EasyEDA para integrar todos los sensores, el microcontrolador y el módulo de radio.
- Se realizaron pruebas individuales de cada sensor, verificando comunicación correcta, estabilidad de lecturas y consistencia de los datos transmitidos.

### 6. Pruebas y validación
- Se verificó que todos los sistemas funcionaran correctamente en conjunto: ESC, servomotor, sensores y módulo de radio.
- Se ajustaron conexiones, se corrigieron errores y se fijó el sistema completo dentro del chasis del vehículo.
- Se documentó la telemetría en tiempo real: coordenadas GPS, aceleraciones, temperatura y detección de meta, asegurando que el sistema podía operar bajo condiciones de carrera y entregar datos precisos para análisis de desempeño.

## Resultados
- Sistema de telemetría completamente funcional en tiempo real.
- Integración mecánica, electrónica y de control optimizada para la potencia del motor y las dimensiones del vehículo.
- Control remoto simplificado y protegido, con joystick y botones operativos.
- Sensores calibrados y verificados, proporcionando datos consistentes de posición, velocidad, orientación y temperatura.
- Documentación completa: esquemáticos, planos, diagramas y video demostrativo.
