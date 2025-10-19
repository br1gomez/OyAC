# Implementación de un filtro IIR de Primer orden Pasa Altos (HPF)
#Utilizando una raspberry pi pico y usado la FPU en ensamblador

from machine import Pin, ADC
from array import array
from time import sleep, sleep_ms 
import _thread

# Configuración del Pin26 como entrada analógica ADC0
ADC0 = ADC(Pin(26))
ADC_V = 3.3 / 65535  # Factor de conversión a voltaje real

Pin25 = Pin(25, Pin.OUT)  # Pin25 como salida digital
pin_OUT = Pin(3, Pin.OUT)    # Pin3 para generar onda cuadrada

# Variables iniciales del filtro
##  U(k)   = UKs[0]                                 
##  U(k-1) = UKs[1]                                 
##                                                 
##  Y(k)   = YKs[0]                                 
##  Y(k-1) = YKs[1]                                 
##                                                 
##  b0 = Cte_UKs[0]                                 
##  b1 = Cte_UKs[1]                                 
##                                                 
##  a0 = Cte_YKs[0]                                 
##  a1 = Cte_YKs[1] 

UKs = array('f', [0.0, 0.0])  # U(k), U(k-1)
YKs = array('f', [0.0, 0.0])  # Y(k), Y(k-1)

#Función de transferencia

# H(z) = (1.0 - 1.0 * z^-1) / (1.0 - 0.8 * z^-1)
#Para el filtro Pasa Altos (HPF) de primer orden

#b0 = 1.0, b1 = -1.0
#a0 = 1.0, a1 = -0.8

Cte_UKs = array('f', [1.0, -1.0])  # Coeficientes b0, b1
Cte_YKs = array('f', [1.0, -0.8])  # Coeficientes a0, a1

#Rutina que genera un onda cuadrada en el pin3 de 0 a 3.3 volts
#con un periodo de 2 segundos (0.5 Hz) que corre en el nucleo 1

def Onda_Cuadrada():
    while True: 
        Pin25.on()
        pin_OUT.value(1)
        sleep(1)
        Pin25.off()
        pin_OUT.value(0)
        sleep(1)

#Inicia la rutina de la onda cuadrada en el nucleo 1
#      Y(k) = b0*U(k) + b1*U(k-1) - a1*Y(k-1)

@micropython.asm_thumb
def filtro(r0, r1, r2, r3):
# r0 -> Cte_UKs (b0, b1)
    # r1 -> UKs (U(k), U(k-1))
    # r2 -> Cte_YKs (a0, a1)
    # r3 -> YKs (Y(k), Y(k-1))
    
    # Inicia el cálculo de la sumatoria de productos:
    # S4 = b0 * U(k)
    vldr(s0, [r0, 0])
    vldr(s1, [r1, 0])
    vmul(s4, s0, s1)
    
    # S4 = S4 + b1 * U(k-1)
    vldr(s0, [r0, 4])
    vldr(s1, [r1, 4])
    vmul(s5, s0, s1)  # s5 = b1 * U(k-1) usando un registro temporal s5
    vadd(s4, s4, s5)  # s4 = s4 + s5
    
    # S4 = S4 - a1 * Y(k-1)
    vldr(s0, [r2, 4])
    vldr(s1, [r3, 4])
    vmul(s5, s0, s1)  #s5 = a1 * Y(k-1) (reutilizamos s5)
    vsub(s4, s4, s5)  #s4 = s4 - s5
    
    # Almacena el resultado final en Y(k)
    # YKs[0] = S4
    vstr(s4, [r3, 0])
    
    # Actualiuzación de variables
    # U(k-1) = U(k)
    vldr(s0, [r1, 0])
    vstr(s0, [r1, 4])
    
    # Y(k-1) = Y(k)
    vldr(s0, [r3, 0])
    vstr(s0, [r3, 4])

#Programa principal que corre en el nucleo 0
_thread.start_new_thread(Onda_Cuadrada, ())  # Inicia el nucleo 1 para la onda cuadrada

#Loop principal del filtro
while True:
    filtro(Cte_UKs, UKs, Cte_YKs, YKs)  # Llama a la función en ensamblador del filtro IIR  
    # Lee la entrada analógica y la convierte a voltaje
    print(UKs[0], YKs[0])  # Imprime la entrada y salida del filtro

    #Tiempo de muestreo 
    sleep_ms(25)

    #Lee al convertidor A/D y asigna la nueva entrada U(k)
    UKs[0] = ADC0.read_u16() * ADC_V  # Lee la señal de entrada del A/D y la convierte a volts reales