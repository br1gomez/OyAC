# Repositorio para guardar proyectos y las practicas de OyAC grupo 01

## Programa FILT_IIR.py
Se implementa un filtro digital IIR o de Respuesta de Impulso Infinito.  
Es un tipo de filtro digital el cual utiliza retroalimentación para calcular su salida, incorporando valores de entrada y salida anteriores, es decir, que la señal de salida depende de todos los valores de entrada previos y de las salidas anteriores.  

Aplicaciones: 
- Procesamiento de audio y ecualizacion.
- Procesamiento de señales de sensores biómedicos.
- Sensores inteligentes en IoT (internet de las cosas).  

Tipos: 
- **Butterworth**. Respuesta de amplitud plana en la banda de paso y de rechazo, pero con una zona de transición amplia. 
- **Chebyshev**. Ofrece una transmisión más estrecha que el Butterworth, a costa de rizado en la banda de paso o rechazo.
- **Cauer**. La zona de transición más estrecha posible, pero con rizado en ambas bandas.
- **Bessel**. Diseñado para una respuesta de retardo de grupo lo más plana posible, aunque tiene una zona de transición muy amplia. 

### Uso 

El programa utiliza un núcleo para generar una señal y el otro para filtrarla.  
- Primero conectar la raspberry pi pico a la computadora, posteriormente abrir Thonny o el editor de MicroPython deseado (investigar y realizar las configuraciones para cada interprete en caso de no usar Thonny) y asegurarse de que este configurado el interprete de MicroPython de la rasp.  
- El programa genera una onda cuadrada de prueba en el **Pin 3** (GP3) y espera a leer esa misma señal en el **Pin 26** (GP26, el ADC0), estos pines se deben de conectar fisicamente con un cable.
- La función _thread.start_new_thread(Onda_Cuadrada,()) usa el núcleo 1 para generar una señal de prueba mientras el bucle while true en el núcleo 0 usa el ADC0.read_u16() para leer una señal de entrada y al hacer un puente entre ambos pines se alimenta el filtro con la señal de prueba que el mismo genera.

### Salida
Al final el programa muestra dos columnas: 
- Primera columna UKs[0]: Entrada antes del filtro que alterna entre 1 y 0, es la onda cuadrada.
- Segunda columna YKs[0]: Salida después del filtro, los valores cambian de forma mas suave, esto debido a que es un filtro paso-bajas que suavisa los bordes de una onda cuadrada.