# Implementación de un filtro IIR simple en Python
#Simulador de funciones de transaferencia discreta de 1er orden 
#En una raspberry pi pico usando la insfraestructura de lenguaje ensamblador
# y la unidad de punto flotante FPU en tiempo real

#Se genera una onda cuadrada en el pin3
#Se debe de conectar el pin 26 (Canal An0 del A/D) y el pin 3 para que el filtro tenga señal de entrada

from array import array
from time import sleep, sleep_ms
from machine import ADC, Pin
import _thread

# Cofiguraciones de pines
ADC0 = ADC(Pin(26))  # Pin 26 como entrada analógica
Pin25 = Pin(25, Pin.OUT)  # Pin 25 como salida digital
Pin3 = Pin(3, Pin.OUT)    # Pin 3 de acción paralela (onda cuadrada)

FACTOR = 1.0 / (65535)  # Constante para conversión a volts reales para el convertidor A/D

# Valores iniciales de las entradas y salidas del filtro

UK = 0.0    # U(k)
UK1 = 0.0   # U(k-1)
UK2 = 0.0   # U(k-2)
YK1 = 0.0   # Y(k-1)
YK2 = 0.0   # Y(k-2)
YK = 0.0    # Y(k)

# Coeficientes de la función de transferencia discreta

####                        A0*Z^2 + A1*Z + A2                  ####
####               H(z) = ----------------------                ####
####                        B0*Z^2 + B1*Z + B2                  ####

# Al obtener la ecuación en diferencias los coeficientes B1 y B2 cambian de signo

# B1*Y(k) = A0*U(k) + A1*U(k-1) - B1*Y(k-1) - B2*Y(k-2)

#En la H(z) normalizada se tiene que B0 = 1 por lo que se tiene: 
#Y(k) = A0*U(k) + A1*U(k-1) - B1*Y(k-1) - B2*Y(k-2)

#Para un sistema de primer orden con una tao de 0.5s y con la función de transferencia continua se tiene: 
####                    (1/Tao)          2                      ####
####          H(s) = -------------- = -------                   ####
####                  S + (1/Tao)      S + 2                    ####

#Aplicando la transformación de Tustin y la herramienta de MATLAB y un tiempo de muestreo Ts = 0.025 se obtienen los siguientes coeficientes:
#Sys = tf([0 2], [1 2]);
#Sysd = c2d(Sys, Ts, 'tustin');

#Lo que da la siguiente función de transferencia:
####                  A0*Z + A1      0.02439Z + 0.02439         ####
####          H(z) = ------------ = --------------------        ####
####                  B0*Z + B1        Z  -  0.9512             ####

#La ecuación en diferencias queda como:
#Y(z) = 0.02439Vi(k) + 0.02439Vi(k-1) + 0.9512Y(k-1)
#Dado que es de primer orden no se usan los coeficientes A2 y B2

A0 = 0.02439
A1 = 0.02439
B1 = 0.9512
B2 = 0.0
A2 = 0.0

#Creación de los vectores de datos que estan basasdos en
# las entradas - salidas y los coeficientes del filtro

Cte_UKs = array('f', (A0, A1, A2))
Cte_YKs = array('f', (B1, B2))
UKs = array('f', (UK, UK1, UK2))
YKs = array('f', (YK, YK1, YK2))

#Instrucciones en ensamblador para el calculo de la sumatoria del filtro IIR
#r0 = vector de coeficientes An
#r1 = vector de entradas Uks
#r2 = vector de coeficientes Bn
#r3 = vector de salidas Yks

@micropython.asm_thumb #Se utiliza el conjunto de instrucciones Thumb
def filtro(r0, r1, r2, r3):
    vldr  (s0,  [r0, 0])    # Adquiere A0
    vldr  (s1,  [r0, 4])    # Adquiere A1
    vldr  (s2,  [r0, 8])    # Adquiere A2
    vldr  (s3,  [r2, 0])    # Adquiere B1
    vldr  (s4,  [r2, 4])    # Adquiere B2
    
    vldr  (s5,  [r1, 0])    # Adquiere U(k)
    vldr  (s6,  [r1, 4])    # Adquiere U(k-1)
    vldr  (s7,  [r1, 8])    # Adquiere U(k-2)
    vldr  (s8,  [r3, 4])    # Adquiere Y(k-1)
    vldr  (s9,  [r3, 8])    # Adquiere Y(k-2)
    
    vmul  (s0, s0, s5)      # S0 = A0*U(k)
    vmul  (s1, s1, s6)      # S1 = A1*U(k-1)
    vmul  (s2, s2, s7)      # S2 = A2*U(k-2)
    vmul  (s3, s3, s8)      # S3 = B1*Y(k-1)
    vmul  (s4, s4, s9)      # S4 = B2*Y(k-2)
    
    vadd  (s0, s0, s1)      # S0 = A0*U(k)+A1*U(k-1)
    vadd  (s0, s0, s2)      # S0 = A0*U(k)+A1*U(k-1)+A2*U(k-2)
    vadd  (s0, s0, s3)      # S0 = A0*U(k)+A1*U(k-1)+A2*U(k-2)+B1*Y(k-1)
    vadd  (s0, s0, s4)      # S0 = A0*U(k)+A1*U(k-1)+A2*U(k-2)+B1*Y(k-1)+B2*Y(k-2)
    vstr  (s0, [r3, 0])     # Coloca  Y(k) = S0

# Actualización de las variables del filtro
    vstr  (s6, [r1, 8])     # U(k-1) --˃ U(k-2)
    vstr  (s5, [r1, 4])     # U(k)   --˃ U(k-1)


    vstr  (s8, [r3, 8])    # Y(k-1) --˃ Y(k-2)   
    vstr  (s0, [r3, 4])    # Y(k)   --˃ Y(k-1)

#Definición de la función para el nucleo 2 para la generación de la onda cuadrada
#Con un periodo en la variable HALF que corresponde al semiperiodo dado en segundos.

ONDA = 0.0625  # Frecuencia de la onda cuadrada en Hertz
Ts = 1/(ONDA) #Periodo de la onda cuadrada
HALF = Ts / 2  # Semiperiodo en segundos

def onda_cuadrada():
    while True:
        Pin25.on()  #Pin testigo de la raspberry en ON.
        Pin3.on()   # Pin 3 en alto
        sleep(HALF) # Espera el semiperiodo
        Pin25.off() #Pin testigo de la raspberry en OFF.
        Pin3.off()  # Pin 3 en bajo
        sleep(HALF) # Espera el semiperiodo

# Programa principal que hace calculos del filtro IIR
_thread.start_new_thread(onda_cuadrada, ())  # Inicia el nucleo 2 para la onda cuadrada

#loop principal del filtro 
while True:
    filtro(Cte_UKs, UKs, Cte_YKs, YKs)  # Llama a la función en ensamblador del filtro IIR
    print(UKs[0], YKs[0])  # Imprime la entrada y salida del filtro
    sleep_ms(25)  # Tiempo de muestreo de 25 ms
    UKs[0] = ADC0.read_u16() * FACTOR  # Lee la señal de entrada del A/D y la convierte a volts reales
