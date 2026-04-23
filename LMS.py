import serial # permite la comunicación con el puerto serial
import numpy as np #Librería para manejo de arrays y operaciones matemáticas
import matplotlib.pyplot as plt #Librería para graficar los datos
import time #Librería para manejar el tiempo

# 1. Configuración del Puerto Serial
puerto_serial = serial.Serial('COM10', 9600, timeout=1) #timeout=1 para evitar bloqueos si no hay datos disponibles.
time.sleep(2) # Esperar un momento para que el puerto serial se estabilice al inicio.

# 2. Variables de control
duracion_segundos = 30  # Duración total de la captura en segundos
mu = 0.03  # Ahora 0.03 es seguro porque normalizaremos la entrada
w = 0.0     # Peso inicial del filtro LMS, se puede iniciar en 0 o con un valor pequeño
datos_originales = []# Lista para almacenar los valores originales del potenciómetro (0-1023) para graficar posteriormente.
datos_filtrados = []# Lista para almacenar los valores filtrados por el algoritmo LMS, que se escalarán de vuelta a 0-1023 para la gráfica.
tiempos = []# Lista para almacenar los tiempos de cada lectura, lo que permitirá graficar la evolución de la señal a lo largo del tiempo.

print(f"Iniciando captura por {duracion_segundos} segundos...")#Mensaje que indica que inicio la captura de datos
inicio_test = time.time()#Marca el tiempo de inicio de la captura para poder controlar la duración total del proceso.

try: #Bucle principal de captura y procesamiento de datos. Se ejecutará hasta que se alcance la duración especificada en duracion_segundos.
#Mientras el tiempo transcurrido desde el inicio de la captura sea menor que la duración especificada, se seguirá leyendo y procesando datos del puerto serial.
    while (time.time() - inicio_test) < duracion_segundos: 
        ##Lee una línea del puerto serial, la decodifica de bytes a string usando UTF-8, y elimina cualquier espacio en blanco o caracteres de nueva línea.
        linea = puerto_serial.readline().decode('utf-8').strip() 
        if linea:#Si la línea leída no está vacía, se procede a procesarla.
            try:
                # --- NORMALIZACIÓN ---
                # Convertimos 0-1023 a un rango de 0.0 a 1.0
                valor_crudo = float(linea) #Convierte la cadena leída del puerto serial a un número de punto flotante. 
                x_n = valor_crudo / 1023.0 #Normaliza el valor del potenciómetro dividiéndolo por 1023.0
                #inclusive en las primeras versiones del codigo el valor del potenciometro subia hasta el infinito
                # --- Algoritmo LMS ---
                y_n = w * x_n          # Salida estimada
                e_n = x_n - y_n        # Error
                w = w + mu * e_n * x_n # Actualización del peso
                
                # --- GUARDAR DATOS (Volvemos a escalar a 1023 para la gráfica) ---
                datos_originales.append(valor_crudo)# almacena el valor original del potenciometro sin normalizar
                datos_filtrados.append(y_n * 1023.0)# almacena el valor filtrado por el algoritmo LMS
                tiempos.append(time.time() - inicio_test)# Almacena el tiempo transcurrido desde el inicio de la captura
                
            except ValueError: #si el Arduino envía un mensaje de error o datos corruptos, se captura la excepción ValueError y se ignora esa línea
                continue#Si ocurre un error al convertir la línea a un número, se ignora esa línea y se continúa con la siguiente iteración del bucle

finally: #Cerrar el puerto serial al finalizar la captura, ya sea por alcanzar la duración especificada o por una interrupción.
    puerto_serial.close()#Cierra el puerto
    print("Captura finalizada y puerto cerrado.") #mensaje indicando al usuario que la captura termino

# 4. Graficación
plt.figure(figsize=(12, 6)) #crea una figura tamaño 12x6
# Señal original en Cyan y Filtrada en Azul como se pidio como requisito
plt.plot(tiempos, datos_originales, color="cyan", label="Señal Original (Potenciómetro)")#grafica la señal original 
plt.plot(tiempos, datos_filtrados, color="blue", label="Señal Filtrada (LMS)")#grafica la señal filtrada por el algoritmo LMS

plt.xlabel("Tiempo (s)")#etiqueta del eje X
plt.ylabel("Valor Potenciómetro (0-1023)")#etiqueta del eje
plt.title("Procesamiento de Señal en Tiempo Real: Arduino + LMS") #titulo de la gráfica
plt.legend()#Agrega una leyenda para identificar las líneas de la gráfica
plt.grid(True, linestyle='--', alpha=0.6)#agrega la cuadrilla

# Ajustar los límites del eje Y para que no se vea infinito si algo sale mal
plt.ylim(-50, 1100) 
# Mostrar la gráfica
plt.show()