import serial #sirve para comunicarse con el puerto serial mediante los pines de transmision (TX/RX)
import time #con esta libreria puedo tengo acceso al reloj interno de la CPU
import numpy as np #esta bliblioeca sirve para procesar arreglos matriciales 
import matplotlib.pyplot as plt #gracias a esta libreria podemos graficar y visualizar los resultados 
from sklearn import svm #carga los modelos matematicos de machine learning

PUERTO = 'COM3' #define el puerto en el que esta el arduino
BAUD_RATE = 9600 #define la velocidad del reloj

datos_capturados = [] #define un arreglo vacio para guardar las mustras

try:
    ser = serial.Serial(PUERTO, BAUD_RATE, timeout=1) #con este comando pedimos control del puerto 
    time.sleep(2) # Esperar a que el Arduino se reinicie tras la conexion
    print("--- Sistema de Captura SVM ---")

    while len(datos_capturados) < 10: #se repite 10 veces
        # 1. Ingreso de datos en el PC
        numero = input(f"\n[{len(datos_capturados)+1}/10] Ingrese numero (0-30): ") 
        
        if not numero.isdigit() or not (0 <= int(numero) <= 30): #aqui se flitran letras o numeros fuera del rango
            print("Error: Ingrese un numero valido entre 0 y 30.")#si el numero no es valido, se muestra un mensaje de error
            continue#si el numero es valido, se convierte a entero para su posterior uso

        # 2. Enviar el numero al Arduino
        ser.write(f"{numero}\n".encode('utf-8')) #traduce los caracteres del numero a valores binarios
        print("Enviado. Ahora presione el BOToN FiSICO en el Arduino para confirmar...")

        # 3. Esperar la confirmacion del Arduino (DATO:XX)
        confirmado = False
        while not confirmado:
            #lee el registro para saber si el arduino envio informacion de vuelta
            if ser.in_waiting > 0: 
                #lee y decodifica la informacio que viene a texto y elimina los espacios o saltos de linea en los extremos
                linea = ser.readline().decode('utf-8').strip() 
                #es basicamente un filtro que solo prosesa la infomracion si resive el codigo de confirmacion
                if linea.startswith("DATO:"): 
                    valor = int(linea.split(":")[1]) #corta el texto por la mitad usando los dos puntos como tijera
                    datos_capturados.append(valor)#guarda el valor confirmado por el arduino en el arreglo de datos capturados
                    print(f"Confirmado! El Arduino registro: {valor}")
                    confirmado = True#sale del bucle de espera para el siguiente numero
                else:
                    # Imprime mensajes informativos del Arduino (como "Presione boton...")
                    print(f" [Arduino]: {linea}")#si el arduino envia otro mensaje que no es el de confirmacion, se imprime en la consola para que el usuario sepa que esta pasando

    ser.close()
# Si ocurre cualquier error durante la comunicacion o el proceso
except Exception as e:
    print(f"Error critico: {e}")#si algo sale mal, se imprime el error en la consola para que el usuario sepa que paso y se cierra el puerto si es necesario
    exit()# Si todo sale bien, se cierra el puerto al finalizar la captura de datos

# --- PROCESAMIENTO Y GRaFICA ---
X = np.array(datos_capturados).reshape(-1, 1) #obliga al arreglo a transformarse en una columna vertical con 10 filas
y = np.where(X <= 14, 0, 1).ravel() #esta parte clasifica si el valor pertenece al grupo uno o al grupo dos

# Entrenamiento del modelo
modelo = svm.SVC(kernel='linear') #esto le dice al modelo que trace una linea recta sin hacer curvas
modelo.fit(X, y) #aqui se inyecta la matriz X y el vector y para calcular la separacion optima de los valores ingresados

# Calculo de la frontera 
peso = modelo.coef_[0][0]
#el sesgo es el valor que se suma a la multiplicacion del peso por la entrada para determinar la clase a la que pertenece un nuevo dato
sesgo = modelo.intercept_[0]
#esta formula sale del despeje de la formula w*x+b=0 queando asi x=-b/w 
frontera = -sesgo / peso 

# Generacion de la grafica
plt.figure(figsize=(10, 5)) #crea un lienzo en blanco para dibujar de 10x5
#filtra solo los datos del grupo 1 los aplasta contra el piso Y=0 y los dibuja como circulos de color cyan
plt.scatter(X[y==0], np.zeros_like(X[y==0]), color='cyan', edgecolors='black', s=150, label='Clase 1 (Bajo)') 
#filtra solo los datos del grupo 2 los aplasta contra el piso Y=0 y los dibuja como circulos de color azul
plt.scatter(X[y==1], np.zeros_like(X[y==1]), color='blue', edgecolors='black', s=150, label='Clase 2 (Alto)') 
#dibuja una linea recta vertical de color rojo justo en el numero que calculo la frontera
plt.axvline(x=frontera, color='red', linestyle='--', linewidth=3, label=f'Frontera SVM: {frontera:.2f}') 
#configura los detalles de la grafica como el titulo, etiquetas, leyenda y cuadrilla
plt.title('Clasificacion SVM: Datos de Arduino Confirmados por Boton')
plt.xlabel('Valor de Entrada')#etiqueta del eje X
plt.yticks([])#elimina las marcas del eje Y para que se vea mas limpio
plt.grid(True, alpha=0.3)#agrega una cuadrilla con transparencia para facilitar la lectura de la grafica
plt.legend()#agrega una leyenda para identificar las clases y la frontera de decision
#imprime el resultado de la frontera de decision en la consola
print(f"\nProceso terminado. Frontera de decision calculada en: {frontera:.2f}")
plt.show()#muestra la grafica al usuario