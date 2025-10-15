# ---------------------------------------------------------------------------
# CALCULADORA FPU CON MICROPYTHON Y ENSAMBLADOR EN RASPBERRY PI PICO 2
# ---------------------------------------------------------------------------
# Este programa integra cinco rutinas de ensamblador para realizar
# operaciones aritméticas de punto flotante utilizando la FPU del
# microcontrolador.
# ---------------------------------------------------------------------------

import micropython
from array import array

# ---------------------------------------------------------------------------
# Definición de las Subrutinas en Ensamblador (Thumb)
# Cada función corresponde a uno de los archivos .py proporcionados.
# ---------------------------------------------------------------------------

@micropython.asm_thumb
def asm_sum(r0, r1, r2):
    """
    Suma dos números de punto flotante.
    r0: Puntero al array del primer operando.
    r1: Puntero al array del segundo operando.
    r2: Puntero al array de salida.
    """
    vldr(s0, [r0, 0])  # Carga el primer número en el registro FPU s0
    vldr(s1, [r1, 0])  # Carga el segundo número en el registro FPU s1
    vadd(s3, s0, s1)   # Realiza la suma: s3 = s0 + s1
    vstr(s3, [r2, 0])  # Almacena el resultado de s3 en la dirección de salida

@micropython.asm_thumb
def asm_sub(r0, r1, r2):
    """Resta dos números de punto flotante."""
    vldr(s0, [r0, 0])
    vldr(s1, [r1, 0])
    vsub(s3, s0, s1)   # Realiza la resta: s3 = s0 - s1
    vstr(s3, [r2, 0])

@micropython.asm_thumb
def asm_mul(r0, r1, r2):
    """Multiplica dos números de punto flotante."""
    vldr(s0, [r0, 0])
    vldr(s1, [r1, 0])
    vmul(s3, s0, s1)   # Realiza la multiplicación: s3 = s0 * s1
    vstr(s3, [r2, 0])

@micropython.asm_thumb
def asm_div(r0, r1, r2):
    """Divide dos números de punto flotante."""
    vldr(s0, [r0, 0])
    vldr(s1, [r1, 0])
    vdiv(s3, s0, s1)   # Realiza la división: s3 = s0 / s1
    vstr(s3, [r2, 0])

@micropython.asm_thumb
def asm_sqrt(r0, r1):
    """Calcula la raíz cuadrada de un número de punto flotante."""
    vldr(s0, [r0, 0])
    vsqrt(s1, s0)      # Realiza la raíz cuadrada: s1 = sqrt(s0)
    vstr(s1, [r1, 0])

# ---------------------------------------------------------------------------
# Función Principal de la Calculadora
# ---------------------------------------------------------------------------

def calculator():
    """MENU DE OPERACIONES."""
    print("############################################################")
    print("### Calculadora FPU con Ensamblador en Raspberry Pi Pico ###")
    print("############################################################")

    while True:
        # Mostrar el menú de opciones
        print("\nSeleccione una operación:")
        print("  1. Suma")
        print("  2. Resta")
        print("  3. Multiplicación")
        print("  4. División")
        print("  5. Raíz Cuadrada")
        print("  6. Salir")

        choice = input("Opción -> ")

        # Preparar arrays para las operaciones
        output = array('f', [0.0])

        try:
            if choice in ('1', '2', '3', '4'):
                num1_str = input("  Ingrese el primer número: ")
                num2_str = input("  Ingrese el segundo número: ")
                num1 = float(num1_str)
                num2 = float(num2_str)
                input1 = array('f', [num1])
                input2 = array('f', [num2])

                if choice == '1':
                    asm_sum(input1, input2, output)
                    print(f"\n>> Resultado: {num1} + {num2} = {output[0]}")
                elif choice == '2':
                    asm_sub(input1, input2, output)
                    print(f"\n>> Resultado: {num1} - {num2} = {output[0]}")
                elif choice == '3':
                    asm_mul(input1, input2, output)
                    print(f"\n>> Resultado: {num1} * {num2} = {output[0]}")
                elif choice == '4':
                    if num2 == 0.0:
                        print("\n!! Error: No se puede dividir por cero.")
                        continue
                    asm_div(input1, input2, output)
                    print(f"\n>> Resultado: {num1} / {num2} = {output[0]}")

            elif choice == '5':
                num_str = input("  Ingrese el número: ")
                num = float(num_str)
                if num < 0:
                    print("\n!! Error: No se puede calcular la raíz cuadrada de un número negativo.")
                    continue
                input1 = array('f', [num])
                asm_sqrt(input1, output)
                print(f"\n>> Resultado: sqrt({num}) = {output[0]}")

            elif choice == '6':
                print("\nSaliendo de la calculadora. ¡Hasta luego!")
                break
            
            else:
                print("\n!! Opción no válida. Por favor, elija un número del 1 al 6.")

        except ValueError:
            print("\n!! Error: Entrada inválida. Por favor, ingrese solo números.")
        except Exception as e:
            print(f"\n!! Ocurrió un error inesperado: {e}")

# Ejecutar la calculadora
if __name__ == "__main__":
    calculator()