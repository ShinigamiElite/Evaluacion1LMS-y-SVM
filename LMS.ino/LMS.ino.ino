// Definimos el pin ANALOG IN del potenciómetro
const int potPin = A0;
//el codigo que se generara para hacer la conexion.
void setup() {
  // El Arduino Leonardo usa Serial.begin() pero la comunicación USB es nativa
  // 9600 es la velocidad estándar que configuramos en Python
  Serial.begin(9600);
  
  // Esperar a que el puerto serial esté listo (específico para Leonardo)
  while (!Serial) {
    ; 
  }
}
//Crea un ciclo que se repetiravbnnbj
void loop() {
  // 1. Leer el valor del potenciómetro (0 a 1023)
  int valorPot = analogRead(potPin);

  // 2. Enviar el valor por el puerto serial
  // Usamos println para que cada dato vaya en una línea nueva
  Serial.println(valorPot);

  // 3. Pequeña pausa para no saturar el buffer
  // Esto nos da aproximadamente 100 lecturas por segundo
  delay(10); 
}