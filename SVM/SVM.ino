const int buttonPin = A0; // Asigna el pin analogico A0 para que funcione como entrada digital del boton
int count = 0; // Crea un contador iniciando en cero para llevar el registro de las 10 muestras
int inputNumber = 0; // Crea una memoria temporal para guardar el numero que llega desde la PC

void setup() {
  Serial.begin(9600); // Enciende el puerto USB a una velocidad de 9600 bits por segundo
  
  // Configura el pin A0 para recibir corriente. Al ser Pull-Down, asume que le pusiste una resistencia a tierra (GND)
  pinMode(buttonPin, INPUT); 
  
  Serial.println("Sistema SVM Iniciado."); // Envia un mensaje inicial a la computadora
}

void loop() {
  if (count < 10) { // Revisa si el contador aun es menor a 10. Si ya llego a 10, ignora todo este bloque
    
    Serial.println("Ingrese un numero entre 0 y 30"); // Pide el dato al usuario
    
    // El Arduino se queda congelado en esta linea dando vueltas hasta que detecte que llego informacion por el cable
    while (Serial.available() == 0) {} 
    
    // Lee el texto que llego por el USB y lo convierte matematicamente en un numero entero
    inputNumber = Serial.parseInt();
    
    // Limpieza de memoria temporal: borra la "basura" invisible (como el 'Enter' o saltos de linea) que quedo flotando
    while(Serial.available() > 0) { Serial.read(); }

    if (inputNumber >= 0 && inputNumber <= 30) { // Filtro de seguridad: verifica que el numero este en el rango correcto
      Serial.print("Ingreso el numero: "); // Avisa que numero entendio el Arduino
      Serial.print(inputNumber);
      Serial.println(". Presione boton para confirmar");

      // 1. Congela el Arduino aqui mientras el pin lea LOW (0 voltios). Es decir, espera a que PRESIONES el boton.
      while (digitalRead(buttonPin) == LOW) {}
      
      // 2. Pausa el microprocesador 200 milisegundos para ignorar las vibraciones fisicas del resorte del boton.
      delay(200); 
      
      // 3. Congela el Arduino aqui mientras el pin lea HIGH (5 voltios). Es decir, espera a que SUELTES el boton.
      while (digitalRead(buttonPin) == HIGH) {} 

      // 4. Envia por el cable la palabra clave exacta para que el script de Python en la PC la intercepte
      Serial.print("DATO:");
      Serial.println(inputNumber); // Envia el numero que validamos
      
      count++; // Le suma 1 al contador de muestras. (ej: pasa de 0 a 1)
      
    } else {
      // Si el numero no estaba entre 0 y 30, arroja este error y el bucle vuelve a empezar sin sumar nada al contador
      Serial.println("Error: Fuera de rango.");
    }
  }
}